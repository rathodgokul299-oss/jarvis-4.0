
"""
=========================================================
JARVIS 4.0
CENTRAL FASTAPI BACKEND
=========================================================

Architecture:

Frontend
   ↓
/chat
   ↓
Local Commands
   ↓
JARVIS Core
   ├── Router
   ├── Groq
   ├── Tavily Web Search
   └── Memory

Vision
   ↓
/vision
   ↓
Groq Vision

System
   ↓
/system
   ↓
psutil

Endpoints:

GET  /
GET  /status
GET  /system

POST /chat
POST /vision

POST /wake
POST /sleep

POST /memory/remember
POST /memory/clear
POST /reset
=========================================================
"""

# =========================================================
# STANDARD LIBRARY
# =========================================================

import os
import re
import sys
import time
import traceback
import platform
from pathlib import Path
from typing import Optional


# =========================================================
# THIRD PARTY
# =========================================================

from fastapi import (
    FastAPI,
    File,
    Form,
    UploadFile,
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from pydantic import BaseModel


# =========================================================
# BACKEND PATH
# =========================================================

BACKEND_DIR = Path(
    __file__
).resolve().parent


if str(BACKEND_DIR) not in sys.path:

    sys.path.insert(
        0,
        str(BACKEND_DIR)
    )


# =========================================================
# START TIME
# =========================================================

START_TIME = time.time()


# =========================================================
# OPTIONAL PSUTIL
# =========================================================

try:

    import psutil

    PSUTIL_AVAILABLE = True

    print(
        "[MAIN] psutil loaded."
    )

except Exception as error:

    PSUTIL_AVAILABLE = False
    psutil = None

    print(
        "[MAIN] psutil unavailable:",
        repr(error)
    )


# =========================================================
# CONFIG
# =========================================================

try:

    from config import (
        GROQ_API_KEY,
        GROQ_MODEL,
        VISION_MODEL,
        TAVILY_API_KEY,
        TAVILY_SEARCH_URL,
    )

    print(
        "[MAIN] Config loaded."
    )

except Exception as error:

    print(
        "[MAIN] Config import ERROR:",
        repr(error)
    )

    GROQ_API_KEY = os.getenv(
        "GROQ_API_KEY",
        ""
    ).strip()

    GROQ_MODEL = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-120b"
    ).strip()

    VISION_MODEL = os.getenv(
        "VISION_MODEL",
        "qwen/qwen3.6-27b"
    ).strip()

    TAVILY_API_KEY = os.getenv(
        "TAVILY_API_KEY",
        ""
    ).strip()

    TAVILY_SEARCH_URL = os.getenv(
        "TAVILY_SEARCH_URL",
        "https://api.tavily.com/search"
    ).strip()


# =========================================================
# LOCAL COMMANDS
# =========================================================

try:

    from core.commands import (
        handle_local_command
    )

    COMMANDS_AVAILABLE = True

    print(
        "[MAIN] Commands loaded."
    )

except Exception as error:

    COMMANDS_AVAILABLE = False

    handle_local_command = None

    print(
        "[MAIN] Commands import ERROR:",
        repr(error)
    )


# =========================================================
# ROUTER
# =========================================================

try:

    from core.router import (
        jarvis_router
    )

    ROUTER_AVAILABLE = True

    print(
        "[MAIN] Router loaded."
    )

except Exception as error:

    ROUTER_AVAILABLE = False

    jarvis_router = None

    print(
        "[MAIN] Router import ERROR:",
        repr(error)
    )


# =========================================================
# GROQ
# =========================================================

try:

    from ai.groq import (
        jarvis_groq
    )

    GROQ_AVAILABLE = True

    print(
        "[MAIN] Groq loaded."
    )

except Exception as error:

    GROQ_AVAILABLE = False

    jarvis_groq = None

    print(
        "[MAIN] Groq import ERROR:",
        repr(error)
    )


# =========================================================
# JARVIS CORE
# =========================================================

try:

    from core.jarvis_core import (
        jarvis_core
    )

    CORE_AVAILABLE = (
        jarvis_core is not None
    )

    print(
        "[MAIN] JARVIS Core loaded."
    )

except Exception as error:

    CORE_AVAILABLE = False

    jarvis_core = None

    print(
        "[MAIN] JARVIS Core import ERROR:",
        repr(error)
    )


# =========================================================
# WEB SEARCH
# =========================================================

try:

    from web_search import (
        web_search_engine,
        create_web_search_engine,
    )

    WEB_SEARCH_AVAILABLE = (
        web_search_engine is not None
    )

    print(
        "[MAIN] Web Search loaded."
    )

except Exception as error:

    WEB_SEARCH_AVAILABLE = False

    web_search_engine = None
    create_web_search_engine = None

    print(
        "[MAIN] Web Search import ERROR:",
        repr(error)
    )


# =========================================================
# VISION
# =========================================================

try:

    from vision import (
        ask_vision
    )

    VISION_MODULE_AVAILABLE = True

    print(
        "[MAIN] Vision loaded."
    )

except Exception as error:

    VISION_MODULE_AVAILABLE = False

    ask_vision = None

    print(
        "[MAIN] Vision import ERROR:",
        repr(error)
    )


# =========================================================
# APP
# =========================================================

app = FastAPI(

    title="JARVIS 4.0",

    description=(
        "Personal AI Assistant Backend"
    ),

    version="4.0.0",

)


# =========================================================
# CORS
# =========================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)


# =========================================================
# STATE
# =========================================================

jarvis_sleeping = False


# =========================================================
# REQUEST MODELS
# =========================================================

class ChatRequest(
    BaseModel
):

    message: str


class MemoryRequest(
    BaseModel
):

    role: str

    content: str


# =========================================================
# HELPER
# =========================================================

def clean_reply(
    text: str
) -> str:

    text = str(
        text or ""
    ).strip()


    text = re.sub(

        r"<think>.*?</think>",

        "",

        text,

        flags=
            re.IGNORECASE
            |
            re.DOTALL,

    )


    text = re.sub(

        r"<think>.*$",

        "",

        text,

        flags=
            re.IGNORECASE
            |
            re.DOTALL,

    )


    text = re.sub(

        r"</?think>",

        "",

        text,

        flags=
            re.IGNORECASE,

    )


    return text.strip()


# =========================================================
# SYSTEM MONITOR
# =========================================================

def format_bytes(
    value: int
) -> str:

    try:

        value = float(
            value or 0
        )

    except Exception:

        value = 0.0


    units = [
        "B",
        "KB",
        "MB",
        "GB",
        "TB",
    ]


    index = 0


    while (
        value >= 1024
        and
        index < len(units) - 1
    ):

        value /= 1024

        index += 1


    if index == 0:

        return (
            f"{int(value)} "
            f"{units[index]}"
        )


    return (
        f"{value:.2f} "
        f"{units[index]}"
    )


def format_uptime(
    seconds: int
) -> str:

    try:

        seconds = int(
            seconds
        )

    except Exception:

        seconds = 0


    seconds = max(
        seconds,
        0
    )


    days = seconds // 86400

    seconds %= 86400

    hours = seconds // 3600

    seconds %= 3600

    minutes = seconds // 60

    seconds %= 60


    if days:

        return (
            f"{days}d "
            f"{hours}h "
            f"{minutes}m"
        )


    if hours:

        return (
            f"{hours}h "
            f"{minutes}m"
        )


    if minutes:

        return (
            f"{minutes}m "
            f"{seconds}s"
        )


    return f"{seconds}s"


def get_system_stats():

    if not PSUTIL_AVAILABLE:

        return {

            "success":
                False,

            "online":
                False,

            "error":
                "psutil is not installed.",

        }


    try:

        cpu = psutil.cpu_percent(
            interval=0.15
        )


        memory = (
            psutil.virtual_memory()
        )


        disk = psutil.disk_usage(
            os.path.abspath(
                os.sep
            )
        )


        network = (
            psutil.net_io_counters()
        )


        battery = None
        battery_charging = None


        try:

            battery_info = (
                psutil.sensors_battery()
            )

            if battery_info:

                battery = round(
                    float(
                        battery_info.percent
                    ),
                    1
                )

                battery_charging = (
                    bool(
                        battery_info.power_plugged
                    )
                )

        except Exception:

            pass


        uptime_seconds = int(

            time.time()
            -
            START_TIME

        )


        return {

            "success":
                True,

            "online":
                True,

            "cpu":
                round(
                    float(cpu),
                    1
                ),

            "ram":
                round(
                    float(
                        memory.percent
                    ),
                    1
                ),

            "ram_used_gb":
                round(
                    memory.used
                    /
                    (1024 ** 3),
                    2
                ),

            "ram_total_gb":
                round(
                    memory.total
                    /
                    (1024 ** 3),
                    2
                ),

            "disk":
                round(
                    float(
                        disk.percent
                    ),
                    1
                ),

            "disk_used_gb":
                round(
                    disk.used
                    /
                    (1024 ** 3),
                    2
                ),

            "disk_total_gb":
                round(
                    disk.total
                    /
                    (1024 ** 3),
                    2
                ),

            "battery":
                battery,

            "battery_charging":
                battery_charging,

            "network_sent":
                (
                    network.bytes_sent
                    if network
                    else 0
                ),

            "network_received":
                (
                    network.bytes_recv
                    if network
                    else 0
                ),

            "network_sent_text":
                format_bytes(
                    network.bytes_sent
                    if network
                    else 0
                ),

            "network_received_text":
                format_bytes(
                    network.bytes_recv
                    if network
                    else 0
                ),

            "uptime":
                uptime_seconds,

            "uptime_text":
                format_uptime(
                    uptime_seconds
                ),

            "os":
                platform.system(),

            "os_release":
                platform.release(),

            "platform":
                platform.platform(),

            "processor":
                platform.processor(),

            "cpu_cores":
                psutil.cpu_count(
                    logical=True
                ),

            "physical_cores":
                psutil.cpu_count(
                    logical=False
                ),

        }


    except Exception as error:

        print(
            "[SYSTEM MONITOR ERROR]:",
            repr(error)
        )

        return {

            "success":
                False,

            "online":
                False,

            "error":
                repr(error),

        }


# =========================================================
# ROOT
# =========================================================

@app.get("/")
async def root():

    return {

        "name":
            "JARVIS 4.0",

        "status":
            "online",

        "version":
            "4.0.0",

        "ai":
            "Groq",

        "groq":
            GROQ_AVAILABLE,

        "groq_model":
            GROQ_MODEL,

        "router":
            ROUTER_AVAILABLE,

        "commands":
            COMMANDS_AVAILABLE,

        "core":
            CORE_AVAILABLE,

        "web_search":
            WEB_SEARCH_AVAILABLE,

        "tavily":
            bool(
                TAVILY_API_KEY
            ),

        "vision":
            VISION_MODULE_AVAILABLE,

        "vision_model":
            VISION_MODEL,

        "system_monitor":
            PSUTIL_AVAILABLE,

        "server":
            "local",

    }


# =========================================================
# STATUS
# =========================================================

@app.get("/status")
async def status():

    groq_ok = False

    groq_model = GROQ_MODEL


    if jarvis_groq is not None:

        try:

            groq_ok = (
                jarvis_groq.is_available()
            )

            groq_model = (
                jarvis_groq.model
            )

        except Exception:

            groq_ok = False


    core_ok = (
        jarvis_core is not None
    )


    web_ok = (
        web_search_engine is not None
        and
        bool(
            TAVILY_API_KEY
        )
    )


    return {

        "status":
            "online",

        "jarvis":
            True,

        "sleeping":
            jarvis_sleeping,

        "groq":
            groq_ok,

        "groq_model":
            groq_model,

        "router":
            ROUTER_AVAILABLE,

        "commands":
            COMMANDS_AVAILABLE,

        "core":
            core_ok,

        "web":
            web_ok,

        "tavily":
            bool(
                TAVILY_API_KEY
            ),

        "vision":
            VISION_MODULE_AVAILABLE,

        "vision_model":
            VISION_MODEL,

        "system_monitor":
            PSUTIL_AVAILABLE,

        "server":
            "local",

    }


# =========================================================
# SYSTEM
# =========================================================

@app.get("/system")
async def system():

    return get_system_stats()


# =========================================================
# WAKE
# =========================================================

@app.post("/wake")
async def wake():

    global jarvis_sleeping

    jarvis_sleeping = False


    return {

        "success":
            True,

        "reply":
            "Ready Sir.",

        "message":
            "Ready Sir.",

        "sleeping":
            False,

        "local":
            True,

        "web":
            False,

    }


# =========================================================
# SLEEP
# =========================================================

@app.post("/sleep")
async def sleep():

    global jarvis_sleeping

    jarvis_sleeping = True


    return {

        "success":
            True,

        "reply":
            "Okay Sir, sleeping now.",

        "message":
            "Okay Sir, sleeping now.",

        "sleeping":
            True,

        "local":
            True,

        "web":
            False,

    }


# =========================================================
# CHAT
# =========================================================

@app.post("/chat")
async def chat(
    request: ChatRequest
):

    global jarvis_sleeping


    message = str(
        request.message or ""
    ).strip()


    # -----------------------------------------------------
    # EMPTY
    # -----------------------------------------------------

    if not message:

        return {

            "success":
                False,

            "reply":
                "Sir, काहीतरी बोला.",

            "message":
                "Sir, काहीतरी बोला.",

            "local":
                False,

            "web":
                False,

            "sleeping":
                jarvis_sleeping,

        }


    print()
    print(
        "=" * 60
    )

    print(
        "[JARVIS REQUEST]"
    )

    print(
        "Message:",
        message
    )

    print(
        "Sleeping:",
        jarvis_sleeping
    )

    print(
        "=" * 60
    )


    # =====================================================
    # LOCAL COMMANDS
    # =====================================================

    if COMMANDS_AVAILABLE:

        try:

            command_result = (
                handle_local_command(
                    message
                )
            )


            # ---------------------------------------------
            # Current commands.py returns 3 values
            # ---------------------------------------------

            if isinstance(
                command_result,
                tuple
            ):

                if len(
                    command_result
                ) == 3:

                    handled = (
                        command_result[0]
                    )

                    local_reply = (
                        command_result[1]
                    )

                    new_sleeping = (
                        command_result[2]
                    )

                elif len(
                    command_result
                ) == 2:

                    handled = (
                        command_result[0]
                    )

                    local_reply = (
                        command_result[1]
                    )

                    new_sleeping = (
                        jarvis_sleeping
                    )

                else:

                    handled = False

                    local_reply = None

                    new_sleeping = (
                        jarvis_sleeping
                    )

            else:

                handled = False

                local_reply = None

                new_sleeping = (
                    jarvis_sleeping
                )


            # ---------------------------------------------
            # Update state
            # ---------------------------------------------

            if handled:

                jarvis_sleeping = bool(
                    new_sleeping
                )


                return {

                    "success":
                        True,

                    "reply":
                        clean_reply(
                            local_reply
                        ),

                    "message":
                        clean_reply(
                            local_reply
                        ),

                    "local":
                        True,

                    "web":
                        False,

                    "sleeping":
                        jarvis_sleeping,

                }


        except Exception as error:

            print(
                "[LOCAL COMMAND ERROR]:",
                repr(error)
            )

            traceback.print_exc()


    # =====================================================
    # SLEEPING
    # =====================================================

    if jarvis_sleeping:

        return {

            "success":
                True,

            "reply":
                None,

            "message":
                None,

            "local":
                True,

            "web":
                False,

            "sleeping":
                True,

        }


    # =====================================================
    # CORE CHECK
    # =====================================================

    if jarvis_core is None:

        return {

            "success":
                False,

            "reply":
                "Sir, JARVIS Core available नाही.",

            "message":
                "Sir, JARVIS Core available नाही.",

            "local":
                False,

            "web":
                False,

            "sleeping":
                jarvis_sleeping,

        }


    # =====================================================
    # CORE PROCESS
    # =====================================================

    try:

        result = await jarvis_core.process(
            message
        )


    except Exception as error:

        print()
        print(
            "[CORE ERROR]"
        )

        print(
            repr(error)
        )

        traceback.print_exc()


        return {

            "success":
                False,

            "reply":
                "Sir, JARVIS Core मध्ये error आला.",

            "message":
                "Sir, JARVIS Core मध्ये error आला.",

            "local":
                False,

            "web":
                False,

            "sleeping":
                jarvis_sleeping,

            "error":
                repr(error),

        }


    # =====================================================
    # INVALID CORE RESULT
    # =====================================================

    if not isinstance(
        result,
        dict
    ):

        return {

            "success":
                False,

            "reply":
                "Sir, Core कडून invalid response मिळाला.",

            "message":
                "Sir, Core कडून invalid response मिळाला.",

            "local":
                False,

            "web":
                False,

            "sleeping":
                jarvis_sleeping,

        }


    result_type = str(
        result.get(
            "type",
            "chat"
        )
        or
        "chat"
    ).strip().lower()


    # =====================================================
    # WEB
    # =====================================================

    if result_type == "web":

        web_reply = clean_reply(

            result.get(
                "message",
                ""
            )

        )


        if not web_reply:

            web_reply = (
                "Sir, web search कडून योग्य answer मिळाला नाही."
            )


        return {

            "success":
                True,

            "reply":
                web_reply,

            "message":
                web_reply,

            "local":
                False,

            "web":
                True,

            "sleeping":
                jarvis_sleeping,

            "route":
                result.get(
                    "route"
                ),

            "context":
                result.get(
                    "context",
                    ""
                ),

        }


    # =====================================================
    # ERROR
    # =====================================================

    if result_type == "error":

        error_message = clean_reply(

            result.get(
                "message",
                "AI response generate करण्यात error आला."
            )

        )


        return {

            "success":
                False,

            "reply":
                error_message,

            "message":
                error_message,

            "local":
                False,

            "web":
                False,

            "sleeping":
                jarvis_sleeping,

            "route":
                result.get(
                    "route"
                ),

            "error":
                result.get(
                    "error"
                ),

        }


    # =====================================================
    # NORMAL CHAT
    # =====================================================

    reply = clean_reply(

        result.get(
            "message",
            ""
        )

    )


    if not reply:

        reply = (
            "Sir, मला योग्य response मिळाला नाही."
        )


    return {

        "success":
            True,

        "reply":
            reply,

        "message":
            reply,

        "local":
            False,

        "web":
            False,

        "sleeping":
            jarvis_sleeping,

        "route":
            result.get(
                "route"
            ),

        "context":
            result.get(
                "context",
                ""
            ),

        "model":
            result.get(
                "model"
            ),

    }


# =========================================================
# VISION
# =========================================================

@app.post("/vision")
async def vision_endpoint(

    image: UploadFile = File(...),

    prompt: str = Form(

        "या image मध्ये काय दिसत आहे? "
        "महत्वाचे details थोडक्यात सांगा."

    ),

):

    start_time = time.time()


    # =====================================================
    # MODULE CHECK
    # =====================================================

    if not VISION_MODULE_AVAILABLE:

        return {

            "success":
                False,

            "reply":
                "Sir, Vision module उपलब्ध नाही.",

            "vision":
                False,

            "model":
                VISION_MODEL,

        }


    # =====================================================
    # FILE VALIDATION
    # =====================================================

    filename = str(
        image.filename or ""
    ).strip()


    content_type = str(

        image.content_type
        or
        "image/png"

    ).strip().lower()


    allowed_types = {

        "image/png",

        "image/jpeg",

        "image/jpg",

        "image/webp",

    }


    if content_type not in allowed_types:

        return {

            "success":
                False,

            "reply":
                "Sir, PNG, JPG किंवा WEBP image वापरा.",

            "vision":
                False,

        }


    # =====================================================
    # READ IMAGE
    # =====================================================

    try:

        image_bytes = await image.read()

    except Exception as error:

        print(
            "[VISION READ ERROR]:",
            repr(error)
        )

        return {

            "success":
                False,

            "reply":
                "Sir, image read करता आली नाही.",

            "error":
                repr(error),

        }


    if not image_bytes:

        return {

            "success":
                False,

            "reply":
                "Sir, image data रिकामी आहे.",

        }


    # =====================================================
    # SIZE LIMIT
    # =====================================================

    max_image_size = (
        20 * 1024 * 1024
    )


    if len(image_bytes) > max_image_size:

        return {

            "success":
                False,

            "reply":
                "Sir, image 20 MB पेक्षा कमी असावी.",

            "size":
                len(image_bytes),

        }


    print()
    print(
        "[VISION REQUEST]"
    )

    print(
        "Filename:",
        filename
    )

    print(
        "Content Type:",
        content_type
    )

    print(
        "Size:",
        len(image_bytes),
        "bytes"
    )

    print(
        "Model:",
        VISION_MODEL
    )


    # =====================================================
    # GROQ CLIENT
    # =====================================================

    groq_client = None


    if jarvis_groq is not None:

        try:

            groq_client = (
                jarvis_groq.client
            )

        except Exception:

            groq_client = None


    if groq_client is None:

        return {

            "success":
                False,

            "reply":
                "Sir, Groq Vision client उपलब्ध नाही.",

        }


    # =====================================================
    # ASK VISION
    # =====================================================

    try:

        reply = ask_vision(

            image_bytes=image_bytes,

            prompt=prompt,

            content_type=content_type,

            groq_client=groq_client,

            model=VISION_MODEL,

            temperature=0.7,

            max_tokens=1024,

        )


    except Exception as error:

        print(
            "[VISION ERROR]:",
            repr(error)
        )

        traceback.print_exc()


        return {

            "success":
                False,

            "reply":
                "Sir, image analysis करताना problem आली.",

            "error":
                repr(error),

            "filename":
                filename,

            "content_type":
                content_type,

            "vision":
                False,

            "model":
                VISION_MODEL,

        }


    # =====================================================
    # CLEAN
    # =====================================================

    reply = clean_reply(
        reply
    )


    if not reply:

        return {

            "success":
                False,

            "reply":
                "Sir, Vision कडून response मिळाला नाही.",

            "vision":
                False,

        }


    elapsed = round(

        time.time()
        -
        start_time,

        2

    )


    print(
        "[VISION SUCCESS]"
    )

    print(
        "Time:",
        elapsed,
        "seconds"
    )

    print(
        "Reply:",
        reply
    )


    return {

        "success":
            True,

        "reply":
            reply,

        "message":
            reply,

        "filename":
            filename,

        "content_type":
            content_type,

        "vision":
            True,

        "model":
            VISION_MODEL,

        "time":
            elapsed,

    }


# =========================================================
# MEMORY REMEMBER
# =========================================================

@app.post("/memory/remember")
async def remember(
    request: MemoryRequest
):

    if jarvis_core is None:

        return {

            "success":
                False,

            "message":
                "JARVIS Core unavailable."

        }


    try:

        success = (
            jarvis_core.remember(
                request.role,
                request.content
            )
        )


        return {

            "success":
                bool(success),

            "message":
                (
                    "Memory saved."
                    if success
                    else
                    "Memory save failed."
                ),

        }


    except Exception as error:

        print(
            "[MEMORY SAVE ERROR]:",
            repr(error)
        )


        return {

            "success":
                False,

            "message":
                "Memory save failed.",

            "error":
                repr(error),

        }


# =========================================================
# MEMORY CLEAR
# =========================================================

@app.post("/memory/clear")
async def clear_memory():

    if jarvis_core is None:

        return {

            "success":
                False,

            "message":
                "JARVIS Core unavailable."

        }


    try:

        success = (
            jarvis_core.clear_memory()
        )


        return {

            "success":
                bool(success),

            "message":
                (
                    "Memory cleared."
                    if success
                    else
                    "Memory clear failed."
                ),

        }


    except Exception as error:

        print(
            "[MEMORY CLEAR ERROR]:",
            repr(error)
        )


        return {

            "success":
                False,

            "message":
                "Memory clear failed.",

            "error":
                repr(error),

        }


# =========================================================
# RESET
# =========================================================

@app.post("/reset")
async def reset():

    try:

        if jarvis_core is not None:

            if hasattr(
                jarvis_core,
                "clear_memory"
            ):

                jarvis_core.clear_memory()


        return {

            "success":
                True,

            "message":
                "Conversation reset.",

        }


    except Exception as error:

        print(
            "[RESET ERROR]:",
            repr(error)
        )


        return {

            "success":
                False,

            "message":
                "Reset failed.",

            "error":
                repr(error),

        }


# =========================================================
# STARTUP
# =========================================================

@app.on_event(
    "startup"
)
async def startup_event():

    print()
    print(
        "=" * 60
    )

    print(
        "          JARVIS 4.0 BACKEND"
    )

    print(
        "=" * 60
    )

    print(
        "[STARTUP] Backend:",
        BACKEND_DIR
    )

    print(
        "[STARTUP] Core:",
        CORE_AVAILABLE
    )

    print(
        "[STARTUP] Router:",
        ROUTER_AVAILABLE
    )

    print(
        "[STARTUP] Commands:",
        COMMANDS_AVAILABLE
    )

    print(
        "[STARTUP] Groq:",
        GROQ_AVAILABLE
    )

    print(
        "[STARTUP] Groq Model:",
        GROQ_MODEL
    )

    print(
        "[STARTUP] Tavily:",
        bool(
            TAVILY_API_KEY
        )
    )

    print(
        "[STARTUP] Web Search:",
        WEB_SEARCH_AVAILABLE
    )

    print(
        "[STARTUP] Vision:",
        VISION_MODULE_AVAILABLE
    )

    print(
        "[STARTUP] Vision Model:",
        VISION_MODEL
    )

    print(
        "[STARTUP] System Monitor:",
        PSUTIL_AVAILABLE
    )

    print(
        "[STARTUP] Server:",
        "http://127.0.0.1:8000"
    )

    print(
        "=" * 60
    )

    print(
        "[STARTUP] JARVIS 4.0 READY."
    )

    print(
        "=" * 60
    )

    print()


# =========================================================
# SHUTDOWN
# =========================================================

@app.on_event(
    "shutdown"
)
async def shutdown_event():

    print()
    print(
        "[SHUTDOWN] JARVIS 4.0 stopping..."
    )

    print()


# =========================================================
# RUN DIRECTLY
# =========================================================

if __name__ == "__main__":

    import uvicorn


    HOST = os.getenv(
        "SERVER_HOST",
        "0.0.0.0"
    )


    try:

        PORT = int(
            os.getenv(
                "SERVER_PORT",
                "8000"
            )
        )

    except Exception:

        PORT = 8000


    print()
    print(
        "[JARVIS] Starting server..."
    )

    print(
        f"[JARVIS] http://127.0.0.1:{PORT}"
    )

    print()


    uvicorn.run(

        app,

        host=HOST,

        port=PORT,

        reload=False,

    )

