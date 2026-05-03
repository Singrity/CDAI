from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Literal

app = FastAPI(
    title="CDAI Calculator",
    description="Калькулятор Clinical Disease Activity Index для ревматоидного артрита",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="front/static"), name="static")
templates = Jinja2Templates(directory="front/templates")


class CDAIInput(BaseModel):
    tjc28: int = Field(..., ge=0, le=28, description="Количество болезненных суставов из 28 (ЧБС28)")
    sjc28: int = Field(..., ge=0, le=28, description="Количество отёчных суставов из 28 (ОПС28)")
    pt_ga: float = Field(..., ge=0.0, le=10.0, description="Оценка состояния пациентом (ВАШ 0-10)")
    ph_ga: float = Field(..., ge=0.0, le=10.0, description="Оценка состояния врачом (ВАШ 0-10)")


class CDAIResult(BaseModel):
    score: float
    category: Literal["remission", "low", "moderate", "high"]
    category_ru: str
    interpretation: str
    recommendation: str


def interpret_cdai(score: float) -> dict:
    if score <= 2.8:
        return {
            "category": "remission",
            "category_ru": "Ремиссия",
            "interpretation": "Активность заболевания отсутствует или минимальна.",
            "recommendation": "Рассмотреть возможность снижения дозы или отмены БПВП/ ГИБП при стабильной ремиссии >6 мес."
        }
    elif score <= 10.0:
        return {
            "category": "low",
            "category_ru": "Низкая активность",
            "interpretation": "Контролируемая активность, но целевые показатели не достигнуты.",
            "recommendation": "Продолжить текущую терапию, усилить мониторинг, рассмотреть коррекцию при отсутствии динамики через 3-6 мес."
        }
    elif score <= 22.0:
        return {
            "category": "moderate",
            "category_ru": "Умеренная активность",
            "interpretation": "Заболевание активно, требуется оптимизация лечения.",
            "recommendation": "Изменить схему БПВП, добавить/заменить ГИБП/таргетный синтетический препарат. Контроль через 1-3 мес."
        }
    else:
        return {
            "category": "high",
            "category_ru": "Высокая активность",
            "interpretation": "Тяжёлое обострение, высокий риск прогрессирования и системных осложнений.",
            "recommendation": "Срочная модификация терапии (комбинированные БПВП или ГИБП/таргетные препараты). Госпитализация при наличии внесуставных проявлений."
        }


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(name="index.html", request=request)


@app.post("/cdai/calculate", response_model=CDAIResult, tags=["Расчёт"])
def calculate_cdai(data: CDAIInput):
    score = data.tjc28 + data.sjc28 + data.pt_ga + data.ph_ga
    result = interpret_cdai(score)
    return {"score": round(score, 1), **result}


@app.get("/cdai/info", tags=["Справка"])
def get_info():
    return {
        "name": "CDAI (Clinical Disease Activity Index)",
        "disease": "Ревматоидный артрит",
        "components": "ЧБС28 + ОПС28 + ВАШ пациента (0-10) + ВАШ врача (0-10)",
        "units_ru": "Суставы: штуки. ВАШ: баллы 0-10 (в РФ часто измеряют в мм 0-100, деление на 10 даёт шкалу 0-10)",
        "thresholds": "≤2.8 ремиссия | 2.9-10 низкая | 10.1-22 умеренная | >22 высокая",
        "guidelines": "EULAR 2022, Ассоциация ревматологов России 2021/2023"
    }