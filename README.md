# ESP32 document question answering

Queries existing ESP32 chunk embeddings in MongoDB Atlas and uses Gemini to answer with document and page citations. Query embeddings use the local `voyageai/voyage-4-nano` model at 1024 dimensions, matching the stored embeddings.

## Setup (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Set `MONGODB_URI` and `GEMINI_API_KEY` in `.env` or the environment. The MongoDB user needs permission to read `esp_rag.chunks` and run Atlas Vector Search. Atlas network access must allow your client. Optional settings: `MONGODB_DATABASE` (default `esp_rag`), `MONGODB_COLLECTION` (default `chunks`), `MONGODB_VECTOR_INDEX` (default `chunk_vector_index`) and `GEMINI_MODEL` (default `gemini-2.5-flash`).

The first query downloads the embedding model from Hugging Face; it requires internet access, disk space and memory. The model uses Hugging Face remote code (`trust_remote_code=True`). Gemini receives the question and retrieved text. No Voyage API key is required.

```powershell
python RAG.py "What wireless protocols does ESP32-C6 support?"
python RAG.py "Compare ESP32-C3 and ESP32-C6 memory" --top-k 12
```

The existing Atlas vector index must index `embedding` with 1024 dimensions. Questions naming variants are filtered after vector search, so a question may return fewer than `top-k` results if the initial candidates do not contain enough matching chunks. PDF extraction can lose table structure; check the cited original pages, especially electrical limits and errata. Page numbers follow the values stored in Atlas.
