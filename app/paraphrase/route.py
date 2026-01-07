from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status

from app.paraphrase.ml_model import generate_paraphrase
from fastapi.concurrency import run_in_threadpool
from app.paraphrase.doc_paraphraser import extract_text_from_file
from app.auth.guard import paid_user
from app.billing.usage_guard import usage_guard
from app.billing.plans import PLAN_LIMITS
from app.paraphrase.limits import MAX_FILE_SIZE_BYTES

router = APIRouter(prefix="/v1/paraphrase", tags=["Paraphrase"])

allowed_content_types = {
    "application/pdf",
    "text/plain",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}

@router.post("/document")
async def paraphrase_doc(file: UploadFile = File(...), user=Depends(paid_user), _=Depends(usage_guard)):
    # Read file
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An empty file was uploaded"
        )

    # check to verify the max number of file bytes
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="File is too large"
        )

    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type"
        )

    # extract text
    try:
        extracted_text = extract_text_from_file(file_bytes=file_bytes, content_type=file.content_type)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to extract text from document"
        )

    if not extracted_text or not extracted_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded document has no readable text"
        )

    # enforce plan limits (example: max characters)
    plan = getattr(user, "plan", "free")
    max_chars = PLAN_LIMITS.get(plan)

    if max_chars is not None and len(extracted_text) > max_chars:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="The provided document exceeds your plan limits"
        )

    # paraphrase text
    try:
        paraphrased_text = await run_in_threadpool(
            generate_paraphrase, extracted_text
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Paraphrasing failed"
        )

    return {
        "original_length": len(extracted_text),
        "paraphrased_length": len(paraphrased_text),
        "paraphrased_text": paraphrased_text,
    }
