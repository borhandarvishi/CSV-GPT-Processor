from fastapi import APIRouter, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
import pandas as pd

from backend.services.openai_service import get_openai_client
from backend.services.csv_processor import process_csv_rows
from backend.utils.file_utils import save_temp_csv, save_log_file


router = APIRouter()


@router.post("/process/")
async def process_file(
    file: UploadFile,
    prompt: str = Form(...),
    api_key: str = Form(...),
    model: str = Form("gpt-4o"),
    temperature: float = Form(0.2),
    top_p: float = Form(0.9),
    system_prompt: str = Form("")
):
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    file.file.seek(0)
    df = pd.read_csv(file.file)

    client = get_openai_client(api_key)
    output_df, error_logs = process_csv_rows(
        df=df,
        prompt_template=prompt,
        model=model,
        temperature=temperature,
        top_p=top_p,
        client=client,
        system_prompt=system_prompt
    )

    output_path = save_temp_csv(output_df)
    log_path = save_log_file(error_logs, output_path, only_if_error=True)

    return FileResponse(output_path, filename="processed_output.csv", headers={"X-Log-Path": log_path})
