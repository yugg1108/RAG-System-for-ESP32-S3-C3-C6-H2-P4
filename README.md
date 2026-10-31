# ESP32 Docs RAG

ESP32 Docs RAG is a question-answering system for ESP32-C3, C6, S3, H2 and P4 datasheets and errata. It helps users find relevant technical information across the five chip variants and provides source and page references with its answers.

The system uses Voyage 4 Nano to create question embeddings locally, MongoDB Atlas Vector Search to retrieve matching document chunks, and Gemini to generate an answer from those passages.

## Setup

1. Download or clone the repository. Extract `data.zip` in the same folder as `RAG.py` and the other project files.

2. Open a terminal in that folder and install the required libraries:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Place the provided `.env` file in the project folder. It contains the MongoDB connection string and Gemini API key used by the application. The MongoDB account must have access to the populated `esp_rag.chunks` collection and its `chunk_vector_index` vector index. Atlas must also allow your network connection.

The first query downloads the Voyage 4 Nano embedding model. Extracting the ZIP does not populate the database; the application requires the existing Atlas index. Check important specifications against the cited PDF pages.

## Run

Ask a question from the project folder:

```bash
python RAG.py "What wireless protocols does ESP32-C6 support?"
```

To retrieve more passages:

```bash
python RAG.py "Compare ESP32-C3 and ESP32-C6 memory" --top-k 12
```
