import os
import subprocess
import datetime
from dotenv import load_dotenv
from langchain.chat_models import ChatVertexAI
from langchain.schema import HumanMessage

load_dotenv()

def get_commits():
    """Obtiene los mensajes de commits desde el último tag"""
    last_tag = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"]).decode().strip()
    commits = subprocess.check_output(["git", "log", f"{last_tag}..HEAD", "--pretty=format:%s"]).decode()
    return commits.splitlines(), last_tag

def generate_changelog(version, commits):
    prompt = f"""
Versión: {version}
Fecha: {datetime.date.today()}
Cambios incluidos:

{chr(10).join(f"- {c}" for c in commits)}

Redacta un changelog profesional en español con secciones:
1. Funcionalidades nuevas
2. Correcciones de errores
3. Cambios técnicos
4. Instrucciones para rollback (si aplica)
5. Consideraciones de instalación
"""

    model = ChatVertexAI(
        model="gemini-1.5-pro-preview-0409",
        project="test-cloud-gcp",
        location="us-central1",
        temperature=0.3,
        max_output_tokens=2048,
    )

    return model.invoke([HumanMessage(content=prompt)]).content

if __name__ == "__main__":
    commits, last_tag = get_commits()
    changelog = generate_changelog(last_tag, commits)
    
    with open("CHANGELOG.md", "w") as f:
        f.write(changelog)
    
    print("✅ Changelog generado exitosamente.")
