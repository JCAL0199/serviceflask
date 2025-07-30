import os
import datetime
import subprocess
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

def get_commits():
    # Obtener los dos tags más recientes ordenados por fecha
    tags = subprocess.check_output(["git", "tag", "--sort=-creatordate"]).decode().split()
    if len(tags) < 2:
        raise Exception("No hay suficientes tags para generar changelog")
    prev_tag = tags[1]  # tag anterior
    curr_tag = tags[0]  # tag actual

    # Obtener commits entre prev_tag y curr_tag
    log = subprocess.check_output(["git", "log", f"{prev_tag}..{curr_tag}", "--pretty=format:* %s"]).decode()
    return log, tags[0]

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

Optimiza el texto pasado en los cambios recientes, ademas de ponerlos y separar el texto original y lo optmizado.
"""
    response = model.invoke([HumanMessage(content=prompt)])
    return response.content

if __name__ == "__main__":
    commits, last_tag = get_commits()
    changelog = generate_changelog(last_tag, commits)
    
    with open("CHANGELOG.md", "w") as f:
        f.write(changelog)
    
    print("✅ Changelog generado exitosamente.")