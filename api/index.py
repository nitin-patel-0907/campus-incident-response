import sys
import os
from pathlib import Path

# Set Vercel environment flag
os.environ["VERCEL"] = "1"

# Resolve absolute paths
root_dir = Path(__file__).resolve().parent.parent
src_dir = root_dir / "src"
scripts_dir = root_dir / "scripts"

# Add directories to Python path
for path in [root_dir, src_dir, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Import FastAPI app from start_unified_server
from scripts.start_unified_server import app

# Export app for Vercel Serverless Function engine
app = app
