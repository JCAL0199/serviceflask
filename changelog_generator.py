import subprocess

tag = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"]).decode().strip()
log = subprocess.check_output(["git", "log", f"{tag}..HEAD", "--pretty=format:* %s"]).decode()

with open("CHANGELOG.md", "w") as f:
    f.write(f"# Cambios desde {tag}\n\n")
    f.write(log)
