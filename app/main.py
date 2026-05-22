import json, pathlib
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from openai import AsyncOpenAI
from app.config import settings

app = FastAPI()
client = AsyncOpenAI(api_key=settings.openai_api_key)
BASE = pathlib.Path(__file__).parent

class GenerateRequest(BaseModel):
    position: str
    company: str
    cover_letter: str = ""

@app.get("/")
async def root():
    return FileResponse(BASE / "static/index.html")

@app.post("/generate")
async def generate(req: GenerateRequest):
    cl_section = f"\n\n지원자 자소서:\n{req.cover_letter}" if req.cover_letter.strip() else ""

    resp = await client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {
                "role": "system",
                "content": "당신은 대기업 채용 면접관입니다. 실제 면접에서 나올 법한 예리한 질문을 생성하고 JSON으로만 응답합니다."
            },
            {
                "role": "user",
                "content": f"""지원 직무: {req.position}
회사: {req.company}{cl_section}

위 정보를 바탕으로 실제 면접에서 나올 법한 예상 질문 10개를 생성해주세요.
카테고리: 직무역량 / 인성 / 상황판단 / 자소서기반 / 회사이해

다음 JSON 형식으로만 응답:
{{
    "questions": [
        {{
            "question": "질문 내용",
            "category": "직무역량",
            "tip": "이렇게 답변하면 좋습니다: 구체적인 팁"
        }}
    ]
}}"""
            }
        ],
        response_format={"type": "json_object"}
    )
    return JSONResponse(json.loads(resp.choices[0].message.content))
