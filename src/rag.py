import os
from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

KB_DIR = Path(__file__).parent.parent / "knowledge_base"
CHROMA_DIR = Path(__file__).parent.parent / ".chroma_db"

_vectorstore: Chroma | None = None


def _load_kb_documents() -> list[Document]:
    docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    for md_file in sorted(KB_DIR.glob("*.md")):
        loader = TextLoader(str(md_file), encoding="utf-8")
        raw = loader.load()
        chunks = splitter.split_documents(raw)
        for chunk in chunks:
            chunk.metadata["source"] = md_file.name
        docs.extend(chunks)
    return docs


def get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    if CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir()):
        _vectorstore = Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=embeddings,
            collection_name="autovoice_kb",
        )
    else:
        CHROMA_DIR.mkdir(exist_ok=True)
        docs = _load_kb_documents()
        _vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory=str(CHROMA_DIR),
            collection_name="autovoice_kb",
        )

    return _vectorstore


def search_kb(query: str, k: int = 4) -> list[dict]:
    vs = get_vectorstore()
    results = vs.similarity_search_with_relevance_scores(query, k=k)
    return [
        {
            "source": doc.metadata.get("source", "unknown"),
            "content": doc.page_content,
            "relevance_score": round(score, 3),
        }
        for doc, score in results
    ]


def rebuild_vectorstore() -> None:
    global _vectorstore
    import shutil
    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)
    _vectorstore = None
    get_vectorstore()
    print("Vector store rebuilt successfully.")
