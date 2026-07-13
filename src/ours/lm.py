# /home/jinwoo/gepa-official/src/ours/lm.py
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from gepa.proposer.reflective_mutation.base import (
    LanguageModel,
    Signature,
)

from ours.runtime import OursRuntime


Prompt = str | list[dict[str, Any]]


_SENSITIVE_CONFIG_KEYS = {
    "api_key",
    "authorization",
    "access_token",
    "auth_token",
    "bearer_token",
    "password",
    "secret",
    "token",
}


def _signature_name(signature_cls: type[Signature]) -> str:
    return (
        f"{signature_cls.__module__}."
        f"{signature_cls.__qualname__}"
    )


def _sanitize_lm_config(value: Any) -> Any:
    """
    Remove credentials before writing the LM configuration into cache files.

    Non-secret behavior-changing fields such as model, api_base,
    temperature, max_tokens, and seed are preserved.
    """
    if isinstance(value, Mapping):
        sanitized = {}

        for key, item in value.items():
            key_string = str(key)

            if key_string.lower() in _SENSITIVE_CONFIG_KEYS:
                continue

            sanitized[key_string] = _sanitize_lm_config(item)

        return sanitized

    if isinstance(value, list):
        return [
            _sanitize_lm_config(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            _sanitize_lm_config(item)
            for item in value
        ]

    return value


def _extract_text_parts(content: Any) -> str | None:
    """
    Extract text from an OpenAI-compatible message content value.

    This is used only for normalizing an LM response. Input prompts are passed
    to the underlying LM without modification.
    """
    if isinstance(content, str):
        return content

    if not isinstance(content, list):
        return None

    parts: list[str] = []

    for item in content:
        if isinstance(item, str):
            parts.append(item)
            continue

        if not isinstance(item, Mapping):
            continue

        if item.get("type") in {"text", "output_text"}:
            text = item.get("text")
            if text is not None:
                parts.append(str(text))

    if not parts:
        return None

    return "".join(parts)


def normalize_lm_output(output: Any) -> str:
    """
    Normalize common LM response shapes into the string expected by GEPA.

    GEPA's LanguageModel protocol requires:

        lm(prompt) -> str

    DSPy and OpenAI-compatible clients may instead return:
      - list[str]
      - {"text": "..."}
      - [{"text": "..."}]
      - {"choices": [{"message": {"content": "..."}}]}
      - response objects with text, output_text, content, or choices
    """
    if isinstance(output, str):
        return output

    if output is None:
        raise TypeError("The language model returned None.")

    if isinstance(output, (list, tuple)):
        if not output:
            raise ValueError(
                "The language model returned an empty output list."
            )

        # Match the behavior previously used with DSPy: select the first
        # generated completion.
        return normalize_lm_output(output[0])

    if isinstance(output, Mapping):
        for key in ("text", "output_text"):
            if key in output:
                return normalize_lm_output(output[key])

        if "content" in output:
            content_text = _extract_text_parts(output["content"])
            if content_text is not None:
                return content_text

            return normalize_lm_output(output["content"])

        if "message" in output:
            return normalize_lm_output(output["message"])

        if "choices" in output:
            choices = output["choices"]

            if not isinstance(choices, (list, tuple)) or not choices:
                raise ValueError(
                    "The language model returned an invalid `choices` field."
                )

            return normalize_lm_output(choices[0])

    for attribute in (
        "text",
        "output_text",
        "content",
        "message",
        "choices",
    ):
        if hasattr(output, attribute):
            value = getattr(output, attribute)

            if attribute == "content":
                content_text = _extract_text_parts(value)
                if content_text is not None:
                    return content_text

            return normalize_lm_output(value)

    # This matches the existing analysis adapter's final fallback behavior.
    return str(output)


class RuntimeLanguageModel:
    """
    GEPA-compatible LanguageModel wrapper backed by OursRuntime.

    The wrapper caches only the normalized raw LM completion. Prompt parsing
    remains owned by the Signature class and is executed on every call.
    """

    def __init__(
        self,
        *,
        runtime: OursRuntime,
        operation: str,
        lm: LanguageModel,
        signature_cls: type[Signature],
        input_dict: Mapping[str, Any],
        lm_config: Mapping[str, Any],
        metadata: Mapping[str, Any] | None = None,
    ):
        operation = operation.strip()
        if not operation:
            raise ValueError("LM operation name cannot be empty.")

        if not isinstance(input_dict, Mapping):
            raise TypeError("input_dict must be a mapping.")

        if not isinstance(lm_config, Mapping):
            raise TypeError("lm_config must be a mapping.")

        self.runtime = runtime
        self.operation = operation
        self.lm = lm
        self.signature_cls = signature_cls
        self.input_dict = dict(input_dict)
        self.lm_config = _sanitize_lm_config(dict(lm_config))
        self.metadata = dict(metadata or {})

        self.last_cache_hit: bool | None = None

    def _invoke_underlying_lm(
        self,
        prompt: Prompt,
    ) -> str:
        raw_output = self.lm(prompt)
        return normalize_lm_output(raw_output)

    def __call__(
        self,
        prompt: Prompt,
    ) -> str:
        signature_name = _signature_name(self.signature_cls)

        request = {
            "operation": self.operation,
            "signature": signature_name,
            "input_dict": self.input_dict,
            "rendered_prompt": prompt,
            "lm_config": self.lm_config,
        }

        call_metadata = {
            "call_type": "signature_lm",
            "operation": self.operation,
            "signature": signature_name,
            **self.metadata,
        }

        raw_output, cache_hit = self.runtime.call(
            operation=f"lm.{self.operation}",
            request=request,
            fn=lambda: self._invoke_underlying_lm(prompt),
            metadata=call_metadata,
            return_cache_hit=True,
        )

        self.last_cache_hit = cache_hit

        # Cached JSON responses are normally strings, but normalize again to
        # preserve the LanguageModel contract if a legacy cache entry has a
        # different shape.
        return normalize_lm_output(raw_output)


def run_signature(
    *,
    runtime: OursRuntime,
    operation: str,
    lm: LanguageModel,
    signature_cls: type[Signature],
    input_dict: Mapping[str, Any],
    lm_config: Mapping[str, Any],
    metadata: Mapping[str, Any] | None = None,
    return_cache_hit: bool = False,
):
    """
    Execute a GEPA Signature through the call-level runtime cache.

    The execution sequence remains GEPA-compatible:

        signature_cls.prompt_renderer(input_dict)
        -> cached_lm(rendered_prompt)
        -> normalized_output.strip()
        -> signature_cls.output_extractor(...)
        -> parsed_output, rendered_prompt, raw_lm_output

    The cached value is the normalized raw LM completion, not the parsed
    Signature output. Therefore, changing output_extractor() does not require
    another LM call.

    Returns:
        When return_cache_hit=False:
            parsed_output, rendered_prompt, raw_lm_output

        When return_cache_hit=True:
            parsed_output, rendered_prompt, raw_lm_output, cache_hit
    """
    cached_lm = RuntimeLanguageModel(
        runtime=runtime,
        operation=operation,
        lm=lm,
        signature_cls=signature_cls,
        input_dict=input_dict,
        lm_config=lm_config,
        metadata=metadata,
    )

    # Reproduce GEPA Signature.run_with_metadata() explicitly.
    #
    # This avoids depending on the imported GEPA version exposing the
    # convenience method while preserving the exact execution order:
    # render -> LM call -> strip -> extract.
    rendered_prompt = signature_cls.prompt_renderer(input_dict)
    lm_result = cached_lm(rendered_prompt)
    raw_lm_output = lm_result.strip()
    parsed_output = signature_cls.output_extractor(raw_lm_output)

    if cached_lm.last_cache_hit is None:
        raise RuntimeError(
            "Signature execution completed without invoking the language model."
        )

    if return_cache_hit:
        return (
            parsed_output,
            rendered_prompt,
            raw_lm_output,
            cached_lm.last_cache_hit,
        )

    return (
        parsed_output,
        rendered_prompt,
        raw_lm_output,
    )
