import sys
import os
from pathlib import Path
from fastapi import FastAPI

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

# Import inner unified FastAPI app
from scripts.start_unified_server import app as unified_app

# Create master FastAPI wrapper for Vercel serverless functions
app = FastAPI(title="Campus Incident System API")

# Mount unified_app at both /api and / to handle all Vercel path rewrite variants seamlessly
app.mount("/api", unified_app)
app.mount("/", unified_app)
