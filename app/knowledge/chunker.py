class DocumentChunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(self, document: dict) -> list[dict]:
        content = document["content"]
        source = document["source"]

        chunks = []

        start = 0
        chunk_id = 0

        while start < len(content):
            end = start + self.chunk_size

            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "source": source,
                    "content": content[start:end],
                }
            )

            chunk_id += 1
            start += self.chunk_size - self.overlap

        return chunks

    def chunk_documents(self, documents: list[dict]) -> list[dict]:
        chunks = []

        for document in documents:
            chunks.extend(self.chunk_document(document))

        return chunks