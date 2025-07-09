from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd
from typing import Optional

from backend.services.openai_service import get_openai_client
from backend.services.csv_processor import process_csv_rows
from backend.utils.file_utils import (
    save_temp_csv, save_log_file,
    load_ignored_ids, reset_processed_ids
)

router = APIRouter()

@router.post("/process/")
async def process_file(
    file: UploadFile = File(...),
    prompt: str = Form(...),
    api_key: str = Form(...),
    model: str = Form("gpt-4o"),
    temperature: float = Form(0.2),
    top_p: float = Form(0.9),
    num_threads: int = Form(6),
    system_prompt: str = Form(""),
    ignored_file: Optional[UploadFile] = File(None)
):
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    file.file.seek(0)

    df = pd.read_csv(file.file)
    print("📥 CSV loaded:", df.shape)

    ignored_ids = set()
    if ignored_file is not None:
        ignored_ids = load_ignored_ids(ignored_file)

    client = get_openai_client(api_key)

    try:
        output_df, error_logs = process_csv_rows(
            df=df,
            prompt_template=prompt,
            model=model,
            temperature=temperature,
            top_p=top_p,
            client=client,
            system_prompt=system_prompt,
            ignored_ids=ignored_ids,
            num_threads=num_threads
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    output_path = save_temp_csv(output_df)
    log_path = save_log_file(error_logs, output_path, only_if_error=True)

    return FileResponse(output_path, filename="processed_output.csv", headers={"X-Log-Path": log_path})


@router.post("/reset/")
def reset_state():
    reset_processed_ids()
    return JSONResponse(content={"message": "✅ Processing state has been reset."})
