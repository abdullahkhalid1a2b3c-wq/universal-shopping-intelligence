"""AI router for FitSense conversational fit assistant, explanations, and intelligence."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.ai.models import AIRequest, ChatMessage, TaskCategory
from app.ai.orchestrator import ai_orchestrator
from app.auth import get_current_user, get_optional_user
from app.limiter import limiter
from app.supabase_client import get_supabase_client

router = APIRouter(prefix="/v1/ai", tags=["ai"])


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    brand_context: Optional[str] = None
    category_context: Optional[str] = None
    include_profile_measurements: bool = True


class ExplainRecommendationRequest(BaseModel):
    brand_name: str
    category: str
    recommended_size: str
    confidence: float
    fit_preference: str = "regular"
    measurements_comparison: Optional[Dict[str, Any]] = None
    locale: str = "en"


class ExtractSizeChartRequest(BaseModel):
    unstructured_text: str
    brand_name: Optional[str] = None
    category: Optional[str] = None


@router.get("/status")
@limiter.limit("30/minute")
async def get_ai_status(request: Request) -> Dict[str, Any]:
    """Retrieve health and availability of configured AI providers without leaking keys."""
    return ai_orchestrator.get_status()


@router.post("/chat")
@limiter.limit("20/minute")
async def chat_with_assistant(
    request: Request,
    body: ChatRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
) -> Dict[str, Any]:
    """Conversational Fit Assistant answering customer sizing and brand questions.
    
    If the user is authenticated and permitted, injects anonymous measurement summary
    strictly to personalize sizing advice without exposing PII.
    """
    user_context_str = ""
    user_id = current_user.get("id") if current_user else None

    # Fetch customer measurements if authenticated and requested
    if user_id and body.include_profile_measurements:
        client = get_supabase_client()
        if client:
            try:
                res = (
                    client.table("body_measurements")
                    .select("chest_cm, waist_cm, hip_cm, shoulder_cm, sleeve_cm, inseam_cm, height_cm")
                    .eq("user_id", user_id)
                    .limit(1)
                    .execute()
                )
                if res.data:
                    m = res.data[0]
                    measurements_str = ", ".join(
                        f"{k.replace('_cm', '')}: {v}cm" for k, v in m.items() if v is not None
                    )
                    user_context_str = f"The shopper's saved body measurements are: {measurements_str}."
            except Exception:
                user_context_str = ""

    system_prompt = (
        "You are FitSense AI Assistant — a sophisticated, helpful fashion and clothing fitting advisor for Pakistan. "
        "You assist shoppers buying from Pakistani fashion brands (such as Khaadi, Sapphire, J., Outfitters, Limelight, Breakout, Diners, etc.).\n\n"
        "Core Guidelines:\n"
        "1. Never guess or fabricate size chart numbers. If you do not know a brand's exact chart, advise the user to use the 'Find My Size' tool on that brand's page.\n"
        "2. Help shoppers understand how different Pakistani brands fit (e.g. traditional eastern kurtas often have looser chest ease, while western tees may be boxy or slim).\n"
        "3. Explain measurement terminology simply (chest vs bust, inseam vs outseam, flat measurement vs circumference).\n"
        "4. If the shopper asks what size to buy, explain that FitSense uses a zero-ML deterministic fit engine that evaluates their measurements against the brand's verified size chart, and guide them to select their brand and category.\n"
        "5. Be courteous, concise, and helpful."
    )

    if body.brand_context:
        system_prompt += f"\nCurrent Brand Context: {body.brand_context}."
    if body.category_context:
        system_prompt += f"\nCurrent Clothing Category: {body.category_context}."
    if user_context_str:
        system_prompt += f"\nCustomer Profile: {user_context_str}"

    ai_req = AIRequest(
        task_category=TaskCategory.FIT_ASSISTANT,
        messages=body.messages,
        system_prompt=system_prompt,
        temperature=0.4,
        max_tokens=600,
    )

    response = await ai_orchestrator.execute(ai_req)
    return {
        "reply": response.content,
        "provider": response.provider.value,
        "model": response.model,
        "duration_ms": response.duration_ms,
        "fallback_used": response.fallback_used,
    }


@router.post("/explain-recommendation")
@limiter.limit("30/minute")
async def explain_recommendation(
    request: Request,
    body: ExplainRecommendationRequest,
) -> Dict[str, Any]:
    """Generate a natural-language, profile-aware explanation of a deterministic fit engine recommendation."""
    comparison_summary = ""
    if body.measurements_comparison:
        parts = []
        for dim, details in body.measurements_comparison.items():
            if isinstance(details, dict):
                body_val = details.get("body")
                garment_val = details.get("garment")
                ease = details.get("ease_cm")
                parts.append(f"{dim.title()}: Body {body_val}cm vs Garment {garment_val}cm (Ease: {ease}cm)")
        comparison_summary = "; ".join(parts)

    system_prompt = (
        "You are the FitSense Explanation Engine. "
        "Your task is to explain why a specific clothing size was recommended by our deterministic sizing engine.\n\n"
        "CRITICAL RULES:\n"
        f"1. The recommended size is {body.recommended_size}. DO NOT suggest or recommend any other size as the primary choice.\n"
        f"2. Reference the brand '{body.brand_name}' and category '{body.category}'.\n"
        "3. Explain the ease (comfort room in centimeters) based on their body measurements.\n"
        f"4. The customer's fit preference is '{body.fit_preference}'. Acknowledge how this size matches their preference.\n"
        "5. Keep the explanation under 3 sentences: clear, polite, and reassuring."
    )

    user_prompt = (
        f"Brand: {body.brand_name}\n"
        f"Category: {body.category}\n"
        f"Recommended Size: {body.recommended_size}\n"
        f"Engine Confidence: {round(body.confidence * 100)}%\n"
        f"Fit Preference: {body.fit_preference}\n"
    )
    if comparison_summary:
        user_prompt += f"Dimension Breakdown: {comparison_summary}\n"

    ai_req = AIRequest(
        task_category=TaskCategory.FIT_ASSISTANT,
        messages=[ChatMessage(role="user", content=user_prompt)],
        system_prompt=system_prompt,
        temperature=0.2,
        max_tokens=300,
    )

    response = await ai_orchestrator.execute(ai_req)
    return {
        "explanation": response.content,
        "recommended_size": body.recommended_size,
        "brand_name": body.brand_name,
        "provider": response.provider.value,
        "duration_ms": response.duration_ms,
    }


@router.post("/extract-size-chart")
@limiter.limit("15/minute")
async def extract_size_chart(
    request: Request,
    body: ExtractSizeChartRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Parse unstructured text from a brand size chart into structured JSON candidate format for retailer review."""
    system_prompt = (
        "You are the FitSense Size Chart Intelligence Assistant. "
        "Extract size chart data from the provided text into a clean JSON structure.\n"
        "Return ONLY a JSON object with this exact shape:\n"
        "{\n"
        '  "measured_as": "circumference" or "flat",\n'
        '  "unit": "cm" or "in",\n'
        '  "sizes": [\n'
        '    {"size_label": "S", "chest": 98.0, "waist": 82.0, "shoulder": 42.0, "length": 68.0},\n'
        '    {"size_label": "M", "chest": 104.0, "waist": 88.0, "shoulder": 44.0, "length": 70.0}\n'
        "  ]\n"
        "}\n"
        "Rules:\n"
        "1. Standardize size labels (XS, S, M, L, XL, XXL or numbers 38, 40, 42).\n"
        "2. All numeric values must be numbers, not strings.\n"
        "3. Do not invent numbers. If a measurement is missing, omit the key or set to null."
    )

    ai_req = AIRequest(
        task_category=TaskCategory.SIZE_CHART_INTELLIGENCE,
        messages=[ChatMessage(role="user", content=body.unstructured_text)],
        system_prompt=system_prompt,
        temperature=0.1,
        max_tokens=1500,
        json_mode=True,
    )

    response = await ai_orchestrator.execute(ai_req)
    return {
        "candidate_data": response.structured_data or {},
        "provider": response.provider.value,
        "duration_ms": response.duration_ms,
    }
