# file: app/__init__.py
# (kept intentionally empty; marks "app" as a package)

# file: app/ingest/__init__.py
# (kept intentionally empty; marks "app.ingest" as a package)

# file: app/ingest/extract_text.py
# encoding: utf-8
"""
Extract text + metadata from PDFs and push chunks to Qdrant.
Why: dual-mode import so it runs via `python -m app.ingest.extract_text` or `python app/ingest/extract_text.py`.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

from qdrant_client.http.models import Distance, SparseVectorParams, VectorParams
from markitdown import MarkItDown

# --- dual-mode import: module or script ---------------------------------------
if __package__ in (None, ""):
    # When run as `python app/ingest/extract_text.py`
    REPO_ROOT = Path(__file__).resolve().parents[2]
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from app.ingest.embed_qdrant import EmbeddingSelfQuery  # type: ignore
else:
    # When run as `python -m app.ingest.extract_text`
    from .embed_qdrant import EmbeddingSelfQuery
# ------------------------------------------------------------------------------

md = MarkItDown()


def process_pdf_file(file_path: str, embedder: EmbeddingSelfQuery) -> List[Dict[str, Any]]:
    """
    Usa o LLM do embedder para extrair metadados/chunks e retorna lista de {text, metadata}.
    """
    pdf_name = os.path.basename(file_path)
    result = md.convert(str(file_path))
    text_content = result.text_content or ""

    prompt = f"""
Você é um especialista jurídico do Tribunal de Contas de Minas Gerais.
Analise o texto abaixo e extraia:

1️⃣ Metadados:
- num_sumula: número da súmula (ex: 71)
- data_status: última data (formato DD/MM/AA)
- data_status_ano: última data (formato AAAA)
- status_atual: último status (VIGENTE, REVOGADA, ALTERADA, etc.)
- pdf_name: nome do arquivo PDF

2️⃣ Chunks (máximo de 3):
- conteudo_principal: texto vigente até antes de 'REFERÊNCIAS NORMATIVAS'
- referencias_normativas: texto após 'REFERÊNCIAS NORMATIVAS:' até antes de 'PRECEDENTES:'
- precedentes: texto após 'PRECEDENTES:' até o final

Retorne **somente** um JSON no formato:
{{
  "metadados": {{
    "num_sumula": "...",
    "data_status": "...",
    "data_status_ano": "...",
    "status_atual": "...",
    "pdf_name": "{pdf_name}"
  }},
  "chunks": {{
    "conteudo_principal": "...",
    "referencias_normativas": "...",
    "precedentes": "..."
  }}
}}

Texto da súmula:
{text_content[:12000]}
"""

    try:
        response = embedder.llm.invoke(prompt)
        json_text = re.sub(r"```[\w-]*", "", response.content).replace("```", "").strip()
        data = json.loads(json_text)

        metadados = data.get("metadados", {})
        chunks = data.get("chunks", {})

        processed: List[Dict[str, Any]] = []
        for idx, (tipo, texto) in enumerate(chunks.items()):
            if not texto or idx >= 3:
                continue
            metadata = {
                "num_sumula": metadados.get("num_sumula"),
                "data_status": metadados.get("data_status"),
                "data_status_ano": metadados.get("data_status_ano"),
                "status_atual": metadados.get("status_atual"),
                "pdf_name": metadados.get("pdf_name", pdf_name),
                "chunk_type": tipo,
                "chunk_index": idx,
            }
            processed.append({"text": texto.strip(), "metadata": metadata})

        return processed

    except Exception as e:
        print(f"⚠️ Erro ao processar {pdf_name}: {e}")
        return []


def main(collection: str = "sumulas_jornada", pasta_pdfs: str | None = None) -> None:
    # Use repo-root/sumulas por padrão (why: execução a partir de qualquer CWD)
    repo_root = Path(__file__).resolve().parents[2]
    pdf_dir = Path(pasta_pdfs) if pasta_pdfs else repo_root / "sumulas"

    embedder = EmbeddingSelfQuery()

    if not embedder.client.collection_exists(collection_name=collection):
        embedder.client.create_collection(
            collection_name=collection,
            vectors_config={"text-dense": VectorParams(size=3072, distance=Distance.COSINE)},
            sparse_vectors_config={"text-sparse": SparseVectorParams()},
        )
        print(f"Coleção '{collection}' criada.")
    else:
        print(f"Coleção '{collection}' já existe.")

    vector_store = embedder.get_qdrant_vector_store(collection)
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"Nenhum PDF encontrado na pasta: {pdf_dir}")
        return

    total_chunks = 0
    for pdf_file in pdf_files:
        chunks = process_pdf_file(str(pdf_file), embedder)
        if not chunks:
            continue
        texts = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        vector_store.add_texts(texts=texts, metadatas=metadatas)
        total_chunks += len(chunks)

    print(f"✅ {len(pdf_files)} PDFs processados. {total_chunks} chunks inseridos no Qdrant.")


if __name__ == "__main__":
    # CLI args (optional): collection, pasta_pdfs
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default="sumulas_jornada")
    parser.add_argument("--pasta_pdfs", default=None)
    args = parser.parse_args()

    main(collection=args.collection, pasta_pdfs=args.pasta_pdfs)


# file: app/ingest/embed_qdrant.py
# unchanged; included for completeness
from qdrant_client import QdrantClient
from app.utils.settings import settings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_qdrant import QdrantVectorStore


class EmbeddingSelfQuery:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            timeout=120,
        )
        self.model = OpenAIEmbeddings(model="text-embedding-3-large")

    def get_qdrant_vector_store(self, collection_name: str) -> QdrantVectorStore:
        return QdrantVectorStore(
            client=self.client,
            collection_name=collection_name,
            embedding=self.model,
            sparse_vector_name="text-sparse",
            vector_name="text-dense",
        )


# file: .vscode/launch.json  (optional, helps F5 run as module)
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run extract (module)",
      "type": "python",
      "request": "launch",
      "module": "app.ingest.extract_text",
      "justMyCode": true,
      "args": ["--collection", "sumulas_jornada"]
    }
  ]
}
