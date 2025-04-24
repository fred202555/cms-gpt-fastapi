from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

class ArticleRequest(BaseModel):
    sujet: str
    mot_cle: str

@app.post("/generer-article")
def generer_article(data: ArticleRequest):
    try:
        prompt = f'''
        Rédige un article SEO de 1500 mots sur le sujet suivant : {data.sujet}.
        Le mot-clé principal à inclure est : {data.mot_cle}.
        Structure l'article avec un titre accrocheur, une introduction, des H2, des H3, une conclusion, et une FAQ.
        Respecte un ton bienveillant, accessible aux étudiants stressés. Utilise du HTML.
        '''
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un rédacteur SEO expert"},
                {"role": "user", "content": prompt}
            ]
        )
        return {"html": completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

