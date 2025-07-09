import pandas as pd
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from backend.services.openai_service import generate_response
from backend.utils.file_utils import load_processed_ids, save_processed_id
from typing import List, Tuple

def process_row(row, idx, columns, prompt_template, model, temperature, top_p, client, system_prompt):
    try:
        prompt = prompt_template
        for col in columns:
            prompt = prompt.replace(f"{{{{{col}}}}}", str(row[col]))

        result = generate_response(client, prompt, model, temperature, top_p, system_prompt)
        row_data = row.to_dict()
        row_data['MODEL_OUTPUT'] = result
        return idx, row_data, None
    except Exception as e:
        error_log = f"[Row {idx}] Error: {str(e)}"
        row_data = row.to_dict()
        row_data['MODEL_OUTPUT'] = f"ERROR: {str(e)}"
        return idx, row_data, error_log

def process_csv_rows(
    df: pd.DataFrame,
    prompt_template: str,
    model: str,
    temperature: float,
    top_p: float,
    client,
    system_prompt: str,
    ignored_ids: set = None,
    num_threads: int = 6
) -> Tuple[pd.DataFrame, List[str]]:
    columns = df.columns.tolist()
    processed_rows = []
    error_logs = []

    # validate prompt columns
    for col in re.findall(r"{{(.*?)}}", prompt_template):
        if col not in df.columns:
            raise ValueError(f"⚠️ Column '{col}' not found in CSV headers.")

    processed_ids = load_processed_ids()
    print(f"🧮 Total rows: {len(df)} | Ignored: {len(ignored_ids)} | Already processed: {len(processed_ids)}")

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for idx, row in df.iterrows():
            if idx in processed_ids or (ignored_ids and idx in ignored_ids):
                continue
            futures.append(executor.submit(
                process_row, row, idx, columns,
                prompt_template, model, temperature, top_p, client, system_prompt
            ))

        for future in as_completed(futures):
            idx, row_data, error_log = future.result()
            processed_rows.append(row_data)
            save_processed_id(idx)
            if error_log:
                error_logs.append(error_log)

    print(f"✅ Processed {len(processed_rows)} rows.")
    return pd.DataFrame(processed_rows), error_logs
