
import re
from pathlib import Path
import fitz
from llama_index.core.schema import Document


SECTION_RE = re.compile(r"^(\d+(?:\.\d+)*)\.\s*(.*)")


class DocumentService:

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path) if isinstance(file_path, str) else file_path

    def create_documents(self) -> list[Document]:
        text = self._read_pdf()
        body, citations = self._split_citations(text)

        lines = [l.strip() for l in body.split("\n") if l.strip()]

        docs = []

        current_id = None
        current_title = None
        buffer: list[str] = []

        def flush():
            if not current_id:
                return

            parent = ".".join(current_id.split(".")[:-1]) or None
            level = current_id.count(".") + 1

            section_header = f"Section {current_id}"
            if current_title:
                section_header += f" — {current_title}"

            content = "\n".join(buffer).strip()

            docs.append(
                Document(
                    text=f"{section_header}\n{content}",
                    metadata={
                        "section_id": current_id,
                        "parent_id": parent,
                        "level": level,
                        "title": current_title,
                        "source": self.file_path.name,
                        "citations": citations,
                    },
                )
            )

        for line in lines:
            match = SECTION_RE.match(line)
            if match:
                flush()

                current_id = match.group(1)
                title_candidate = match.group(2).strip()

                current_title = title_candidate if title_candidate else None
                buffer = []

            else:
                if current_id and current_title is None:
                    current_title = line
                else:
                    buffer.append(line)

        flush()

        return docs

    def _read_pdf(self) -> str:
        pdf = fitz.open(self.file_path)
        text = ""
        for page in pdf:
            text += page.get_text()
        pdf.close()

        text = re.sub(r"\r\n?", "\n", text)
        text = re.sub(r"\n+", "\n", text)
        return text

    def _split_citations(self, text: str):
        parts = re.split(r"Citations:", text, maxsplit=1)
        body = parts[0]

        citations = []
        if len(parts) > 1:
            citations = [c.strip() for c in parts[1].splitlines() if c.strip()]

        return body, citations