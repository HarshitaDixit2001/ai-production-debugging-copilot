from app.knowledge.chunker import DocumentChunker
from app.knowledge.loader import DocumentLoader
from app.retrieval.retriever import Retriever


class KnowledgeBase:
    def __init__(self):
        self.loader = DocumentLoader()
        self.chunker = DocumentChunker()
        self.retriever = Retriever()

    def build(self):
        documents = self.loader.load_all()
        chunks = self.chunker.chunk_documents(documents)

        self.retriever.index(chunks)

        return {
            "documents": len(documents),
            "chunks": len(chunks),
        }

    def search(self, query: str, top_k: int = 5):
        return self.retriever.search(query, top_k)
