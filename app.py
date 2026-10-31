"""Browser interface for the ESP32 document assistant."""
import logging
import os

import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient
import voyageai

from RAG import ROOT, answer, retrieve, source_label

logger = logging.getLogger(__name__)
load_dotenv(ROOT / ".env")
st.set_page_config(page_title="ESP32 Docs Assistant", page_icon="🔍", layout="centered")


class VoyageQueryModel:
    """Adapter for the existing retrieval function using Voyage's hosted API."""
    def __init__(self, client):
        self.client = client

    def encode_query(self, question, **kwargs):
        import numpy as np
        result = self.client.embed(
            [question], model="voyage-4-lite", input_type="query", output_dimension=1024
        )
        return np.asarray(result.embeddings[0], dtype=np.float32)


@st.cache_resource
def get_clients(uri, voyage_key):
    return MongoClient(uri, serverSelectionTimeoutMS=10000), VoyageQueryModel(voyageai.Client(api_key=voyage_key))


st.title("ESP32 Docs Assistant")
st.caption("Answers grounded in ESP32 datasheets and errata")
st.markdown("Ask about **ESP32-C3, C6, S3, H2, or P4**. Each answer includes its supporting sources.")

with st.form("question_form"):
    question = st.text_input("Your question", placeholder="What does GPIO9 do at boot on the ESP32-C3?", max_chars=1000)
    submitted = st.form_submit_button("Ask", type="primary", use_container_width=True)

if submitted:
    if not question.strip():
        st.warning("Enter a question to get started.")
    elif not all(os.getenv(name) for name in ("MONGODB_URI", "VOYAGE_API_KEY", "GEMINI_API_KEY")):
        st.error("The app is missing its database or API configuration. Please contact the app owner.")
    else:
        stage = "client initialization"
        try:
            with st.spinner("Searching the documentation and preparing an answer…"):
                client, model = get_clients(os.environ["MONGODB_URI"], os.environ["VOYAGE_API_KEY"])
                collection = client[os.getenv("MONGODB_DATABASE", "esp_rag")][os.getenv("MONGODB_COLLECTION", "chunks")]
                stage = "Voyage embedding or MongoDB vector search"
                results = retrieve(question.strip(), collection, model, top_k=8)
                stage = "Gemini answer generation"
                response = answer(question.strip(), results)
            st.subheader("Answer")
            st.write(response)
            if results:
                st.subheader("Sources")
                for i, chunk in enumerate(results, 1):
                    with st.expander(f"[S{i}] {source_label(chunk)}"):
                        st.text(chunk.get("text", ""))
        except Exception as exc:
            logger.error("Request failed during %s (%s)", stage, type(exc).__name__)
            st.error("The assistant could not complete the request. Please try again or contact the app owner.")

st.divider()
st.caption("Answers depend on the retrieved passages. Check the cited PDF pages for critical specifications.")
