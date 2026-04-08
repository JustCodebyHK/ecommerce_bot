from pydantic import BaseModel, Field
from typing import Optional

class Action(BaseModel):
    # This tells the LLM what tools it has
    action_type: str = Field(description="One of: query_order, update_address, issue_refund")
    order_id: str = Field(description="The 3-digit order ID")
    data: Optional[str] = Field(description="New address or reason for refund", default=None)

class Observation(BaseModel):
    # This is what the LLM 'sees' after an action
    status_msg: str
    order_details: Optional[dict] = None
    success: bool