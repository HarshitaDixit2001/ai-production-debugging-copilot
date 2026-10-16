from pathlib import Path


class DocumentLoader:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)

    def load_text_files(self) -> list[dict]:
        documents = []

        for path in self.data_dir.rglob("*"):
            if path.is_file() and path.suffix in {".log", ".md", ".py"}:
                documents.append(
                    {
                        "source": str(path),
                        "content": path.read_text(encoding="utf-8"),
                    }
                )

        return documents

    def load_json_files(self) -> list[dict]:
        documents = []

        for path in self.data_dir.rglob("*.json"):
            documents.append(
                {
                    "source": str(path),
                    "content": path.read_text(encoding="utf-8"),
                }
            )

        return documents

    def load_all(self) -> list[dict]:
        return self.load_text_files() + self.load_json_files()