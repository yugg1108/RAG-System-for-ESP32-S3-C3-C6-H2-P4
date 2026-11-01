"""Browser interface for the ESP32 document assistant."""
import logging
import os

import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient
import voyageai

from RAG import ROOT, answer, load_model, retrieve, source_label

logger = logging.getLogger(__name__)
load_dotenv(ROOT / ".env")
st.set_page_config(page_title="ESP32 Docs Assistant", page_icon="🔍", layout="centered")


class VoyageEmbeddingError(Exception):
    """Report the failing service without exposing API response details."""


class VoyageQueryModel:
    """Adapter for the existing retrieval function using Voyage's hosted API."""
    def __init__(self, client):
        self.client = client

    def encode_query(self, question, **kwargs):
        import numpy as np
        try:
            result = self.client.embed(
                [question], model="voyage-4-lite", input_type="query", output_dimension=1024
            )
        except Exception as exc:
            logger.error("Voyage embedding failed (%s)", type(exc).__name__)
            raise VoyageEmbeddingError("Voyage embedding failed") from None
        return np.asarray(result.embeddings[0], dtype=np.float32)


@st.cache_resource
def get_clients(uri, embedding_mode, voyage_key):
    if embedding_mode == "local":
        model = load_model()
    elif embedding_mode == "voyage_api":
        model = VoyageQueryModel(voyageai.Client(api_key=voyage_key))
    else:
        raise ValueError("EMBEDDING_MODE must be local or voyage_api")
    return MongoClient(uri, serverSelectionTimeoutMS=10000), model


st.title("ESP32 Docs Assistant")
st.caption("Answers grounded in ESP32 datasheets and errata")
st.markdown("Ask about **ESP32-C3, C6, S3, H2, or P4**. Each answer includes its supporting sources.")

with st.form("question_form"):
    question = st.text_input("Your question", placeholder="What does GPIO9 do at boot on the ESP32-C3?", max_chars=1000)
    submitted = st.form_submit_button("Ask", type="primary", use_container_width=True)

if submitted:
    if not question.strip():
        st.warning("Enter a question to get started.")
    elif not all(os.getenv(name) for name in ("MONGODB_URI", "GEMINI_API_KEY")) or (os.getenv("EMBEDDING_MODE", "local") == "voyage_api" and not os.getenv("VOYAGE_API_KEY")):
        st.error("The app is missing its database or API configuration. Please contact the app owner.")
    else:
        stage = "client initialization"
        try:
            with st.status("Preparing the assistant...", expanded=True) as progress:
                st.write("Loading the embedding model and connecting to MongoDB. The first run can take longer.")
                client, model = get_clients(os.environ["MONGODB_URI"], os.getenv("EMBEDDING_MODE", "local"), os.getenv("VOYAGE_API_KEY", ""))
                collection = client[os.getenv("MONGODB_DATABASE", "esp_rag")][os.getenv("MONGODB_COLLECTION", "chunks")]
                stage = "query embedding or MongoDB vector search"
                progress.update(label="Searching the documents...")
                st.write("Embedding the question and searching MongoDB for relevant passages.")
                results = retrieve(question.strip(), collection, model, top_k=8)
                stage = "Gemini answer generation"
                progress.update(label="Preparing the answer...")
                st.write(f"Found {len(results)} passages. Generating the answer.")
                response = answer(question.strip(), results)
                progress.update(label="Finished", state="complete", expanded=False)
            st.subheader("Answer")
            st.write(response)
            if results:
                st.subheader("Sources")
                for i, chunk in enumerate(results, 1):
                    with st.expander(f"[S{i}] {source_label(chunk)}"):
                        st.text(chunk.get("text", ""))
        except Exception as exc:
            status = getattr(exc, "code", None) or getattr(exc, "status_code", None)
            logger.error("Request failed during %s (%s, status=%s)", stage, type(exc).__name__, status if isinstance(status, int) else "unknown")
            st.error("The assistant could not complete the request. Please try again or contact the app owner.")

st.divider()
st.caption("Answers depend on the retrieved passages. Check the cited PDF pages for critical specifications.")
