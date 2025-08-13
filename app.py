# app.py
import streamlit as st
import requests

st.set_page_config(page_title="NL→Code", layout="centered")
st.title("💻 Natural Language → Code Generator")

prompt = st.text_area("Write your instruction (e.g., 'Write a Python function to check prime')", height=140)

if st.button("Generate Code"):
    if not prompt.strip():
        st.warning("Enter an instruction first.")
    else:
        with st.spinner("Generating..."):
            try:
                res = requests.post("http://127.0.0.1:8000/generate", json={"prompt": prompt}, timeout=60)
                if res.status_code == 200:
                    code = res.json().get("code", "")
                    st.subheader("Generated Code")
                    st.code(code, language="python")
                else:
                    st.error(f"Server error: {res.status_code}")
            except Exception as e:
                st.error(f"Request failed: {e}")
