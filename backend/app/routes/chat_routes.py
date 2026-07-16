from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from google import genai
from google.genai import types

from app.config import settings
from app.database import get_session, User
from app.auth import get_current_user
from app.models import AskRequest, AskResponse

router = APIRouter(prefix="/chat", tags=["chat"])

client = genai.Client(api_key=settings.gemini_api_key)

FREE_DAILY_LIMIT = 5

PERSONAS = {
    "free": (
        "friendly",
        "You are a friendly, encouraging Study Assistant. Explain concepts simply, "
        "using short, relatable analogies. Keep answers concise (3-5 sentences) unless "
        "the user explicitly asks for a different length. End with one short follow-up question.",
    ),
    "pro": (
        "academic",
        "You are an expert academic Study Assistant. Deliver rigorous, highly accurate, "
        "and conceptually deep explanations using precise academic terminology. "
        "CRITICAL: Always strictly respect direct formatting constraints in the user's prompt "
        "(e.g., if they ask for a 'two-line explanation', 'one sentence', or a specific format, "
        "adhere to that constraint perfectly instead of writing a massive essay). "
        "Only write long, in-depth breakdowns when the user's request is open-ended. "
        "End with a single thoughtful follow-up question to deepen understanding.",
    ),
}


@router.post("/ask", response_model=AskResponse)
async def ask_question(
    data: AskRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    plan = user.plan

    if plan == "free":
        today = str(date.today())
        count = user.questions_asked_today

        if user.last_question_date != today:
            count = 0

        if count >= FREE_DAILY_LIMIT:
            raise HTTPException(
                status_code=429,
                detail=f"Free plan limit of {FREE_DAILY_LIMIT} questions/day reached. Upgrade to Pro for unlimited access.",
            )

        user.questions_asked_today = count + 1
        user.last_question_date = today
        session.add(user)
        await session.commit()

    persona_name, system_prompt = PERSONAS[plan]

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.4,
            max_output_tokens=10000,
        ),
        contents=data.question,
    )

    return AskResponse(answer=response.text, persona_used=persona_name, plan=plan)