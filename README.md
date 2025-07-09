# CSV-GPT Processor

A modular and extensible platform to process CSV data using OpenAI GPT models, with a focus on flexibility, fault-tolerance, and interactive control via Streamlit UI.

---

## 🚀 Features

- **CSV Upload**: Upload your dataset for processing.
- **Prompt Templating**: Use `{{column_name}}` placeholders to dynamically fill rows into prompts.
- **Model Selection**: Choose from available OpenAI models or input manually.
- **Advanced Controls**: Adjust `temperature`, `top_p`, system prompt, and concurrency level.
- **Ignore Row Support**: Optionally upload a `.txt` file with row indices to skip.
- **Resumable Processing**: Keeps track of processed rows to resume safely after interruptions.
- **Multi-threaded Execution**: Leverages concurrent processing to speed up row-level inference.
- **Downloadable Output**: Processed results and processed row IDs are available for download.
- **Logging**: All processing logs are saved both in terminal and `~/csv_gpt_debug.log`.
- **Clean UI**: Streamlit interface with clear sectioning and real-time controls.


---

## ⚙️ Requirements

- Python 3.9+
- OpenAI API Key
- Dependencies listed in `requirements.txt`

---

## 💻 Running Locally

1. Clone the repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt

4. Start the backend (FastAPI)
```bash
PYTHONPATH=. uvicorn backend.app:app --reload

5. Start the frontend (Streamlit)
```bash
streamlit run frontend/app.py

```bash
The UI will be served at: http://localhost:8501

