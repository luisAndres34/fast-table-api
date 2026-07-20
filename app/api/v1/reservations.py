from fastapi import APIRouter, BackgroundTasks, status
from app.api.dependencies import SessionDep
from app.models.reservation import Reservation
from app.schemas.reservation import ReservationCreate, ReservationPublic
from app.core.email import send_real_email

router = APIRouter(prefix="/reservations", tags=["reservations"])

def generate_reservation_email_content(name: str, date: str) -> str:
    return f"""
    <html>
        <body>
            <h2>Reservation Confirmed!</h2>
            <p>Hello <b>{name}</b>,</p>
            <p>Your table reservation for <b>{date}</b> has been successfully processed.</p>
            <p>We look forward to serving you!</p>
            <br>
            <p>Best regards,<br>The FastTable Team</p>
        </body>
    </html>
    """

@router.post("/", response_model=ReservationPublic, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    reservation_in: ReservationCreate, 
    background_tasks: BackgroundTasks, 
    session: SessionDep
):

    db_reservation = Reservation(**reservation_in.model_dump())
    session.add(db_reservation)
    await session.commit()
    await session.refresh(db_reservation)

    email_content = generate_reservation_email_content(
        name=db_reservation.customer_name,
        date=db_reservation.reservation_date.strftime("%Y-%m-%d %H:%M")
    )

    background_tasks.add_task(
        send_real_email,
        recipient_email=db_reservation.customer_email,
        subject="Your Table Reservation Confirmation",
        html_content=email_content
    )

    return db_reservation
