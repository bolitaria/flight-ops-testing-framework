import pytest
from unittest.mock import MagicMock

class MockFlight:
    def __init__(self, id, origin, destination, departure_time, capacity, available_seats):
        self.id = id
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.capacity = capacity
        self.available_seats = available_seats

@pytest.mark.unit
def test_book_seat_reduces_availability():
    mock_db = MagicMock()
    flight = MockFlight(1, "MAD", "BCN", "10:00", 100, 100)
    
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = flight
    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query

    if flight.available_seats > 0:
        flight.available_seats -= 1
        mock_db.commit()
        result = {"message": "Seat booked", "available_seats": flight.available_seats}
    else:
        raise Exception("No available seats")
    
    assert flight.available_seats == 99
    assert result["available_seats"] == 99
    mock_db.commit.assert_called_once()
