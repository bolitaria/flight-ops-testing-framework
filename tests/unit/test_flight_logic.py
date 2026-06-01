import pytest
from src.flight_service.main import book_seat, flights_db, Flight

@pytest.mark.unit
@pytest.mark.asyncio
async def test_book_seat_reduces_availability():
    """Unit test: booking a seat should decrease available seats."""
    flights_db.clear()
    flight = Flight(id=1, origin="MAD", destination="BCN",
                    departure_time="10:00", capacity=100, available_seats=100)
    flights_db.append(flight)
    await book_seat(1)
    assert flight.available_seats == 99
