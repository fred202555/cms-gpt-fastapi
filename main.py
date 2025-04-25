from fastapi import FastAPI, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
import openai, os, paramiko
from slugify import slugify

app = FastAPI()

# Configuration Cloudways
HOST = "155.138.157.201"
PORT = 22
USERNAME = "mastercms"
PASSWORD = os.getenv("CLOUDWAYS_SFTP")
REMOTE_BASE_DIR = "/home/mastercloud/apps/zxsxanhphuk/public_html"

# Vérification de la variable
if not PASSWORD:
    raise ValueError("⛔ Variable d’environnement CLOUDWAYS_SFTP non définie")

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/", response_class=HTMLResponse)
def upload_form():
    return '''
    <html><body>
    <h2>🧘 Générateur d’article ZenExamen</h2>
    <form action="/generate" enctype="multipart/form-data" method="post">
        <input name="file" type="file">
        <button type="submit">Lancer la génération</button>
    </form>
    </body></html>
    '''

def mkdir_p(sftp, remote_directory):
    """Crée les dossiers distants de façon récursive"""
    dirs = remote_directory.strip("/").split("/")
    path = ""
    for folder in dirs:
        path += f"/{folder}"
        try:
            sftp.stat(path)
        except FileNotFoundError:
            sftp.mkdir(path)

@app.post("/generate")
def generate(file: UploadFile):
    lines = file.file.read().decode("utf-8").splitlines()

    def streamer():
        transport = paramiko.Transport((HOST, PORT))
        transport.connect(username=USERNAME, password=PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)

        for title in lines:
            try:
                slug = slugify(title)
                prompt = f"Rédige un article HTML SEO de 1500 mots. Titre : {title}. Inclut <title>, meta description, <h2>, paragraphes, et une conclusion."

                yield f"\n---\n✨ {title}"

                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )

                if not response.choices:
                    yield f"\n❌ Pas de réponse de GPT pour : {title}"
                    continue

                html = response.choices[0].message.content.strip()

                if not html:
                    yield f"\n❌ Contenu vide généré pour : {title}"
                    continue

                tmp_path = f"/tmp/{slug}.html"
                with open(tmp_path, "w", encoding="utf-8") as tmp:
                    tmp.write(html)

                remote_path = f"{REMOTE_BASE_DIR}/articles/{slug}/"
                mkdir_p(sftp, remote_path)

                if os.path.exists(tmp_path):
                    sftp.put(tmp_path, f"{remote_path}index.html")
                    yield f"\n✅ Publié : https://zenexamen.com/articles/{slug}/"
                else:
                    yield f"\n❌ Fichier temporaire introuvable pour : {title}"

            except Exception as e:
                yield f"\n❌ Erreur : {title} → {e}"

        sftp.close()
        transport.close()

    return StreamingResponse(streamer(), media_type="text/plain")
