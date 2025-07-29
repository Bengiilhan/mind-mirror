# backend/analyze.py
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Body

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter()

@router.post("/")
def analyze_entry(text: str = Body(..., embed=True)):
    try:
        prompt = f"""
Aşağıdaki metin bir kişinin günlük yazısıdır. Lütfen bu metni bilişsel davranışçı terapi (BDT) ilkelerine göre analiz et.

1. Metindeki dikkat çeken olumsuz düşünceleri tespit et (en fazla 5 adet).
2. Her düşünce için:
    - Çarpıtma türünü belirt (örnek: felaketleştirme, zihin okuma, genelleme).
    - İlgili cümleyi yaz.
    - Kısa bir açıklama yap (neden bu çarpıtma türüne girdiğini anlat).
    - Daha sağlıklı bir alternatif düşünce öner.

🔴 Cevabı mutlaka aşağıdaki JSON formatında ver:

```json
{{
  "distortions": [
    {{
      "type": "çarpıtma_türü",
      "sentence": "ilgili_cümle",
      "explanation": "neden bu çarpıtma olduğuna dair açıklama",
      "alternative": "daha sağlıklı alternatif düşünce"
    }}
  ]
}}

Metin: \"\"\"{text}\"\"\"
"""

        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
)

        content = response.choices[0].message.content.strip()

        # JSON bloğunu ayıkla
        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        json_data = content[json_start:json_end]

        try:
            parsed = json.loads(json_data)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="GPT geçerli bir JSON döndürmedi.")

        return parsed

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
