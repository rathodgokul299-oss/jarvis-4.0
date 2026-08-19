# =========================================================
# JARVIS 4.0 - CONFIGURATION
# =========================================================

import os
from pathlib import Path


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = Path(__file__).resolve().parent


# =========================================================
# ENVIRONMENT FILE
# =========================================================

ENV_FILE = BASE_DIR / ".env"


# =========================================================
# SIMPLE ENV LOADER
# =========================================================

def load_env_file():

    if not ENV_FILE.exists():
        return

    try:

        with open(
            ENV_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                if line.startswith("#"):
                    continue

                if "=" not in line:
                    continue

                key, value = line.split(
                    "=",
                    1
                )

                key = key.strip()
                value = value.strip()

                if (
                    len(value) >= 2
                    and value[0] == '"'
                    and value[-1] == '"'
                ):
                    value = value[1:-1]

                if (
                    len(value) >= 2
                    and value[0] == "'"
                    and value[-1] == "'"
                ):
                    value = value[1:-1]

                if key:
                    os.environ.setdefault(
                        key,
                        value
                    )

    except Exception as error:

        print(
            "[CONFIG] .env load error:",
            repr(error)
        )


load_env_file()


# =========================================================
# HELPER
# =========================================================

def get_env(
    name: str,
    default: str = ""
):

    return os.getenv(
        name,
        default
    ).strip()


def get_int(
    name: str,
    default: int
):

    try:

        return int(
            get_env(
                name,
                str(default)
            )
        )

    except (ValueError, TypeError):

        return default


def get_float(
    name: str,
    default: float
):

    try:

        return float(
            get_env(
                name,
                str(default)
            )
        )

    except (ValueError, TypeError):

        return default


# =========================================================
# GROQ
# =========================================================

GROQ_API_KEY = get_env(
    "GROQ_API_KEY"
)

GROQ_MODEL = get_env(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)

VISION_MODEL = get_env(
    "VISION_MODEL",
    "meta-llama/llama-4-scout-17b-16e-instruct"
)


# =========================================================
# TAVILY
# =========================================================

TAVILY_API_KEY = get_env(
    "TAVILY_API_KEY"
)

TAVILY_SEARCH_URL = get_env(
    "TAVILY_SEARCH_URL",
    "https://api.tavily.com/search"
)


# =========================================================
# SERVER
# =========================================================

SERVER_HOST = get_env(
    "SERVER_HOST",
    "0.0.0.0"
)

SERVER_PORT = get_int(
    "SERVER_PORT",
    8000
)


# =========================================================
# AI PARAMETERS
# =========================================================

CHAT_NUM_PREDICT = get_int(
    "CHAT_NUM_PREDICT",
    1024
)

VISION_NUM_PREDICT = get_int(
    "VISION_NUM_PREDICT",
    1024
)

CHAT_TEMPERATURE = get_float(
    "CHAT_TEMPERATURE",
    0.7
)

VISION_TEMPERATURE = get_float(
    "VISION_TEMPERATURE",
    0.2
)


# =========================================================
# MEMORY
# =========================================================

MEMORY_DB_PATH = get_env(
    "MEMORY_DB_PATH",
    str(BASE_DIR / "jarvis_memory.db")
)

MEMORY_CONTEXT_LIMIT = get_int(
    "MEMORY_CONTEXT_LIMIT",
    12
)


# =========================================================
# OLLAMA
# =========================================================

# Kept only for compatibility.
# JARVIS 4.0 uses Groq as the main AI engine.

OLLAMA_URL = get_env(
    "OLLAMA_URL",
    "http://127.0.0.1:11434/api/chat"
)


# =========================================================
# DEBUG / STATUS
# =========================================================

DEBUG = (
    get_env(
        "DEBUG",
        "false"
    ).lower()
    in (
        "1",
        "true",
        "yes",
        "on"
    )
)


# =========================================================
# CONFIG STATUS
# =========================================================

print(
    "[CONFIG] Loaded:",
    ENV_FILE
)

print(
    "[GROQ] API key:",
    "FOUND"
    if GROQ_API_KEY
    else
    "MISSING"
)

print(
    "[GROQ] Model:",
    GROQ_MODEL
)

print(
    "[VISION] Model:",
    VISION_MODEL
)

print(
    "[TAVILY] API key:",
    "FOUND"
    if TAVILY_API_KEY
    else
    "MISSING"
)

print(
    "[SERVER] Host:",
    SERVER_HOST
)

print(
    "[SERVER] Port:",
    SERVER_PORT
)