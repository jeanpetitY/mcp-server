from fastmcp import FastMCP
from server.services import SumService

server = FastMCP("sum")
sum_service = SumService()


@server.tool()
def add(a: float, b: float) -> float:
    """Add two numbers and return the result.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The sum of a and b.
    """
    return sum_service.add(a, b)
