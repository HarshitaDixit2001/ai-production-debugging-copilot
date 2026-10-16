class ContextBuilder:

    def build(self, results: list[dict]) -> str:
        if not results:
            return "No relevant evidence found."

        sections = []

        for index, result in enumerate(results, start=1):
            chunk = result.get("chunk_id", "tool-result")
            score = result.get("score", 0.0)

            sections.append(
                f"""Evidence {index}
Source: {result["source"]}
Chunk: {chunk}
Similarity: {score:.4f}

{result["content"]}
"""
            )

        return "\n---\n".join(sections)