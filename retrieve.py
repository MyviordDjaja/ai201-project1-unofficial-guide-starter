import chromadb
from chromadb.utils import embedding_functions

from chunk_text import chunk_text  # wherever your chunk_text() lives

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "professor_reviews"
MODEL_NAME = "all-MiniLM-L6-v2"

# Persistent client — embeddings are written to disk and survive between runs
client = chromadb.PersistentClient(path=CHROMA_PATH)

# Chroma will call this to embed both stored documents and incoming queries
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=MODEL_NAME
)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embed_fn,
    metadata={"hnsw:space": "cosine"},  # cosine distance → scores land in 0–1
)


def index_chunks(metadata_path="rmp_data/metadata.json"):
    """Embed all chunks and upsert them into the collection.

    upsert keys on `id`, so re-running overwrites existing chunks rather than
    duplicating them or raising a DuplicateID error.
    """
    chunks = chunk_text(metadata_path)

    documents = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    ids = [c["metadata"]["chunk_id"] for c in chunks]

    collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
    print(f"Indexed {len(ids)} chunks into '{COLLECTION_NAME}'.")
    return len(ids)


def retrieve(query, k=5):
    """Return the top-k chunks for a query as a list of dicts."""
    results = collection.query(query_texts=[query], n_results=k)

    # Chroma returns each field as a list-of-lists (one inner list per query).
    # We sent a single query, so everything lives at index [0].
    hits = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({"text": text, "metadata": meta, "distance": dist})
    return hits


if __name__ == "__main__":
    # Build/refresh the index. Safe to run every time thanks to upsert.
    index_chunks()

    test_queries = [
        "Does Salvatore LaMarca test students on the Unix manual?",
        "Which professor gives a lot of extra credit?",
        "Why do students dislike Shelby Funk?",
    ]

    for query in test_queries:
        print(f"\n=== Query: {query} ===")
        for i, hit in enumerate(retrieve(query, k=5), start=1):
            prof = hit["metadata"].get("professor", "?")
            print(f"\n[{i}] {prof}  (distance: {hit['distance']:.3f})")
            print(f"    {hit['text']}")