from ..utils import tool

import io
import contextlib


@tool()
def execute_python_code(code: str) -> str:
    """Executes python code in the active environemnt."""
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            exec(code)
        return output.getvalue()
    except Exception as e:
        return str(e)
