from langchain_core.tools import tool
from typing import Optional, Dict, Any

# Note: The actual flight_service and booking_service imports are omitted or mocked here
# as they belong to the service layer which handles the business logic.

@tool
def search_flight_tool(origin: str, destination: str, date: str) -> Dict[str, Any]:
    """Search for available flights based on origin, destination, and date."""
    # In a real implementation, this would call `flight_service.search_flights(...)`
    # Mock response for now:
    return {
        "status": "success",
        "data": [
            {"flight_no": "CA123", "origin": origin, "destination": destination, "time": f"{date} 10:00", "price": 500},
            {"flight_no": "MU456", "origin": origin, "destination": destination, "time": f"{date} 14:00", "price": 450}
        ]
    }

@tool
def book_flight_tool(flight_no: str, user_id: str) -> Dict[str, Any]:
    """Book a specific flight using the flight number."""
    # In a real implementation, this would call `booking_service.create_booking(...)`
    # Mock response for now:
    return {
        "status": "success",
        "message": f"Successfully booked flight {flight_no} for user {user_id}.",
        "booking_id": "BKG-9999"
    }
