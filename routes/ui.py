"""UI route handler."""
from fastapi.responses import HTMLResponse
from pathlib import Path


async def get_ui():
    """Serve the main UI page."""
    html_path = Path(__file__).parent.parent / "static" / "index.html"
    
    if not html_path.exists():
        return HTMLResponse(
            content="<h1>Error: index.html not found</h1>",
            status_code=500
        )
    
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    return HTMLResponse(html_content)