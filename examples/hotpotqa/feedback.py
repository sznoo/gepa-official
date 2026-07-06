# /home/jinwoo/gepa-official/examples/hotpotqa/feedback.py
from examples.hotpotqa.metric import answer_match_fn, answer_exact_match_with_feedback


def _get(obj, key, default=None):
    if hasattr(obj, key):
        return getattr(obj, key)
    if isinstance(obj, dict):
        return obj.get(key, default)
    try:
        return obj[key]
    except Exception:
        return default


def _title_set_from_docs(docs):
    return set([d.split(" | ")[0].strip() for d in docs])


def _title_to_sentences(example):
    context = _get(example, "context", {}) or {}
    return {
        title: sentences
        for title, sentences in zip(context["title"], context["sentences"])
    }


def _gold_titles(example):
    supporting_facts = _get(example, "supporting_facts", {}) or {}
    return set([t.strip() for t in supporting_facts["title"]])


def _gold_answer(example):
    return _get(example, "answer")


def provide_feedback_to_answer_module(
    predictor_output, predictor_inputs, module_inputs, module_outputs, captured_trace
):
    prediction = answer_exact_match_with_feedback(module_inputs, module_outputs)
    return {
        "score": prediction.score,
        "feedback": prediction.feedback,
    }


def provide_feedback_to_query_module(
    predictor_output, predictor_inputs, module_inputs, module_outputs, captured_trace
):
    assert "question" in predictor_inputs
    assert "summary_1" in predictor_inputs

    hop1_docs = _get(module_outputs, "hop1_docs", [])
    hop2_docs = _get(module_outputs, "hop2_docs", [])

    docs_after_hop1 = _title_set_from_docs(hop1_docs)
    docs_after_hop2 = _title_set_from_docs(hop2_docs).union(docs_after_hop1)

    gold_titles = _gold_titles(module_inputs)

    relevant_docs_after_hop1 = gold_titles.intersection(docs_after_hop1)
    relevant_docs_after_hop2 = gold_titles.intersection(docs_after_hop2)
    new_relevant_docs_after_hop2 = relevant_docs_after_hop2.difference(
        relevant_docs_after_hop1
    )

    total_remaining_docs_after_hop2 = gold_titles.difference(docs_after_hop2)
    total_remaining_docs_after_hop1 = gold_titles.difference(docs_after_hop1)

    docs_remaining_after_hop1_not_retrieved_in_hop2 = (
        total_remaining_docs_after_hop1.difference(docs_after_hop2)
    )

    title_to_sentences = _title_to_sentences(module_inputs)
    full_docs_remaining_after_hop1_not_retrieved_in_hop2 = [
        f"{title} | {''.join(title_to_sentences[title])}"
        for title in docs_remaining_after_hop1_not_retrieved_in_hop2
        if title in title_to_sentences
    ]

    question = _get(module_inputs, "question")
    gold_answer = _gold_answer(module_inputs)

    feedback_text = f"""You are optimizing the query generation for the **second hop** of a multi-hop retrieval system. Your goal is to help the system find all relevant documents necessary to answer the following question:

    "{question}"

The correct answer is: "{gold_answer}".

**System behavior overview:**
- **First hop:** Documents were retrieved directly using the original question.
- **Second hop (your query):** Your query aims to retrieve additional relevant documents not found in the first hop.

**Analysis:**
- Documents relevant to the answer retrieved in the first hop: {sorted(relevant_docs_after_hop1)}
- Documents still needing retrieval after the first hop: {sorted(total_remaining_docs_after_hop2)}
- New relevant documents your earlier query retrieved in the second hop: {sorted(new_relevant_docs_after_hop2)}

**Feedback for improvement:**
Your query successfully retrieved {len(new_relevant_docs_after_hop2)} out of {len(total_remaining_docs_after_hop2)} remaining relevant document(s) in the second hop. To improve:
- Analyze the missing documents: {sorted(full_docs_remaining_after_hop1_not_retrieved_in_hop2)}
- How can you rephrase or adjust your query to better target these?

**Tip:** Consider what connections or clues from the retrieved first hop documents could help surface the remaining relevant ones."""

    return {
        "score": answer_match_fn(
            _get(module_outputs, "answer", ""),
            [_get(module_inputs, "answer")],
            frac=1.0,
        ),
        "feedback": feedback_text,
    }


def provide_feedback_to_summary2_module(
    predictor_output, predictor_inputs, module_inputs, module_outputs, captured_trace
):
    assert "question" in predictor_inputs
    assert "context" in predictor_inputs
    assert "passages" in predictor_inputs

    hop1_docs = _get(module_outputs, "hop1_docs", [])
    hop2_docs = _get(module_outputs, "hop2_docs", [])

    docs_after_hop1 = _title_set_from_docs(hop1_docs)
    docs_after_hop2 = _title_set_from_docs(hop2_docs).union(docs_after_hop1)

    gold_titles = _gold_titles(module_inputs)
    relevant_docs_after_hop2 = gold_titles.intersection(docs_after_hop2)
    total_remaining_docs_after_hop2 = gold_titles.difference(docs_after_hop2)

    title_to_sentences = _title_to_sentences(module_inputs)
    supporting_facts = _get(module_inputs, "supporting_facts", {}) or {}

    question = _get(module_inputs, "question")
    gold_answer = _gold_answer(module_inputs)

    final_score = answer_match_fn(
        _get(module_outputs, "answer", ""),
        [_get(module_inputs, "answer")],
        frac=1.0,
    )

    ideal_summary_2 = "\n   ".join(
        [
            f"{title} | {title_to_sentences[title][sent_id]}"
            for title, sent_id in zip(
                supporting_facts["title"],
                supporting_facts["sent_id"],
            )
            if title in title_to_sentences and 0 <= sent_id < len(title_to_sentences[title])
        ]
    )

    feedback_text = f"""You are the summary generation module in a multi-hop QA system, responsible for producing a high-quality, informative summary from the input question, an intermediate summary (context), and newly retrieved passages. Your summary will be used *directly* by the answer generation module to finalize the answer, which has no access to the underlying passages or full context.

Your goal is to integrate and synthesize information relevant to answering the multi-hop question: "{question}". The correct answer is "{gold_answer}".

An ideal summary to answer this question would have included all of the following information:
   {ideal_summary_2}

While your input passages may not always contain every necessary detail, you should aim to bridge any gaps by inferring or generalizing, drawing upon information from both the initial summary and new passages. Strive to match the coverage and relevance of the ideal summary, ensuring your output contains all key supporting information needed for accurate answer generation.

Keep your summary precise and well-structured, including all necessary connections and facts that enable the answer module to confidently arrive at the correct answer."""

    return {
        "score": final_score,
        "feedback": feedback_text,
    }


def provide_feedback_to_summarize1_module(
    predictor_output, predictor_inputs, module_inputs, module_outputs, captured_trace
):
    question = _get(module_inputs, "question")
    gold_answer = _gold_answer(module_inputs)

    gold_titles = _gold_titles(module_inputs)
    title_to_sentences = _title_to_sentences(module_inputs)
    supporting_facts = _get(module_inputs, "supporting_facts", {}) or {}

    hop1_docs = _get(module_outputs, "hop1_docs", [])
    docs_after_hop1 = _title_set_from_docs(hop1_docs)

    relevant_docs_after_hop1 = gold_titles.intersection(docs_after_hop1)
    missing_docs_after_hop1 = gold_titles.difference(docs_after_hop1)

    full_missing_docs = [
        f"{title} | {''.join(title_to_sentences[title])}"
        for title in missing_docs_after_hop1
        if title in title_to_sentences
    ]

    ideal_summary = "\n   ".join(
        [
            f"{title} | {title_to_sentences[title][sent_id]}"
            for title, sent_id in zip(
                supporting_facts["title"],
                supporting_facts["sent_id"],
            )
            if title in title_to_sentences and 0 <= sent_id < len(title_to_sentences[title])
        ]
    )

    feedback_text = f"""You are the first-hop **summarization module** in a multi-hop QA system, responsible for distilling the most critical information from the top retrieved passages in response to the initial question:

    "{question}"

Your summary must serve two purposes:
1. **Enable the creation of a focused, effective follow-up query** (for the second hop).
2. **Provide a strong foundation for the answer generation module** (later stages depend on what you include here).

**Analysis:**
- Relevant documents retrieved in the first hop: {sorted(relevant_docs_after_hop1)}
- Relevant documents still missing after first hop: {sorted(missing_docs_after_hop1)}

**Ideal summary for this question would include:**
-----
{ideal_summary}
-----

**Feedback:**
- Ensure you cover all necessary facts and clues from the retrieved passages, especially any information that could help generate queries to surface missing supporting facts (such as connections, entities, or bridging concepts).
- Try to represent key details from the cited relevant documents ({sorted(relevant_docs_after_hop1)}), and highlight information that might help hint or bridge to the remaining facts: {sorted(full_missing_docs)}
- If you missed mentioning or signaling these, it may become impossible for the system to retrieve them in the next hop, or generate the correct answer at the end.

**Tip:** When summarizing, don't just compress; synthesize—include both direct answers and clues required for the system's next steps."""

    return {
        "score": answer_match_fn(
            _get(module_outputs, "answer", ""),
            [gold_answer],
            frac=1.0,
        ),
        "feedback": feedback_text,
    }


feedback_fn_map = {
    "create_query_hop2.predict": provide_feedback_to_query_module,
    "final_answer.predict": provide_feedback_to_answer_module,
    "summarize1.predict": provide_feedback_to_summarize1_module,
    "summarize2.predict": provide_feedback_to_summary2_module,
}