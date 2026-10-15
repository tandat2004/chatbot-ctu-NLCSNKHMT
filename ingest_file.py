#!/usr/bin/env python3
import sys
from pathlib import Path
import subprocess

# Chạy rag_pipeline/ingest_file.py với các tham số truyền vào
script = Path(__file__).resolve().parent / "rag_pipeline" / "ingest_file.py"
cmd = [sys.executable, str(script)] + sys.argv[1:]
sys.exit(subprocess.run(cmd).returncode)
