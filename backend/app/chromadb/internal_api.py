from typing import Any
from app.chromadb import get_chroma_collection
from app.chromadb.dataclass import ChromaResult
from app.utils.enums import ChromaCollections
import chromadb as cdb


def _convert_chroma_result_to_dataclass(
    chroma_result: dict,
) -> list[ChromaResult]:
    ids, documents = chroma_result.get("ids"), chroma_result.get("documents")
    chroma_results: ChromaResult = []
    for id, document in zip(ids, documents):
        chroma_results.append(
            ChromaResult(
                id=id,
                document=document,
            )
        )

    return chroma_results


def add_data_to_chroma(document: str, collection: ChromaCollections, id: str) -> None:
    chroma_collection = get_chroma_collection(
        collection=collection
    )
    chroma_collection.add(
        documents=[document],
        ids=[id],
    )


def query_from_chroma(
    query: str,
    collection: ChromaCollections,
    n_results: int,
    str_search: str = "",
) -> list[ChromaResult]:
    chroma_collection = get_chroma_collection(collection=collection)
    chroma_result = chroma_collection.query(
        query_texts=query,
        n_results=n_results,
        where_document={"$contains": str_search}
    )
    return _convert_chroma_result_to_dataclass(chroma_result=chroma_result)


def query_from_chroma_by_ids(
    ids: list[int],
    collection: ChromaCollections,
) -> list[ChromaResult]:
    chroma_collection = get_chroma_collection(collection=collection)
    chroma_result = chroma_collection.get(
        ids=ids,
    )
    return _convert_chroma_result_to_dataclass(chroma_result=chroma_result)
