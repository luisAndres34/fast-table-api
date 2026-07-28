from fastapi import APIRouter, HTTPException, status, Request, Header
import stripe

from app.api.dependencies import SessionDep
from app.crud.order import order as crud_order
from app.crud.payment import payment as crud_payment
from app.schemas.payment import CreateCheckoutSessionRequest, CheckoutSessionResponse, PaymentCreate
from app.models.enums import OrderStatus, PaymentStatus
from app.services.stripe_service import stripe_service
from app.services.websocket_manager import ws_manager
from app.core.email import generate_receipt_email_content
from app.core.config import settings
from app.core.tasks import enqueue_email_task
from app.core.logger import logger

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post(
    "/checkout-session", 
    response_model=CheckoutSessionResponse, 
    status_code=status.HTTP_201_CREATED
)
async def create_checkout_session(
    body: CreateCheckoutSessionRequest,
    session: SessionDep
):
    db_order = await crud_order.get(session=session, id=body.order_id)
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order not found"
        )

    if db_order.status == OrderStatus.paid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="This order has already been paid"
        )

    if db_order.status != OrderStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Cannot generate payment for order with status '{db_order.status.value}'"
        )

    if db_order.total_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Order total amount must be greater than zero"
        )

    stripe_session = stripe_service.create_checkout_session(
        order_id=str(db_order.id),
        amount=db_order.total_amount,
        currency=settings.STRIPE_CURRENCY,
        customer_email=body.customer_email,
        success_url=body.success_url,
        cancel_url=body.cancel_url
    )

    payment_in = PaymentCreate(
        order_id=db_order.id,
        amount=db_order.total_amount,
        currency=settings.STRIPE_CURRENCY,
        customer_email=body.customer_email,
        stripe_session_id=stripe_session.id
    )
    await crud_payment.create(session=session, obj_in=payment_in)

    return CheckoutSessionResponse(
        checkout_url=stripe_session.url,
        session_id=stripe_session.id
    )


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    session: SessionDep,
    stripe_signature: str | None = Header(None, alias="stripe-signature")
):
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Missing stripe-signature header"
        )

    payload = await request.body()

    try:
        event = stripe_service.construct_webhook_event(
            payload=payload, 
            sig_header=stripe_signature
        )
    except ValueError as e:
        logger.error(f"Invalid Webhook payload: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid Webhook signature: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        stripe_session = event["data"]["object"]

        if isinstance(stripe_session, dict):
            session_id = stripe_session.get("id")
            payment_intent_id = stripe_session.get("payment_intent")
        else:
            session_id = getattr(stripe_session, "id", None)
            payment_intent_id = getattr(stripe_session, "payment_intent", None)

        logger.info(f"Processing successful payment for Stripe Session ID: {session_id}")

        payment = await crud_payment.get_by_stripe_session_id_for_update(
            session=session, 
            session_id=session_id
        )

        if not payment:
            logger.warning(f"Payment session not found for Stripe Session ID: {session_id}")
            return {"status": "success"}

        if payment.status == PaymentStatus.pending:
            payment.status = PaymentStatus.succeeded
            if payment_intent_id:
                payment.stripe_payment_intent_id = payment_intent_id
            session.add(payment)

            db_order = await crud_order.get(session=session, id=payment.order_id)
            if db_order:
                db_order.status = OrderStatus.paid
                session.add(db_order)

            await session.commit()
            await session.refresh(payment)
            if db_order:
                await session.refresh(db_order)

            logger.info(f"Order ID {payment.order_id} and Payment ID {payment.id} atomically updated to paid/succeeded")

            if db_order:
                websocket_message = {
                    "event": "order_paid",
                    "data": {
                        "order_id": str(db_order.id),
                        "table_number": db_order.table_number,
                        "total_amount": str(db_order.total_amount),
                        "status": db_order.status
                    }
                }
                await ws_manager.broadcast_json(websocket_message)

                if payment.customer_email:
                    receipt_html = generate_receipt_email_content(
                        order=db_order, 
                        payment_id=str(payment.id)
                    )
                    await enqueue_email_task(
                        recipient_email=payment.customer_email,
                        subject=f"Receipt for Table #{db_order.table_number} - FastTable",
                        html_content=receipt_html
                    )

    return {"status": "success"}
