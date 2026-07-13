# /home/jinwoo/gepa-official/examples/ours/program.py
from functools import partial
from typing import Any

import dspy

from examples.ours.retriever import search, set_retriever_dir


def _get(trace: Any, key: str):
    if isinstance(trace, dict):
        return trace[key]
    return getattr(trace, key)


class HotpotMultiHop(dspy.Module):
    def __init__(
        self,
        k: int = 7,
        retriever_dir: str | None = None,
        retriever_url: str | None = None,
        configure_retriever: bool | None = None,
    ):
        super().__init__()

        self.k = k

        if retriever_dir is not None:
            set_retriever_dir(retriever_dir)

        self.retrieve_k = partial(search, k=self.k)

        self.summarize1 = dspy.ChainOfThought(
            "question,passages->summary"
        )
        self.create_query_hop2 = dspy.ChainOfThought(
            "question,summary_1->query"
        )
        self.summarize2 = dspy.ChainOfThought(
            "question,context,passages->summary"
        )
        self.final_answer = dspy.ChainOfThought(
            "question,summary_1,summary_2->answer"
        )

    def retrieve_hop1(self, question: str) -> tuple[str, list[str]]:
        query = question
        docs = self.retrieve_k(query).passages
        return query, docs

    def run_summary1(
        self,
        question: str,
        hop1_docs: list[str],
    ) -> str:
        return self.summarize1(
            question=question,
            passages=hop1_docs,
        ).summary

    def run_query(
        self,
        question: str,
        summary_1: str,
    ) -> str:
        return self.create_query_hop2(
            question=question,
            summary_1=summary_1,
        ).query

    def retrieve_hop2(self, hop2_query: str) -> list[str]:
        return self.retrieve_k(hop2_query).passages

    def run_summary2(
        self,
        question: str,
        summary_1: str,
        hop2_docs: list[str],
    ) -> str:
        return self.summarize2(
            question=question,
            context=summary_1,
            passages=hop2_docs,
        ).summary

    def run_final(
        self,
        question: str,
        summary_1: str,
        summary_2: str,
    ) -> str:
        return self.final_answer(
            question=question,
            summary_1=summary_1,
            summary_2=summary_2,
        ).answer

    @staticmethod
    def build_prediction(
        answer: str,
        hop1_query: str,
        hop1_docs: list[str],
        hop2_query: str,
        hop2_docs: list[str],
        summary_1: str,
        summary_2: str,
    ) -> dspy.Prediction:
        return dspy.Prediction(
            answer=answer,
            hop1_query=hop1_query,
            hop1_docs=hop1_docs,
            hop2_query=hop2_query,
            hop2_docs=hop2_docs,
            summary_1=summary_1,
            summary_2=summary_2,
        )

    def forward(self, question: str):
        hop1_query, hop1_docs = self.retrieve_hop1(question)
        summary_1 = self.run_summary1(question, hop1_docs)

        hop2_query = self.run_query(question, summary_1)
        hop2_docs = self.retrieve_hop2(hop2_query)
        summary_2 = self.run_summary2(
            question,
            summary_1,
            hop2_docs,
        )

        answer = self.run_final(
            question,
            summary_1,
            summary_2,
        )

        return self.build_prediction(
            answer=answer,
            hop1_query=hop1_query,
            hop1_docs=hop1_docs,
            hop2_query=hop2_query,
            hop2_docs=hop2_docs,
            summary_1=summary_1,
            summary_2=summary_2,
        )

    def rerun_from(
        self,
        question: str,
        baseline_trace,
        start_agent: str,
    ):
        """
        Re-run the selected agent and all downstream stages.

        Upstream states are copied from baseline_trace.

        start_agent:
            summary1
            query
            summary2
            final
        """
        valid_agents = {
            "summary1",
            "query",
            "summary2",
            "final",
        }
        if start_agent not in valid_agents:
            raise ValueError(
                f"Unknown start_agent={start_agent!r}. "
                f"Expected one of {sorted(valid_agents)}."
            )

        hop1_query = _get(baseline_trace, "hop1_query")
        hop1_docs = _get(baseline_trace, "hop1_docs")
        hop2_query = _get(baseline_trace, "hop2_query")
        hop2_docs = _get(baseline_trace, "hop2_docs")
        summary_1 = _get(baseline_trace, "summary_1")
        summary_2 = _get(baseline_trace, "summary_2")
        answer = _get(baseline_trace, "answer")

        if start_agent == "summary1":
            summary_1 = self.run_summary1(
                question,
                hop1_docs,
            )
            hop2_query = self.run_query(
                question,
                summary_1,
            )
            hop2_docs = self.retrieve_hop2(hop2_query)
            summary_2 = self.run_summary2(
                question,
                summary_1,
                hop2_docs,
            )
            answer = self.run_final(
                question,
                summary_1,
                summary_2,
            )

        elif start_agent == "query":
            hop2_query = self.run_query(
                question,
                summary_1,
            )
            hop2_docs = self.retrieve_hop2(hop2_query)
            summary_2 = self.run_summary2(
                question,
                summary_1,
                hop2_docs,
            )
            answer = self.run_final(
                question,
                summary_1,
                summary_2,
            )

        elif start_agent == "summary2":
            summary_2 = self.run_summary2(
                question,
                summary_1,
                hop2_docs,
            )
            answer = self.run_final(
                question,
                summary_1,
                summary_2,
            )

        elif start_agent == "final":
            answer = self.run_final(
                question,
                summary_1,
                summary_2,
            )

        return self.build_prediction(
            answer=answer,
            hop1_query=hop1_query,
            hop1_docs=hop1_docs,
            hop2_query=hop2_query,
            hop2_docs=hop2_docs,
            summary_1=summary_1,
            summary_2=summary_2,
        )


def inspect_program():
    program = HotpotMultiHop()

    print("Named predictors:")
    for name, pred in program.named_predictors():
        instructions = pred.signature.instructions
        print(
            f"- {name}: "
            f"{instructions[:120].replace(chr(10), ' ')}"
        )


if __name__ == "__main__":
    inspect_program()
