# /home/jinwoo/gepa-official/examples/hotpotqa/retriever.py
import os
import threading
from pathlib import Path

import bm25s
import Stemmer
import ujson
from diskcache import Cache


DEFAULT_RETRIEVER_DIR = Path(__file__).resolve().parent

_retriever_dir = Path(os.environ.get("HOTPOT_RETRIEVER_DIR", DEFAULT_RETRIEVER_DIR))
_retriever = None
_stemmer = None
_corpus = None
_cache = None
_initialized = False
_init_lock = threading.Lock()


class DotDict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")


def set_retriever_dir(directory: str):
    global _retriever_dir, _retriever, _stemmer, _corpus, _cache, _initialized

    new_dir = Path(directory)
    if new_dir == _retriever_dir and _initialized:
        return

    _retriever_dir = new_dir
    _retriever = None
    _stemmer = None
    _corpus = None
    _cache = None
    _initialized = False


def get_retriever_dir() -> str:
    return str(_retriever_dir)


def _load_corpus(corpus_path: Path) -> list[str]:
    corpus = []
    with corpus_path.open() as f:
        for line in f:
            item = ujson.loads(line)
            corpus.append(f"{item['title']} | {' '.join(item['text'])}")
    return corpus


def init_retriever():
    global _retriever, _stemmer, _corpus, _cache, _initialized

    if _initialized:
        return

    with _init_lock:
        if _initialized:
            return

        retriever_path = _retriever_dir / "bm25s_retriever"
        corpus_path = _retriever_dir / "wiki.abstracts.2017.jsonl"

        if not retriever_path.is_dir():
            raise FileNotFoundError(
                f"BM25 retriever not found: {retriever_path}"
            )

        if not corpus_path.is_file():
            raise FileNotFoundError(
                f"Corpus file not found: {corpus_path}"
            )

        _retriever = bm25s.BM25.load(str(retriever_path))
        _stemmer = Stemmer.Stemmer("english")
        _corpus = _load_corpus(corpus_path)
        _cache = Cache(str(_retriever_dir / "retriever_cache"))

        _initialized = True


def search(query: str, k: int):
    init_retriever()

    cache_key = (query, int(k))
    cached = _cache.get(cache_key)
    if cached is not None:
        return DotDict({"passages": cached})

    tokens = bm25s.tokenize(
        query,
        stopwords="en",
        stemmer=_stemmer,
        show_progress=False,
    )

    results, scores = _retriever.retrieve(
        tokens,
        k=k,
        n_threads=1,
        show_progress=False,
    )

    passages = []
    seen = set()

    for doc_id, score in zip(results[0], scores[0]):
        passage = _corpus[int(doc_id)]
        if passage in seen:
            continue
        seen.add(passage)
        passages.append(passage)
        if len(passages) >= k:
            break

    _cache.set(cache_key, passages)
    return DotDict({"passages": passages})