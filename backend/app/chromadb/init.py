from app.utils.enums import ChromaCollections
import chromadb as cdb
from typing import Any


def get_chroma_client():
    return cdb.PersistentClient(
        path="persistent_chroma_client",
    )

def get_chroma_collection(collection: ChromaCollections) -> Any:
    chroma_client = get_chroma_client()
    return chroma_client.get_or_create_collection(
        name=collection,
    )
