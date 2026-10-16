import numpy as np


class VectorStore:
    def __init__(self):
        self.embeddings = []
        self.documents = []

    def add(self, embeddings, documents):
        self.embeddings.extend(embeddings)
        self.documents.extend(documents)

    def search(self, query_embedding, top_k: int = 5):
        if not self.embeddings:
            return []

        query = np.array(query_embedding)

        scores = []

        for index, embedding in enumerate(self.embeddings):
            vector = np.array(embedding)

            similarity = np.dot(query, vector) / (
                np.linalg.norm(query) * np.linalg.norm(vector)
            )

            scores.append((similarity, self.documents[index]))

        scores.sort(key=lambda item: item[0], reverse=True)

        return [
            {
                "score": float(score),
                "document": document,
            }
            for score, document in scores[:top_k]
        ]