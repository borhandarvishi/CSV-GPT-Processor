import streamlit as st
import requests
import pandas as pd
import io

st.set_page_config(page_title="CSV GPT Processor", layout="wide")
st.title("📄 CSV Processor with OpenAI")

# ---------- Sidebar Configuration ----------
st.sidebar.title("⚙️ Model Configuration")

api_key = st.sidebar.text_input("🔑 OpenAI API Key", type="password")

model_mode = st.sidebar.radio("Model Input Mode", ["Dropdown", "Manual"], horizontal=True)
if model_mode == "Dropdown":
    model = st.sidebar.selectbox("Choose a model", ["gpt-4o", "gpt-4", "gpt-3.5-turbo"])
else:
    model = st.sidebar.text_input("Enter model name manually", value="gpt-4o")

with st.sidebar.expander("🔧 Advanced Parameters"):
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, step=0.05)
    top_p = st.slider("Top-p", 0.0, 1.0, 0.9, step=0.05)
    num_threads = st.slider("Number of Threads", 1, 16, 6)
    system_prompt = st.text_area("System Prompt (optional)", placeholder="e.g., You are a helpful assistant...", height=100)

# ---------- Main Layout ----------
uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])
ignored_file = st.file_uploader("🚫 (Optional) Upload ignored rows (TXT)", type=["txt"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File uploaded successfully.")

    with st.expander("📊 Preview Uploaded Data"):
        st.dataframe(df.head(), use_container_width=True)

    st.subheader("📝 Prompt Template")
    prompt = st.text_area(
        "Use {{column_name}} syntax to reference columns in your prompt.",
        height=150,
        placeholder="Classify this text: {{HozeFaaliat}}"
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("🚀 Run GPT Processing"):
            with st.spinner("Processing via OpenAI..."):
                file_bytes = uploaded_file.getvalue()
                files = {'file': (uploaded_file.name, io.BytesIO(file_bytes))}

                if ignored_file:
                    ignored_bytes = ignored_file.getvalue()
                    files['ignored_file'] = (ignored_file.name, io.BytesIO(ignored_bytes))

                data = {
                    'prompt': prompt,
                    'api_key': api_key,
                    'model': model,
                    'temperature': str(temperature),
                    'top_p': str(top_p),
                    'num_threads': str(num_threads),
                    'system_prompt': system_prompt
                }

                try:
                    response = requests.post("http://localhost:8000/process/", files=files, data=data)

                    if response.status_code == 200:
                        st.success("✅ Processing complete. Download your results below.")
                        st.download_button("📥 Download Processed CSV", response.content, file_name="output.csv")

                        log_path = response.headers.get("X-Log-Path")
                        if log_path and "error" in log_path:
                            try:
                                with open(log_path, "r", encoding="utf-8") as f:
                                    logs = f.read()
                                if logs.strip():
                                    st.error("⚠️ Some rows failed. See logs below:")
                                    st.text_area("Errors", value=logs, height=300)
                            except:
                                st.warning("Log file referenced but not accessible.")
                    else:
                        st.error(f"❌ Error: {response.status_code}")
                        st.text(response.text)

                except Exception as e:
                    st.error(f"🚨 Connection error: {e}")

    with col2:
        if st.button("🔁 Reset progress"):
            res = requests.post("http://localhost:8000/reset/")
            if res.status_code == 200:
                st.success("✅ Progress reset successfully.")
            else:
                st.error("❌ Failed to reset state.")
else:
    st.info("📎 Please upload a CSV file to begin.")
