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
   ├── Chrome
   ├── Calculator
   ├── YouTube
   ├── Sleep
   └── Wake
   ↓
JARVIS Core
   ↓
Router
   ├── Web
   └── Groq AI
   ↓
Memory
   ↓
Response

Endpoints:

GET  /
GET  /status

POST /chat
POST /wake
POST /sleep

POST /memory/remember
POST /memory/clear
=========================================================
"""

import os
import sys
import traceback
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# =========================================================
# BACKEND PATH
# =========================================================

BACKEND_DIR = Path(__file__).resolve().parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


print()
print("=" * 60)
print("              JARVIS 4.0")
print("          BACKEND INITIALIZING")
print("=" * 60)
print("[MAIN] Backend directory:", BACKEND_DIR)
print()


# =========================================================
# COMPONENT IMPORTS
# =========================================================

handle_local_command = None
jarvis_router = None
jarvis_groq = None
jarvis_core = None


# =========================================================
# COMMANDS
# =========================================================

try:

    from core.commands import handle_local_command

    print("[MAIN] Commands loaded successfully.")

except Exception as error:

    print("[MAIN] Commands import ERROR:")
    print(repr(error))

    traceback.print_exc()


# =========================================================
# ROUTER
# =========================================================

try:

    from core.router import jarvis_router

    print("[MAIN] Router loaded successfully.")

except Exception as error:

    print("[MAIN] Router import ERROR:")
    print(repr(error))

    traceback.print_exc()


# =========================================================
# GROQ
# =========================================================

try:

    from ai.groq import jarvis_groq

    print("[MAIN] Groq loaded successfully.")

except Exception as error:

    print("[MAIN] Groq import ERROR:")
    print(repr(error))

    traceback.print_exc()


# =========================================================
# JARVIS CORE
# =========================================================

try:

    from core.jarvis_core import jarvis_core

    print("[MAIN] JARVIS Core loaded successfully.")

except Exception as error:

    print("[MAIN] JARVIS Core import ERROR:")
    print(repr(error))

    traceback.print_exc()


# =========================================================
# APP
# =========================================================

app = FastAPI(

    title="JARVIS 4.0",

    description=(
        "JARVIS Personal AI Assistant Backend"
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
# GLOBAL STATE
# =========================================================

jarvis_sleeping = False


# =========================================================
# REQUEST MODELS
# =========================================================

class ChatRequest(BaseModel):

    message: str


class MemoryRequest(BaseModel):

    role: str

    content: str


# =========================================================
# HELPER
# =========================================================

def get_core_status():

    """
    Safely check whether JARVIS Core is available.
    """

    global jarvis_core

    return jarvis_core is not None


def get_groq_status():

    """
    Safely check Groq availability.
    """

    global jarvis_groq

    if jarvis_groq is None:
        return False

    try:

        return bool(
            jarvis_groq.is_available()
        )

    except Exception:

        return False


def get_groq_model():

    """
    Safely get current Groq model.
    """

    global jarvis_groq

    if jarvis_groq is None:
        return None

    try:

        return jarvis_groq.model

    except Exception:

        return None


# =========================================================
# ROOT
# =========================================================

@app.get("/")
async def root():

    return {

        "name": "JARVIS",

        "version": "4.0.0",

        "status": "online",

        "message": (
            "JARVIS 4.0 Backend is running."
        ),

        "components": {

            "core": get_core_status(),

            "router": (
                jarvis_router is not None
            ),

            "commands": (
                handle_local_command is not None
            ),

            "groq": get_groq_status(),

        },

    }


# =========================================================
# STATUS
# =========================================================

@app.get("/status")
async def status():

    core_available = get_core_status()

    router_available = (
        jarvis_router is not None
    )

    commands_available = (
        handle_local_command is not None
    )

    groq_available = get_groq_status()

    groq_model = get_groq_model()


    return {

        "status": "online",

        "jarvis": True,

        "sleeping": jarvis_sleeping,

        "groq": groq_available,

        "groq_model": groq_model,

        "router": router_available,

        "commands": commands_available,

        "core": core_available,

    }


# =========================================================
# WAKE
# =========================================================

@app.post("/wake")
async def wake():

    global jarvis_sleeping

    jarvis_sleeping = False

    print(
        "[JARVIS] Wake command received."
    )

    return {

        "success": True,

        "reply": "Ready Sir.",

        "message": "Ready Sir.",

        "sleeping": False,

        "local": True,

        "web": False,

    }


# =========================================================
# SLEEP
# =========================================================

@app.post("/sleep")
async def sleep():

    global jarvis_sleeping

    jarvis_sleeping = True

    print(
        "[JARVIS] Sleep command received."
    )

    return {

        "success": True,

        "reply": "Okay Sir, sleeping now.",

        "message": "Okay Sir, sleeping now.",

        "sleeping": True,

        "local": True,

        "web": False,

    }


# =========================================================
# CHAT
# =========================================================

@app.post("/chat")
async def chat(request: ChatRequest):

    global jarvis_sleeping

    message = str(
        request.message or ""
    ).strip()


    # =====================================================
    # EMPTY MESSAGE
    # =====================================================

    if not message:

        return {

            "success": False,

            "reply": (
                "Sir, message रिकामा आहे."
            ),

            "message": (
                "Sir, message रिकामा आहे."
            ),

            "local": False,

            "web": False,

            "sleeping": jarvis_sleeping,

        }


    # =====================================================
    # LOG
    # =====================================================

    print()
    print("=" * 60)

    print("[JARVIS REQUEST]")

    print("Message:", message)

    print("Sleeping:", jarvis_sleeping)

    print("=" * 60)


    # =====================================================
    # LOCAL COMMAND SYSTEM
    # =====================================================

    if handle_local_command is not None:

        try:

            handled, local_reply, new_sleeping = (
                handle_local_command(

                    message,

                    sleeping=jarvis_sleeping,

                )
            )


            print(
                "[LOCAL RESULT]:",
                handled,
                local_reply,
                new_sleeping
            )


            # =================================================
            # WAKE COMMAND
            # =================================================

            if handled and not new_sleeping:

                normalized = (
                    message
                    .strip()
                    .lower()
                )


                wake_words = [

                    "wake",

                    "wake up",

                    "wake jarvis",

                    "wake up jarvis",

                    "jarvis wake",

                    "jarvis wake up",

                    "wake up please",

                    "jarvis please wake up",

                    "जाग",

                    "जाग जार्विस",

                    "जार्विस जाग",

                    "जागा जार्विस",

                ]


                is_wake = (

                    normalized in wake_words

                    or
                    "wake up jarvis"
                    in normalized

                    or
                    "jarvis wake up"
                    in normalized

                )


                if is_wake:

                    jarvis_sleeping = False

                    reply = (
                        local_reply
                        or
                        "Ready Sir."
                    )


                    return {

                        "success": True,

                        "reply": reply,

                        "message": reply,

                        "local": True,

                        "web": False,

                        "sleeping": False,

                    }


            # =================================================
            # SLEEP COMMAND
            # =================================================

            if handled and new_sleeping:

                jarvis_sleeping = True

                reply = (

                    local_reply

                    or

                    "Okay Sir, sleeping now."

                )


                return {

                    "success": True,

                    "reply": reply,

                    "message": reply,

                    "local": True,

                    "web": False,

                    "sleeping": True,

                }


            # =================================================
            # OTHER LOCAL COMMAND
            # =================================================

            if handled and local_reply:

                jarvis_sleeping = (
                    new_sleeping
                )

                return {

                    "success": True,

                    "reply": local_reply,

                    "message": local_reply,

                    "local": True,

                    "web": False,

                    "sleeping": (
                        jarvis_sleeping
                    ),

                }


            # =================================================
            # SLEEPING
            # =================================================

            if jarvis_sleeping:

                return {

                    "success": True,

                    "reply": None,

                    "message": None,

                    "local": True,

                    "web": False,

                    "sleeping": True,

                }


        except Exception as error:

            print(
                "[LOCAL COMMAND ERROR]:",
                repr(error)
            )

            traceback.print_exc()


    # =====================================================
    # CORE CHECK
    # =====================================================

    if jarvis_core is None:

        print(
            "[MAIN] JARVIS Core unavailable."
        )


        return {

            "success": False,

            "reply": (
                "Sir, JARVIS Core available नाही."
            ),

            "message": (
                "Sir, JARVIS Core available नाही."
            ),

            "local": False,

            "web": False,

            "sleeping": jarvis_sleeping,

            "core": False,

        }


    # =====================================================
    # CORE PROCESS
    # =====================================================

    try:

        print(
            "[MAIN] Sending request to JARVIS Core..."
        )


        result = await jarvis_core.process(
            message
        )


    except Exception as error:

        print()
        print("=" * 60)

        print("[CORE ERROR]")

        print("Type:", type(error).__name__)

        print("Message:", str(error))

        print("Details:", repr(error))

        print("=" * 60)

        traceback.print_exc()


        return {

            "success": False,

            "reply": (
                "Sir, JARVIS Core मध्ये error आला."
            ),

            "message": (
                "Sir, JARVIS Core मध्ये error आला."
            ),

            "local": False,

            "web": False,

            "sleeping": jarvis_sleeping,

            "core": True,

            "error": repr(error),

        }


    # =====================================================
    # INVALID CORE RESPONSE
    # =====================================================

    if not isinstance(result, dict):

        print(
            "[MAIN] Invalid Core response:",
            repr(result)
        )


        return {

            "success": False,

            "reply": (
                "Sir, Core कडून invalid response मिळाला."
            ),

            "message": (
                "Sir, Core कडून invalid response मिळाला."
            ),

            "local": False,

            "web": False,

            "sleeping": jarvis_sleeping,

            "core": True,

        }


    # =====================================================
    # CORE RESULT TYPE
    # =====================================================

    result_type = str(
        result.get(
            "type",
            "chat"
        )
    ).strip().lower()


    print(
        "[MAIN CORE TYPE]:",
        result_type
    )


    # =====================================================
    # WEB RESULT
    # =====================================================

    if result_type == "web":

        web_message = str(

            result.get(
                "message",
                message
            )

            or

            message

        ).strip()


        return {

            "success": True,

            "reply": None,

            "message": web_message,

            "local": False,

            "web": True,

            "sleeping": jarvis_sleeping,

            "route": result.get(
                "route"
            ),

            "context": result.get(
                "context",
                ""
            ),

            "core": True,

        }


    # =====================================================
    # CORE ERROR
    # =====================================================

    if result_type == "error":

        error_message = str(

            result.get(

                "message",

                "AI response generate करण्यात error आला."

            )

            or

            "AI response generate करण्यात error आला."

        ).strip()


        return {

            "success": False,

            "reply": error_message,

            "message": error_message,

            "local": False,

            "web": False,

            "sleeping": jarvis_sleeping,

            "route": result.get(
                "route"
            ),

            "error": result.get(
                "error"
            ),

            "core": True,

        }


    # =====================================================
    # CHAT RESPONSE
    # =====================================================

    reply = str(

        result.get(
            "message",
            ""
        )

        or

        ""

    ).strip()


    if not reply:

        reply = (
            "Sir, मला response मिळाला नाही."
        )


    return {

        "success": True,

        "reply": reply,

        "message": reply,

        "local": False,

        "web": False,

        "sleeping": jarvis_sleeping,

        "route": result.get(
            "route"
        ),

        "context": result.get(
            "context",
            ""
        ),

        "model": result.get(
            "model"
        ),

        "core": True,

    }


# =========================================================
# MEMORY - REMEMBER
# =========================================================

@app.post("/memory/remember")
async def remember(
    request: MemoryRequest
):

    if jarvis_core is None:

        return {

            "success": False,

            "message": (
                "JARVIS Core unavailable."
            ),

        }


    try:

        role = str(
            request.role or ""
        ).strip()


        content = str(
            request.content or ""
        ).strip()


        if not role or not content:

            return {

                "success": False,

                "message": (
                    "Role आणि content आवश्यक आहेत."
                ),

            }


        jarvis_core.remember(

            role,

            content

        )


        return {

            "success": True,

            "message": "Memory saved.",

        }


    except Exception as error:

        print(
            "[MEMORY SAVE ERROR]:",
            repr(error)
        )

        traceback.print_exc()


        return {

            "success": False,

            "message": (
                "Memory save failed."
            ),

            "error": repr(error),

        }


# =========================================================
# MEMORY - CLEAR
# =========================================================

@app.post("/memory/clear")
async def clear_memory():

    if jarvis_core is None:

        return {

            "success": False,

            "message": (
                "JARVIS Core unavailable."
            ),

        }


    try:

        success = (
            jarvis_core.clear_memory()
        )


        return {

            "success": bool(success),

            "message": (

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

        traceback.print_exc()


        return {

            "success": False,

            "message": (
                "Memory clear failed."
            ),

            "error": repr(error),

        }


# =========================================================
# STARTUP
# =========================================================

@app.on_event("startup")
async def startup_event():

    print()
    print("=" * 60)

    print(
        "             JARVIS 4.0 BACKEND"
    )

    print("=" * 60)

    print(
        "[STARTUP] Backend:",
        BACKEND_DIR
    )

    print(
        "[STARTUP] Core:",
        get_core_status()
    )

    print(
        "[STARTUP] Router:",
        jarvis_router is not None
    )

    print(
        "[STARTUP] Commands:",
        handle_local_command is not None
    )

    print(
        "[STARTUP] Groq:",
        get_groq_status()
    )

    print(
        "[STARTUP] Model:",
        get_groq_model()
    )

    print("=" * 60)

    print(
        "[STARTUP] JARVIS 4.0 READY."
    )

    print("=" * 60)

    print()


# =========================================================
# SHUTDOWN
# =========================================================

@app.on_event("shutdown")
async def shutdown_event():

    print()
    print(
        "[JARVIS] Backend shutting down..."
    )

    print(
        "[JARVIS] Goodbye Sir."
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


    PORT = int(
        os.getenv(
            "SERVER_PORT",
            "8000"
        )
    )


    print()
    print(
        "[JARVIS] Starting server..."
    )

    print(
        f"[JARVIS] URL: http://127.0.0.1:{PORT}"
    )

    print()


    uvicorn.run(

        "main:app",

        host=HOST,

        port=PORT,

        reload=False,

    )