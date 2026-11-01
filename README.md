# ESP32 Docs RAG

An AI assistant for exploring ESP32-C3, C6, S3, H2 and P4 datasheets and errata. Ask a question and receive an answer grounded in retrieved documentation, with source and page references.

**[Open the live app](https://rag-system-for-esp32-s3-c3-c6-h2-p4-fqymbvkvsdruyxtafamr76.streamlit.app/)**

The first question may take longer while the app loads its embedding model. For the project architecture and demo, see the [presentation](ESP32%20Docs%20RAG%20%E2%80%94%20Hackathon%20Demo.pptx).

## How it works

1. Voyage 4 Nano embeds the question locally. The web app can optionally use the Voyage API instead.
2. MongoDB Atlas Vector Search retrieves relevant document chunks and their metadata.
3. Gemini generates an answer from the retrieved passages and cites its sources.

## Run locally

Install the dependencies in the project folder:

```bash
python -m pip install -r requirements.txt
```

Create a `.env` file in the same folder:

```dotenv
MONGODB_URI="your_atlas_connection_string"
GEMINI_API_KEY="your_gemini_api_key"
```

The Atlas database must already contain the embedded document chunks and a Vector Search index. By default, the app uses database `esp_rag`, collection `chunks`, and index `chunk_vector_index`, with 1024-dimensional vectors in the `embedding` field. The database user needs read access and Atlas must allow the client connection. The query code does not ingest PDFs or create the index.

To run the web app:

```bash
python -m streamlit run app.py
```

To ask a question in the terminal:

```bash
python RAG.py "What wireless protocols does ESP32-C6 support?"
```

## Configuration

The web app defaults to local Voyage 4 Nano embeddings. Its first run downloads the model and may be slow on a CPU. To use the hosted Voyage API for web app questions, add the following to `.env` or your hosting platform's secrets:

```dotenv
EMBEDDING_MODE="voyage_api"
VOYAGE_API_KEY="your_voyage_api_key"
```

The hosted mode uses `voyage-4-lite` with 1024 dimensions and is subject to API limits and charges. The command-line script continues to use the local model. Optional settings are `GEMINI_MODEL` (default `gemini-3.8-flash`), `MONGODB_DATABASE`, `MONGODB_COLLECTION` and `MONGODB_VECTOR_INDEX`.

Keep API keys and connection strings private; do not commit `.env` to GitHub. Answers depend on the available indexed passages, and PDF tables may be extracted imperfectly. Verify important specifications in the cited documents.
