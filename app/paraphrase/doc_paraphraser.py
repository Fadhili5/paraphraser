from fastapi import HTTPException, status
from typing import Union
from io import BytesIO

import PyPDF2
import docx

supported_doc_types = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
}

def extract_text_from_file(file_bytes: bytes, content_type: str) -> str:
    if content_type not in supported_doc_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported document type",
        )

    if content_type == "application/pdf":
        reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
        # return "\n".join(reader.getPage(0).extractText() or "" for page in range(reader.numPages))

    if content_type.endswith("wordprocessingml.document"):
        doc = docx.Document(BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs)

    if content_type == "text/plain":
        return file_bytes.decode("utf-8")

    return ""