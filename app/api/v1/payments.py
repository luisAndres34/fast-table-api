from fastapi import APIRouter, HTTPException, status, Request, Header
import stripe

from app.api.dependencies import SessionDep
from app.crud.order import order as crud_order
from app.crud.payment import payment as crud_payment
from app.schemas.payment import CreateCheckoutSessionRequest, CheckoutSessionResponse, PaymentCreate
from app.models.enums import OrderStatus, PaymentStatus
from app.services.stripe_service import stripe_service
from app.services.websocket_manager import ws_manager
from app.core.email import send_real_email, generate_receipt_email_content
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
    """
    Generate a Stripe Checkout Session URL for a pending Order.
    """
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
    """
    Public Stripe Webhook endpoint to process real-time payment notifications.
    Verifies cryptographic signatures before processing events.
    """
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
        session_id = stripe_session.get("id")
        payment_intent_id = stripe_session.get("payment_intent")

        logger.info(f"Processing successful payment for Stripe Session ID: {session_id}")

        payment = await crud_payment.get_by_stripe_session_id_for_update(
            session=session, 
            session_id=session_id
        )

        if payment and payment.status == PaymentStatus.pending:
            await crud_payment.update_status(
                session=session,
                db_obj=payment,
                new_status=PaymentStatus.succeeded,
                payment_intent_id=payment_intent_id
            )

            db_order = await crud_order.get(session=session, id=payment.order_id)
            if db_order:
                await crud_order.update_status(
                    session=session,
                    db_obj=db_order,
                    new_status=OrderStatus.paid
                )
                logger.info(f"Order ID {db_order.id} status successfully updated to 'paid'")

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
