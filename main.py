
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
import openai
import os

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/", response_class=HTMLResponse)
def home():
    return """<!DOCTYPE html>
<html>
<head><title>ZenExamen Générateur</title></head>
<body>
<h2>Interface disponible à <a href='/form'>/form</a></h2>
</body></html>"""

@app.get("/form", response_class=HTMLResponse)
def form():
    return '''
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>ZenExamen - Générateur d’article</title>
        </head>
        <body>
            <h1>🧘 Générateur d’article ZenExamen</h1>
            <form action="/generate" method="post">
                <label for="keyword">Mot-clé :</label>
                <input type="text" id="keyword" name="keyword" required>
                <button type="submit">Générer</button>
            </form>
        </body>
        </html>
    '''

@app.post("/generate")
def generate(keyword: str = Form(...)):
    slug = keyword.lower().replace(" ", "-")
    prompt = f"Rédige un article SEO de 1500 mots en HTML sur le thème : {keyword}. L’article doit être structuré avec titre, meta description, balises <h2>, et contenu fluide et humain. Pas d’images."
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    article_content = response.choices[0].message.content
    
    # Sauvegarde locale pour téléchargement
    filename = f"{slug}.html"
    filepath = f"/tmp/{filename}"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(article_content)

    return FileResponse(filepath, media_type='text/html', filename=filename)
