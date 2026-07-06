# /home/jinwoo/gepa-official/examples/hotpotqa/program.py
from functools import partial

import dspy

from examples.hotpotqa.retriever import search, set_retriever_dir


class HotpotMultiHop(dspy.Module):
    def __init__(
        self,
        k: int = 7,
        retriever_dir: str | None = None,
        retriever_url: str | None = None,          # kept for backward-compatible runner args
        configure_retriever: bool | None = None,   # kept for backward-compatible runner args
    ):
        super().__init__()

        self.k = k

        if retriever_dir is not None:
            set_retriever_dir(retriever_dir)

        # Artifact-compatible path:
        # Hotpot uses BM25 search over wiki.abstracts.2017, not ColBERT HTTP.
        self.retrieve_k = partial(search, k=self.k)

        self.summarize1 = dspy.ChainOfThought("question,passages->summary")
        self.create_query_hop2 = dspy.ChainOfThought("question,summary_1->query")
        self.summarize2 = dspy.ChainOfThought("question,context,passages->summary")
        self.final_answer = dspy.ChainOfThought("question,summary_1,summary_2->answer")

    def forward(self, question: str):
        # Hop 1
        hop1_query = question
        hop1_docs = self.retrieve_k(hop1_query).passages
        summary_1 = self.summarize1(
            question=question,
            passages=hop1_docs,
        ).summary

        # Hop 2
        hop2_query = self.create_query_hop2(
            question=question,
            summary_1=summary_1,
        ).query
        hop2_docs = self.retrieve_k(hop2_query).passages
        summary_2 = self.summarize2(
            question=question,
            context=summary_1,
            passages=hop2_docs,
        ).summary

        # Final answer
        answer = self.final_answer(
            question=question,
            summary_1=summary_1,
            summary_2=summary_2,
        ).answer

        return dspy.Prediction(
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
        print(f"- {name}: {pred.signature.instructions[:120].replace(chr(10), ' ')}")


if __name__ == "__main__":
    inspect_program()