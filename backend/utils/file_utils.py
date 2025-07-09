import os
import tempfile
import uuid
from fastapi import UploadFile

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

def get_progress_file_path():
    return os.path.join(tempfile.gettempdir(), "processed_ids.txt")

def load_processed_ids():
    path = get_progress_file_path()
    if not os.path.exists(path):
        return set()
    with open(path, "r") as f:
        return set(int(line.strip()) for line in f if line.strip().isdigit())

def save_processed_id(idx: int):
    path = get_progress_file_path()
    with open(path, "a") as f:
        f.write(f"{idx}\n")

def load_ignored_ids(file: UploadFile) -> set:
    contents = file.file.read().decode("utf-8")
    return set(int(line.strip()) for line in contents.splitlines() if line.strip().isdigit())

def reset_processed_ids():
    path = get_progress_file_path()
    if os.path.exists(path):
        os.remove(path)
