import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient
from app.crud.order import order as crud_order
from app.crud.payment import payment as crud_payment
from app.schemas.order import OrderCreate, OrderItemCreate
from app.schemas.payment import PaymentCreate
from app.models.enums import OrderStatus, PaymentStatus

@pytest.mark.asyncio
async def test_create_checkout_session_success(client: AsyncClient, session):
    # 1. Arrange: Create a pending order in DB
    order_in = OrderCreate(
        table_number=3,
        customer_name="John Checkout",
        items=[OrderItemCreate(product_name="Pasta", quantity=2, unit_price=12.50)]
    )
    db_order = await crud_order.create(session=session, obj_in=order_in)

    mock_stripe_session = MagicMock()
    mock_stripe_session.id = "cs_test_mock_session_123"
    mock_stripe_session.url = "https://checkout.stripe.com/pay/cs_test_mock_session_123"

    payload = {
        "order_id": str(db_order.id),
        "customer_email": "john@example.com"
    }

    # 2. Act: Mock stripe_service and call endpoint
    with patch("app.api.v1.payments.stripe_service.create_checkout_session", return_value=mock_stripe_session):
        response = await client.post("/api/v1/payments/checkout-session", json=payload)

    # 3. Assert
    assert response.status_code == 201
    data = response.json()
    assert data["checkout_url"] == "https://checkout.stripe.com/pay/cs_test_mock_session_123"
    assert data["session_id"] == "cs_test_mock_session_123"

    # Verify payment record was saved in DB
    payments = await crud_payment.get_by_order_id(session=session, order_id=db_order.id)
    assert len(payments) == 1
    assert payments[0].status == PaymentStatus.pending
    assert payments[0].stripe_session_id == "cs_test_mock_session_123"


@pytest.mark.asyncio
async def test_create_checkout_session_order_not_found(client: AsyncClient):
    payload = {
        "order_id": "00000000-0000-0000-0000-000000000000",
        "customer_email": "fake@example.com"
    }
    response = await client.post("/api/v1/payments/checkout-session", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


@pytest.mark.asyncio
async def test_create_checkout_session_already_paid(client: AsyncClient, session):
    # 1. Arrange: Create order and update to 'paid'
    order_in = OrderCreate(
        table_number=4,
        items=[OrderItemCreate(product_name="Salad", quantity=1, unit_price=8.00)]
    )
    db_order = await crud_order.create(session=session, obj_in=order_in)
    await crud_order.update_status(session=session, db_obj=db_order, new_status=OrderStatus.paid)

    # 2. Act
    payload = {"order_id": str(db_order.id)}
    response = await client.post("/api/v1/payments/checkout-session", json=payload)

    # 3. Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "This order has already been paid"


@pytest.mark.asyncio
async def test_stripe_webhook_successful_payment(client: AsyncClient, session):
    # 1. Arrange: Create order and pending payment record
    order_in = OrderCreate(
        table_number=10,
        customer_name="Alice Webhook",
        items=[OrderItemCreate(product_name="Pizza", quantity=1, unit_price=15.00)]
    )
    db_order = await crud_order.create(session=session, obj_in=order_in)

    payment_in = PaymentCreate(
        order_id=db_order.id,
        amount=db_order.total_amount,
        currency="usd",
        customer_email="alice@example.com",
        stripe_session_id="cs_test_webhook_session_999"
    )
    db_payment = await crud_payment.create(session=session, obj_in=payment_in)

    # Mock Stripe Event Object
    mock_event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_webhook_session_999",
                "payment_intent": "pi_mock_intent_888"
            }
        }
    }

    # 2. Act: Send Webhook request with mocked signature verification
    with patch("app.api.v1.payments.stripe_service.construct_webhook_event", return_value=mock_event), \
         patch("app.api.v1.payments.ws_manager.broadcast_json") as mock_ws_broadcast:
        
        response = await client.post(
            "/api/v1/payments/webhook",
            json={},
            headers={"stripe-signature": "t=123,v1=mock_signature"}
        )

    # 3. Assert: Response is 200 OK
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    # Verify Payment updated to succeeded
    updated_payment = await crud_payment.get(session=session, id=db_payment.id)
    assert updated_payment.status == PaymentStatus.succeeded
    assert updated_payment.stripe_payment_intent_id == "pi_mock_intent_888"

    # Verify Order updated to paid
    updated_order = await crud_order.get(session=session, id=db_order.id)
    assert updated_order.status == OrderStatus.paid

    # Verify WebSocket broadcast was called
    mock_ws_broadcast.assert_called_once()


@pytest.mark.asyncio
async def test_stripe_webhook_invalid_signature(client: AsyncClient):
    import stripe

    # Mock signature verification error
    with patch(
        "app.api.v1.payments.stripe_service.construct_webhook_event", 
        side_effect=stripe.error.SignatureVerificationError("Invalid sig", "sig_header")
    ):
        response = await client.post(
            "/api/v1/payments/webhook",
            json={},
            headers={"stripe-signature": "bad_signature"}
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid signature"
