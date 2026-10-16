from sentence_transformers import SentenceTransformer

from app.retrieval.vector_store import VectorStore


class Retriever:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.store = VectorStore()

    def index(self, chunks):
        texts = [chunk["content"] for chunk in chunks]

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        self.store.add(embeddings, chunks)

    def search(self, query: str, top_k: int = 5):
        query_embedding = self.model.encode(
            query,
            normalize_embeddings=True,
        )

        results = self.store.search(query_embedding, top_k)

        for result in results:
            document = result["document"]

            result["source"] = document["source"]
            result["chunk_id"] = document["chunk_id"]
            result["content"] = document["content"]

            del result["document"]

        return results