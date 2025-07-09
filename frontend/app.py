# frontend/app.py
import streamlit as st
import requests
import pandas as pd
import io
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.api.routes import router

st.set_page_config(page_title="CSV GPT Processor", layout="wide")

# ---------- Sidebar Configuration ----------
st.sidebar.title("⚙️ Model Configuration")

# API Key Input
api_key = st.sidebar.text_input("🔑 OpenAI API Key", type="password")

# Model Selection
model_mode = st.sidebar.radio("Model Input Mode", ["Dropdown", "Manual"], horizontal=True)

if model_mode == "Dropdown":
    model = st.sidebar.selectbox("Choose a model", ["gpt-4o", "gpt-4", "gpt-3.5-turbo"])
else:
    model = st.sidebar.text_input("Enter model name manually", value="gpt-4o")

# Advanced Settings
with st.sidebar.expander("🔧 Advanced Parameters"):
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, step=0.05)
    top_p = st.slider("Top-p", 0.0, 1.0, 0.9, step=0.05)
    system_prompt = st.text_area("System Prompt (optional)", placeholder="e.g., You are a helpful assistant...", height=100)

# ---------- Main Layout ----------
st.title("📄 CSV Processor with GPT")

# File Upload Section
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("File uploaded successfully!")

    with st.expander("🔍 Preview Uploaded Data"):
        st.dataframe(df.head(), use_container_width=True)

    # Prompt Section
    st.subheader("📝 Prompt Template")
    prompt = st.text_area(
        "Enter your prompt. Use {{column_name}} to reference columns:",
        height=150,
        placeholder="Classify this text: {{HozeFaaliat}}"
    )

    # Process Button
    if st.button("🚀 Run GPT Processing"):
        with st.spinner("Processing via OpenAI..."):
            file_bytes = uploaded_file.getvalue()
            files = {'file': (uploaded_file.name, io.BytesIO(file_bytes))}
            data = {
                'prompt': prompt,
                'api_key': api_key,
                'model': model,
                'temperature': str(temperature),
                'top_p': str(top_p),
                'system_prompt': system_prompt
            }

            response = requests.post("http://localhost:8000/process/", files=files, data=data)

            if response.status_code == 200:
                st.success("✅ Processing complete. Download your results below.")
                st.download_button("📥 Download Processed CSV", response.content, file_name="output.csv")

                # Load error logs if present
                log_path = response.headers.get("X-Log-Path")
                if log_path and "error" in log_path:
                    try:
                        with open(log_path, "r", encoding="utf-8") as f:
                            logs = f.read()
                        if logs.strip():
                            st.error("Some rows failed. See logs below:")
                            st.text_area("Errors", value=logs, height=300)
                    except:
                        pass
            else:
                st.error(f"❌ Error: {response.status_code}")
                st.text(response.text)
else:
    st.info("📎 Please upload a CSV file to begin.")
