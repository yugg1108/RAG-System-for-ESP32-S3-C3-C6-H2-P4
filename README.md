# ESP32 Docs RAG

A retrieval-augmented question-answering system for ESP32-C3, C6, S3, H2 and P4 datasheets and errata. It searches document chunks in MongoDB Atlas and asks Gemini to answer from the retrieved passages, with source and page citations.

Built by Team Complex for the MongoDB Student Hackathon (SVNIT). For the architecture, demo and future ideas, see the [project presentation](ESP32%20Docs%20RAG%20%E2%80%94%20Hackathon%20Demo.pptx).

## How it works

1. Voyage 4 Nano generates a 1024-dimensional embedding for the question locally.
2. MongoDB Atlas Vector Search retrieves relevant chunks from `esp_rag.chunks`. Each chunk stores its text, embedding and source metadata.
3. Gemini generates an answer from those passages and cites them as `[S1]`, `[S2]`, etc. The CLI prints the corresponding source and page details.

## Setup

1. Clone or download this repository. Extract `data.zip` **in the same folder as the other project files**, such as `RAG.py` and `requirements.txt`. The extracted PDFs are available for checking citations. The query script searches the existing Atlas index; extracting the ZIP does not create or populate that index.

2. Create a virtual environment and install all libraries from `requirements.txt`:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

   On macOS/Linux, activate with `source .venv/bin/activate` instead.

3. Create a `.env` file in the project folder:

   ```dotenv
   MONGODB_URI=your_mongodb_atlas_connection_string
   GEMINI_API_KEY=your_gemini_api_key
   ```

   Use an Atlas database already populated with the document chunks. The default database is `esp_rag`, collection is `chunks`, and vector index is `chunk_vector_index` on the 1024-dimensional `embedding` field. The Atlas user must have read access and the client must be allowed by Atlas network settings. An empty Atlas database will not work: this repository's query script does not ingest PDFs.

   Optionally set `MONGODB_DATABASE`, `MONGODB_COLLECTION`, `MONGODB_VECTOR_INDEX` or `GEMINI_MODEL` in `.env`. Gemini defaults to `gemini-2.5-flash`. Keep `.env` private and out of Git.

4. Ask a question from the project folder:

   ```powershell
   python RAG.py "What wireless protocols does ESP32-C6 support?"
   python RAG.py "Compare ESP32-C3 and ESP32-C6 memory" --top-k 12
   ```

The first query downloads the local embedding model from Hugging Face and requires internet access, disk space and memory. The model uses `trust_remote_code=True`. Gemini receives the question and retrieved passages. A Voyage API key is not required for local embeddings.

## Limitations

Answers depend on the indexed documents and retrieved passages. Variant filtering happens after vector search, so fewer than the requested number of chunks may be returned. PDF tables and section labels can be imperfect; verify important specifications against the cited original pages. Page numbers reflect the metadata stored in Atlas.
