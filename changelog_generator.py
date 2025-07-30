import subprocess

# Obtener los dos tags más recientes ordenados por fecha
tags = subprocess.check_output(["git", "tag", "--sort=-creatordate"]).decode().split()
if len(tags) < 2:
    raise Exception("No hay suficientes tags para generar changelog")

prev_tag = tags[1]  # tag anterior
curr_tag = tags[0]  # tag actual

# Obtener commits entre prev_tag y curr_tag
log = subprocess.check_output(["git", "log", f"{prev_tag}..{curr_tag}", "--pretty=format:* %s"]).decode()

with open("CHANGELOG.md", "w") as f:
    f.write(f"# Cambios desde {prev_tag} hasta {curr_tag}\n\n")
    f.write(log)
