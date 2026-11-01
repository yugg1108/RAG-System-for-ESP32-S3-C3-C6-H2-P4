"""Embed ESP32 PDF pages locally and upload chunks to a new Atlas collection."""
import hashlib
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne
from pypdf import PdfReader
from RAG import ROOT, MODEL, VARIANTS, load_model


def split_text(text, size=1200, overlap=200):
    text = re.sub(r"\s+", " ", text).strip()
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            boundary = text.rfind(" ", start + size // 2, end)
            if boundary > start:
                end = boundary
        yield text[start:end]
        if end == len(text):
            break
        start = end - overlap


def main():
    load_dotenv(ROOT / '.env')
    uri = os.getenv('MONGODB_URI')
    if not uri:
        raise SystemExit('Set MONGODB_URI in .env first.')
    data_dir = ROOT / 'data'
    files = sorted(data_dir.rglob('*.pdf'))
    if not files:
        raise SystemExit('No PDFs found under data/.')
    with MongoClient(uri, serverSelectionTimeoutMS=10000) as client:
        client.admin.command('ping')
        collection = client[os.getenv('MONGODB_DATABASE', 'esp_rag')][os.getenv('MONGODB_COLLECTION', 'chunks')]
        model = load_model()
        total = 0
        for path in files:
            chip = next((part.upper() for part in path.relative_to(data_dir).parts[:-1] if part.upper() in VARIANTS), None)
            if not chip:
                print(f'Skipping {path}: no recognized chip folder')
                continue
            source = f'esp32{chip.lower()}/{path.name}'
            reader = PdfReader(path)
            rows = []
            for page_no, page in enumerate(reader.pages, 1):
                for chunk_no, text in enumerate(split_text(page.extract_text() or '')):
                    ident = hashlib.sha256(f'{source}\0{page_no}\0{chunk_no}\0{text}'.encode()).hexdigest()
                    rows.append({'_id': ident, 'source_id': source, 'chip': chip, 'chip_label': f'ESP32-{chip}',
                                 'doc_type': 'errata' if 'errata' in path.name.lower() else 'datasheet',
                                 'page': page_no, 'chunk_index': chunk_no, 'text': text, 'embedded_with': MODEL})
            print(f'{source}: {len(rows)} chunks', flush=True)
            for start in range(0, len(rows), 16):
                batch = rows[start:start + 16]
                texts = [f"{r['chip_label']} {r['doc_type']}\n{r['text']}" for r in batch]
                vectors = model.encode_document(texts, batch_size=8, normalize_embeddings=True, convert_to_numpy=True)
                if vectors.ndim != 2 or vectors.shape != (len(batch), 1024):
                    raise ValueError(f'Unexpected embedding shape: {vectors.shape}')
                for row, vector in zip(batch, vectors):
                    row['embedding'] = vector.tolist()
                collection.bulk_write([UpdateOne({'_id': row['_id']}, {'$set': {k:v for k,v in row.items() if k != '_id'}}, upsert=True) for row in batch])
                total += len(batch)
                print(f'  Uploaded {total} chunks', flush=True)
    print('Done. Create the Atlas vector index and wait for it to become ready.')


if __name__ == '__main__':
    main()
