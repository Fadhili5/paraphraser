from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status

from app.paraphrase.ml_model import generate_paraphrase
from app.paraphrase.doc_paraphraser import extract_text_from_file
from app.auth.guard import paid_user

router = APIRouter(prefix="/v1/paraphrase", tags=["Paraphrase"])

@router.post("/document")
async def paraphrase_doc(file: UploadFile = File(...), user=Depends(paid_user)):
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file was uploaded",
        )

    extracted_text = extract_text_from_file(file_bytes=file_bytes, content_type=file.content_type)
    if not extracted_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The document has no readable text",
        )
    paraphrased_text = generate_paraphrase(extracted_text)

    return {
        "original_length": len(extracted_text),
        "paraphrased_text": paraphrased_text,
    }