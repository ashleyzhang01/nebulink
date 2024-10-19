from app.chromadb.init import get_chroma_collection
from app.utils.enums import ChromaCollections
import chromadb as cdb


def add_data_to_chroma(document: str, collection: ChromaCollections, id: str) -> None:
    chroma_collection = get_chroma_collection(
        collection=collection
    )
    chroma_collection.add(
        documents=[document],
        ids=[id],
    )
