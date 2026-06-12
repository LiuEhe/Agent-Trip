from langchain_core.tools import tool
from typing import Dict, Any

@tool
def check_user_limits_tool(user_id: str) -> Dict[str, Any]:
    """Check the booking limits and status of the current user."""
    # This would normally call `user_service.get_user_limits(...)`
    return {
        "user_id": user_id,
        "remaining_quota": 5,
        "status": "active"
    }
