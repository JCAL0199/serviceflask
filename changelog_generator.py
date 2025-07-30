import os
import datetime
import subprocess
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

def get_commits():
    last_tag = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"]).decode().strip()
    log = subprocess.check_output(["git", "log", f"{last_tag}..HEAD", "--pretty=format:%s"]).decode()
    return log.splitlines(), last_tag

def generate_changelog(version, commits):
    model = ChatVertexAI(
        model="gemini-2.5-pro",
        project="test-cloud-gcp",
        location="us-central1",
        temperature=0.4,
        max_output_tokens=2048,
    )
    
    prompt = f"""
Versión: {version}
Fecha: {datetime.date.today()}

Cambios recientes:
{chr(10).join(f"- {c}" for c in commits)}

Redacta un changelog en español claro y profesional.
Incluye secciones:
- Funcionalidades nuevas
- Correcciones
- Refactors
- Consideraciones para el despliegue
- Rollback (si aplica)
"""
    response = model.invoke([HumanMessage(content=prompt)])
    return response.content

if __name__ == "__main__":
    commits, last_tag = get_commits()
    for c in commits
        print(f"commit:---${c}")
    changelog = generate_changelog(last_tag, commits)
    
    with open("CHANGELOG.md", "w") as f:
        f.write(changelog)
    
    print("✅ Changelog generado exitosamente.")