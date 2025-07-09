import os
import tempfile
import uuid

def save_temp_csv(df):
    path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.csv")
    df.to_csv(path, index=False)
    return path


def save_log_file(logs: list, csv_path: str, only_if_error: bool = True):
    if only_if_error and not logs:
        return ""
    log_path = csv_path.replace(".csv", "_log.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(logs))
    return log_path
