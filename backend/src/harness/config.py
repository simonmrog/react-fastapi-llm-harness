import os
from pathlib import Path

from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE)

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = os.environ.get("MODEL", "claude-opus-5-5")
MAX_ITERATIONS = int(os.environ.get("MAX_ITERATIONS", "4"))
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "16000"))
EXECUTION_TIMEOUT = int(os.environ.get("EXECUTION_TIMEOUT", "10"))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
