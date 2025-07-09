import pandas as pd
from .openai_service import generate_response
from typing import List, Tuple

def process_csv_rows(
    df: pd.DataFrame,
    prompt_template: str,
    model: str,
    temperature: float,
    top_p: float,
    client,
    system_prompt: str
) -> Tuple[pd.DataFrame, List[str]]:
    columns = df.columns.tolist()
    processed_rows = []
    error_logs = []

    for idx, row in df.iterrows():
        try:
            prompt = prompt_template
            for col in columns:
                prompt = prompt.replace(f"{{{{{col}}}}}", str(row[col]))

            result = generate_response(client, prompt, model, temperature, top_p, system_prompt)

            row_data = row.to_dict()
            row_data['MODEL_OUTPUT'] = result
            processed_rows.append(row_data)

        except Exception as e:
            error_log = f"[Row {idx}] Error: {str(e)}"
            error_logs.append(error_log)
            row_data = row.to_dict()
            row_data['MODEL_OUTPUT'] = f"ERROR: {str(e)}"
            processed_rows.append(row_data)

    return pd.DataFrame(processed_rows), error_logs
