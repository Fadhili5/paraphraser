# fixed the dict vs int problem in this file

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.concurrency import run_in_threadpool

from app.paraphrase.ml_model import generate_paraphrase
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
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@router.post("/document")
async def paraphrase_doc(
    file: UploadFile = File(...),
    user=Depends(paid_user),
):
    # Read file
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An empty file was uploaded",
        )

    # Check file size
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="File is too large",
        )

    # Check content type
    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type",
        )

    # Extract text
    try:
        extracted_text = extract_text_from_file(
            file_bytes=file_bytes,
            content_type=file.content_type,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to extract text from document",
        )

    if not extracted_text or not extracted_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded document has no readable text",
        )

    # Enforce plan limits
    plan = getattr(user, "plan", "free")
    plan_config = PLAN_LIMITS.get(plan)

    if not plan_config:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unknown subscription plan",
        )

    max_chars = plan_config["max_characters"]

    if len(extracted_text) > max_chars:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="The provided document exceeds your plan limits",
        )

    # Usage guard AFTER knowing how many characters we need
    # This is where the dict vs int problem is fixed
    await usage_guard(len(extracted_text))(user)

    # Paraphrase text
    try:
        paraphrased_text = await run_in_threadpool(
            generate_paraphrase,
            extracted_text,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Paraphrasing failed",
        )

    return {
        "original_length": len(extracted_text),
        "paraphrased_length": len(paraphrased_text),
        "paraphrased_text": paraphrased_text,
    }
