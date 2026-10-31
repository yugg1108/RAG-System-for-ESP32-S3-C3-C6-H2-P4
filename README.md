# ESP32 Docs RAG

Ask questions about ESP32-C3, C6, S3, H2 and P4 datasheets and errata. The system searches document chunks in MongoDB Atlas and uses Gemini to generate answers with source and page references.

## Setup

1. Download or clone the repository. Extract `data.zip` in the same folder as `RAG.py` and the other project files.

2. Open a terminal in that folder and install the required libraries:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Place the provided `.env` file in the project folder. It contains the MongoDB connection string and Gemini API key used by the application. The MongoDB account must have access to the populated `esp_rag.chunks` collection and its `chunk_vector_index` vector index. Atlas must also allow your network connection.

4. Ask a question:

   ```bash
   python RAG.py "What wireless protocols does ESP32-C6 support?"
   ```

   To retrieve more passages:

   ```bash
   python RAG.py "Compare ESP32-C3 and ESP32-C6 memory" --top-k 12
   ```

The first query downloads the Voyage 4 Nano embedding model. The application uses it locally to embed questions, searches Atlas for relevant chunks, and sends those passages to Gemini. Extracting the ZIP does not populate the database; the application requires the existing Atlas index. Check important specifications against the cited PDF pages.

For more details, see the [project presentation](ESP32%20Docs%20RAG%20%E2%80%94%20Hackathon%20Demo.pptx).
