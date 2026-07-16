import stripe
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import get_session, User
from app.auth import get_current_user
from app.models import UserOut

stripe.api_key = settings.stripe_secret_key

router = APIRouter(prefix="/subscription", tags=["subscription"])


@router.post("/create-checkout-session")
async def create_checkout_session(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Creates a Stripe Checkout session (test mode) for upgrading to Pro."""
    customer_id = user.stripe_customer_id

    if not customer_id:
        customer = stripe.Customer.create(email=user.email, name=user.name)
        customer_id = customer["id"]
        user.stripe_customer_id = customer_id
        session.add(user)
        await session.commit()

    checkout_session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{"price": settings.stripe_price_id, "quantity": 1}],
        mode="subscription",
        success_url=f"{settings.frontend_url}/upgrade-success",
        cancel_url=f"{settings.frontend_url}/upgrade-cancelled",
        metadata={"user_email": user.email},
    )
    return {"checkout_url": checkout_session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, session: AsyncSession = Depends(get_session)):
    """Stripe calls this when a checkout session completes. Use the Stripe CLI
    (`stripe listen --forward-to localhost:8000/subscription/webhook`) to test locally."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    except Exception as e:
        # This will print the precise signature error reason in your Uvicorn terminal
        print(f"\n!!! Webhook Verification Failed: {str(e)}\n")
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    if event["type"] == "checkout.session.completed":
        stripe_session = event["data"]["object"]
        email = stripe_session.get("metadata", {}).get("user_email")
        if email:
            result = await session.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            if user:
                user.plan = "pro"
                session.add(user)
                await session.commit()

    # Handle cancellations so users drop back to free
    if event["type"] == "customer.subscription.deleted":
        customer_id = event["data"]["object"].get("customer")
        if customer_id:
            result = await session.execute(select(User).where(User.stripe_customer_id == customer_id))
            user = result.scalar_one_or_none()
            if user:
                user.plan = "free"
                session.add(user)
                await session.commit()

    return {"status": "ok"}


@router.get("/me", response_model=UserOut)
async def get_my_status(user: User = Depends(get_current_user)):
    return UserOut(
        name=user.name,
        email=user.email,
        plan=user.plan,
        questions_asked_today=user.questions_asked_today,
    )