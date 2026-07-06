# examples/hover/program.py

import os
import tarfile
import threading
from functools import partial
from pathlib import Path

import bm25s
import dspy
import Stemmer
import ujson
from diskcache import Cache
from huggingface_hub import hf_hub_download


class DotDict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{key}'"
            )

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{key}'"
            )


def get_retriever_dir() -> Path:
    return Path(os.environ.get("HOVER_RETRIEVER_DIR", Path(__file__).parent)).resolve()


stemmer = None
retriever = None
corpus = None
initialized = False
init_lock = threading.Lock()

cache = Cache(str(get_retriever_dir() / "retriever_cache"))


def initialize_bm25s_retriever_and_corpus(directory: Path):
    directory.mkdir(parents=True, exist_ok=True)

    jsonl_path = directory / "wiki.abstracts.2017.jsonl"
    retriever_path = directory / "bm25s_retriever"

    if not jsonl_path.exists():
        tar_path = hf_hub_download(
            repo_id="dspy/cache",
            filename="wiki.abstracts.2017.tar.gz",
            local_dir=str(directory),
        )
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=directory)

    assert jsonl_path.exists(), f"Corpus file not found: {jsonl_path}"

    corpus_data = []
    with open(jsonl_path) as f:
        for line in f:
            row = ujson.loads(line)
            corpus_data.append(f"{row['title']} | {' '.join(row['text'])}")

    local_stemmer = Stemmer.Stemmer("english")
    corpus_tokens = bm25s.tokenize(
        corpus_data,
        stopwords="en",
        stemmer=local_stemmer,
    )

    local_retriever = bm25s.BM25(k1=0.9, b=0.4)
    local_retriever.index(corpus_tokens)
    local_retriever.save(str(retriever_path))

    assert retriever_path.exists(), f"Retriever not saved: {retriever_path}"


def init_retriever():
    global retriever, stemmer, corpus, initialized

    if initialized:
        return

    with init_lock:
        if initialized:
            return

        directory = get_retriever_dir()
        jsonl_path = directory / "wiki.abstracts.2017.jsonl"
        retriever_path = directory / "bm25s_retriever"

        if not jsonl_path.exists() or not retriever_path.exists():
            initialize_bm25s_retriever_and_corpus(directory)

        retriever = bm25s.BM25.load(str(retriever_path))
        stemmer = Stemmer.Stemmer("english")

        corpus_data = []
        with open(jsonl_path) as f:
            for line in f:
                row = ujson.loads(line)
                corpus_data.append(f"{row['title']} | {' '.join(row['text'])}")

        corpus = corpus_data
        initialized = True


@cache.memoize()
def search(query: str, k: int) -> DotDict:
    init_retriever()

    tokens = bm25s.tokenize(
        query,
        stopwords="en",
        stemmer=stemmer,
        show_progress=False,
    )
    results, scores = retriever.retrieve(
        tokens,
        k=k,
        n_threads=1,
        show_progress=False,
    )

    run = {
        corpus[doc]: float(score)
        for doc, score in zip(results[0], scores[0])
    }

    return DotDict({"passages": list(run.keys())[:k]})


class HoverMultiHopPredict(dspy.Module):
    def __init__(self, k: int = 7):
        super().__init__()
        self.k = k

        self.create_query_hop2 = dspy.Predict("claim,summary_1->query")
        self.create_query_hop3 = dspy.Predict("claim,summary_1,summary_2->query")
        self.summarize1 = dspy.Predict("claim,passages->summary")
        self.summarize2 = dspy.Predict("claim,context,passages->summary")

        self.retrieve_k = partial(search, k=self.k)
        self.retrieve_10 = partial(search, k=10)

    def forward(self, claim):
        hop1_docs = self.retrieve_k(claim).passages
        summary_1 = self.summarize1(
            claim=claim,
            passages=hop1_docs,
        ).summary

        hop2_query = self.create_query_hop2(
            claim=claim,
            summary_1=summary_1,
        ).query
        hop2_docs = self.retrieve_k(hop2_query).passages
        summary_2 = self.summarize2(
            claim=claim,
            context=summary_1,
            passages=hop2_docs,
        ).summary

        hop3_query = self.create_query_hop3(
            claim=claim,
            summary_1=summary_1,
            summary_2=summary_2,
        ).query
        hop3_docs = self.retrieve_10(hop3_query).passages

        return dspy.Prediction(
            retrieved_docs=hop1_docs + hop2_docs + hop3_docs,
            hop1_docs=hop1_docs,
            hop2_docs=hop2_docs,
            hop3_docs=hop3_docs,
            summary_1=summary_1,
            summary_2=summary_2,
            hop2_query=hop2_query,
            hop3_query=hop3_query,
        )


class HoverMultiHop(dspy.Module):
    def __init__(self, k: int = 7):
        super().__init__()
        self.k = k

        self.create_query_hop2 = dspy.ChainOfThought("claim,summary_1->query")
        self.create_query_hop3 = dspy.ChainOfThought("claim,summary_1,summary_2->query")
        self.summarize1 = dspy.ChainOfThought("claim,passages->summary")
        self.summarize2 = dspy.ChainOfThought("claim,context,passages->summary")

        self.retrieve_k = partial(search, k=self.k)
        self.retrieve_10 = partial(search, k=10)

    def forward(self, claim):
        hop1_docs = self.retrieve_k(claim).passages
        summary_1 = self.summarize1(
            claim=claim,
            passages=hop1_docs,
        ).summary

        hop2_query = self.create_query_hop2(
            claim=claim,
            summary_1=summary_1,
        ).query
        hop2_docs = self.retrieve_k(hop2_query).passages
        summary_2 = self.summarize2(
            claim=claim,
            context=summary_1,
            passages=hop2_docs,
        ).summary

        hop3_query = self.create_query_hop3(
            claim=claim,
            summary_1=summary_1,
            summary_2=summary_2,
        ).query
        hop3_docs = self.retrieve_10(hop3_query).passages

        return dspy.Prediction(
            retrieved_docs=hop1_docs + hop2_docs + hop3_docs,
            hop1_docs=hop1_docs,
            hop2_docs=hop2_docs,
            hop3_docs=hop3_docs,
            summary_1=summary_1,
            summary_2=summary_2,
            hop2_query=hop2_query,
            hop3_query=hop3_query,
        )


def inspect_program():
    program = HoverMultiHop()

    print("Predictors:")
    for name, pred in program.named_predictors():
        print(f"- {name}")
        print(pred.signature.instructions)
        print()


if __name__ == "__main__":
    inspect_program()