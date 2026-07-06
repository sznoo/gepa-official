# examples/hover/feedback.py

import dspy


def _gold_titles(module_inputs):
    return set(
        map(
            dspy.evaluate.normalize_text,
            [doc["key"] for doc in module_inputs["supporting_facts"]],
        )
    )


def _found_titles(module_outputs):
    return set(
        map(
            dspy.evaluate.normalize_text,
            [doc.split(" | ")[0] for doc in module_outputs["retrieved_docs"]],
        )
    )


def _get_docs_after_hops(captured_trace, final_found_titles):
    docs_after_hop1 = None
    docs_after_hop2 = None
    docs_after_hop3 = set(final_found_titles)

    for trace_instance in captured_trace:
        inputs = trace_instance[1]

        if set(inputs.keys()) == {"claim", "passages"}:
            docs_after_hop1 = set(
                map(
                    dspy.evaluate.normalize_text,
                    [doc.split(" | ")[0] for doc in inputs["passages"]],
                )
            )

        elif set(inputs.keys()) == {"claim", "context", "passages"}:
            docs_after_hop2 = set(
                map(
                    dspy.evaluate.normalize_text,
                    [doc.split(" | ")[0] for doc in inputs["passages"]],
                )
            )

    assert docs_after_hop1 is not None, "docs_after_hop1 is None"
    assert docs_after_hop2 is not None, "docs_after_hop2 is None"

    docs_after_hop1 = set(docs_after_hop1)
    docs_after_hop2 = set(docs_after_hop2).union(docs_after_hop1)
    docs_after_hop3 = set(docs_after_hop3).union(docs_after_hop2)

    return docs_after_hop1, docs_after_hop2, docs_after_hop3


def provide_feedback_to_summary_module(
    predictor_output,
    predictor_inputs,
    module_inputs,
    module_outputs,
    captured_trace,
):
    gold_titles = _gold_titles(module_inputs)
    found_titles = _found_titles(module_outputs)

    score = gold_titles.issubset(found_titles)

    docs_after_hop1, docs_after_hop2, docs_after_hop3 = _get_docs_after_hops(
        captured_trace,
        found_titles,
    )

    if score:
        feedback_text = (
            "Your summaries are correct and useful in guiding query generation "
            "to retrieve relevant evidence documents."
        )

    else:
        if "context" in predictor_inputs:
            # summarize2
            remaining_docs_after_hop2 = gold_titles.difference(docs_after_hop2)
            remaining_docs_at_end = gold_titles.difference(docs_after_hop3)

            docs_helped = remaining_docs_after_hop2.difference(
                remaining_docs_at_end
            )
            docs_not_helped = remaining_docs_after_hop2.intersection(
                remaining_docs_at_end
            )

            feedback_text = f"""Your summaries are used to generate queries to identify evidence relevant to the claim.
{'**Successful retrieval:** Your summary correctly helped retrieve the following evidence: ' + ', '.join(docs_helped) + '. ' if docs_helped else ''}
{'**Missing evidence:** However, your summary could not help make the connection to these key evidence: ' + ', '.join(docs_not_helped) + '. ' if docs_not_helped else ''}

Think about how you can make the connection between the provided passages and the missed evidence relevant to the claim."""

        else:
            # summarize1
            remaining_docs_after_hop1 = gold_titles.difference(docs_after_hop1)
            remaining_docs_at_end = gold_titles.difference(docs_after_hop3)

            docs_helped = remaining_docs_after_hop1.difference(
                remaining_docs_at_end
            )
            docs_not_helped = remaining_docs_after_hop1.intersection(
                remaining_docs_at_end
            )

            feedback_text = f"""Your summaries are used to generate queries to identify evidence relevant to the claim.

{'**Successful retrieval:** Your summary correctly helped retrieve the following evidence: ' + ', '.join(docs_helped) + '. ' if docs_helped else ''}
{'**Missing evidence:** However, your summary could not help make the connection to these key evidence: ' + ', '.join(docs_not_helped) + '. ' if docs_not_helped else ''}

Think about how you can make the connection between the provided passages and the missed evidence relevant to the claim."""

    return {
        "score": float(score),
        "feedback": feedback_text,
    }


def provide_feedback_to_query_module(
    predictor_output,
    predictor_inputs,
    module_inputs,
    module_outputs,
    captured_trace,
):
    gold_titles = _gold_titles(module_inputs)
    found_titles = _found_titles(module_outputs)

    docs_after_hop1, docs_after_hop2, docs_after_hop3 = _get_docs_after_hops(
        captured_trace,
        found_titles,
    )

    score = gold_titles.issubset(found_titles)

    if score:
        feedback_text = (
            "Your queries are correct and useful in retrieving relevant "
            "evidence documents."
        )

    else:
        if "summary_2" in predictor_inputs:
            # create_query_hop3
            remaining_docs_after_hop2 = gold_titles.difference(docs_after_hop2)
            remaining_docs_at_end = gold_titles.difference(docs_after_hop3)

            docs_helped = remaining_docs_after_hop2.difference(
                remaining_docs_at_end
            )
            docs_not_helped = remaining_docs_after_hop2.intersection(
                remaining_docs_at_end
            )

            feedback_text = f"""Your queries are used to identify evidence relevant to the claim.
{'**Successful retrieval:** Your query correctly helped retrieve the following evidence: ' + ', '.join(docs_helped) + '. ' if docs_helped else ''}
{'**Missing evidence:** However, your query could not help retrieve these key evidence: ' + ', '.join(docs_not_helped) + '. ' if docs_not_helped else ''}
Think about how you can modify your query to make the connection between the provided summary and the missed evidence relevant to the claim."""

        else:
            # create_query_hop2
            remaining_docs_after_hop1 = gold_titles.difference(docs_after_hop1)
            remaining_docs_after_hop2 = gold_titles.difference(docs_after_hop2)

            docs_helped = remaining_docs_after_hop1.difference(
                remaining_docs_after_hop2
            )
            docs_not_helped = remaining_docs_after_hop1.intersection(
                remaining_docs_after_hop2
            )

            feedback_text = f"""Your queries are used to identify evidence relevant to the claim.
{'**Successful retrieval:** Your query correctly helped retrieve the following evidence: ' + ', '.join(docs_helped) + '. ' if docs_helped else ''}
{'**Missing evidence:** However, your query could not help retrieve these key evidence: ' + ', '.join(docs_not_helped) + '. ' if docs_not_helped else ''}

Think about how you can modify your query to make the connection between the provided summary and the missed evidence relevant to the claim."""

    return {
        "score": float(score),
        "feedback": feedback_text,
    }


feedback_fn_map = {
    "create_query_hop2.predict": provide_feedback_to_query_module,
    "create_query_hop3.predict": provide_feedback_to_query_module,
    "summarize1.predict": provide_feedback_to_summary_module,
    "summarize2.predict": provide_feedback_to_summary_module,
}