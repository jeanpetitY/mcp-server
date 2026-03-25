from fastmcp import FastMCP

server = FastMCP("sum")


@server.tool()
def add(a: float, b: float) -> float:
    """Add two numbers and return the result.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The sum of a and b.
    """
    return a + b
