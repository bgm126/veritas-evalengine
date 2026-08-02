"""Sandboxed tools for order processing agent."""

from veritas_evalengine.scorers.tool_replay import ToolSpec

ORDER_TOOLS = [
    ToolSpec(
        name="fetch_order",
        description="Fetches order information by order ID.",
        input_schema={"order_id": "str"},
        output_schema={"status": "str", "items": "list"},
        side_effects=[],
        idempotent=True,
    ),
    ToolSpec(
        name="cancel_order",
        description="Cancels an order by order ID.",
        input_schema={"order_id": "str"},
        output_schema={"status": "str"},
        side_effects=["update_db"],
        idempotent=False,
    ),
]
