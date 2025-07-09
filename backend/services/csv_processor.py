import os
import re
import logging
import pandas as pd
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from backend.services.openai_service import generate_response
from backend.utils.file_utils import load_processed_ids, save_processed_id

# ────── Logging Setup ────── #
logger = logging.getLogger("csv_processor")
if not logger.hasHandlers():
    logger.setLevel(logging.INFO)

    log_path = os.path.join(os.path.expanduser("~"), "csv_gpt_debug.log")

    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

logger.info("🔄 Logger initialized.")


# ────── Row Processor ────── #
def process_row(row, idx, columns, prompt_template, model, temperature, top_p, client, system_prompt):
    try:
        prompt = prompt_template
        logger.info(f"🌀 Processing row {idx}")
        for col in columns:
            value = str(row[col])
            prompt = prompt.replace(f"{{{{{col}}}}}", value)
            logger.info(f"   └ {col}: {value}")

        logger.info(f"📤 Final prompt:\n{prompt}")

        result = generate_response(client, prompt, model, temperature, top_p, system_prompt)
        logger.info(f"✅ Row {idx} → result: {result}")

        row_data = row.to_dict()
        row_data['MODEL_OUTPUT'] = result
        return idx, row_data, None

    except Exception as e:
        logger.error(f"❌ Error in row {idx}: {str(e)}")
        row_data = row.to_dict()
        row_data['MODEL_OUTPUT'] = f"ERROR: {str(e)}"
        return idx, row_data, f"[Row {idx}] Error: {str(e)}"


# ────── CSV Processor ────── #
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

    # Validate prompt variables
    for col in re.findall(r"{{(.*?)}}", prompt_template):
        if col not in df.columns:
            raise ValueError(f"⚠️ Column '{col}' not found in CSV headers.")

    processed_ids = load_processed_ids()
    logger.info(f"\n📊 Loaded CSV with {len(df)} rows")
    logger.info(f"⛔ Ignored rows: {len(ignored_ids) if ignored_ids else 0}")
    logger.info(f"✅ Already processed: {len(processed_ids)}")

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

    logger.info(f"\n🧾 Finished. Total processed: {len(processed_rows)}")
    if error_logs:
        logger.warning(f"⚠️ Rows with errors: {len(error_logs)}")

    return pd.DataFrame(processed_rows), error_logs
