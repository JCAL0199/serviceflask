import os
import datetime
from pathlib import Path
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings


from google.cloud import storage

load_dotenv()

# ---------- CONFIG ----------
REPO_PATH = Path("https://github.com/JCAL0199/serviceflask")
PROMPT_PATH = Path("prompts/readme_prompt.j2")
OUTPUT_FILE = Path("README_GEMINI.md")
BUCKET_NAME = "bucket-changelog"
PROJECT = "test-cloud-gcp"
LOCATION = "us-central1"
MODEL_NAME = "gemini-2.5-pro"
EXCLUDED_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules"}
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "prompts")

# ---------- LOAD FILES ----------
def load_repo_docs():
    docs = []
    for path in Path("repo").rglob("*"):
        if any(ex in path.parts for ex in EXCLUDED_DIRS):
            continue

        if path.is_file() and path.suffix in {".py", ".md", ".yml", ".yaml", ".json", ".ts", ".html", ".css"}:
            try:
                loader = TextLoader(str(path), encoding="utf-8")
                docs.extend(loader.load())
            except Exception as e:
                print(f"⚠️ Error al cargar {path}: {e}")
    return docs

# ---------- RAG PROCESS ----------
def generate_document(docs):
    # Embedding + RAG
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vs = Chroma.from_documents(docs, embeddings, persist_directory=".chroma")
    retriever = vs.as_retriever()

    # Cargar plantilla
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("readme_prompt.j2")
    context_chunks = retriever.get_relevant_documents("describe el proyecto, archivos. funciones, clases, metodos")
    flat_context = "\n".join([doc.page_content for doc in context_chunks])
    prompt = template.render(context=flat_context)

    # LLM
    model = ChatVertexAI(
        model_name=MODEL_NAME,
        temperature=0.4,
        max_output_tokens=2048,
        project=PROJECT,
        location=LOCATION,
    )

    return model.invoke([HumanMessage(content=prompt)]).content

# ---------- GCS UPLOAD ----------
def upload_to_gcs(local_path, bucket_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob_name = f"docs/{local_path.name}"
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_path)
    #blob.make_public()
    print(f"📤 Archivo subido a GCS: {blob.public_url}")
    return blob.public_url

# ---------- MAIN ----------
if __name__ == "__main__":
    docs = load_repo_docs()
    print(f"📚 {len(docs)} documentos cargados.")
    content = generate_document(docs)

    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"✅ Documento generado: {OUTPUT_FILE}")

    upload_to_gcs(OUTPUT_FILE, BUCKET_NAME)
