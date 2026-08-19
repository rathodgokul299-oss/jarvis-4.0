"""
JARVIS GROQ AI
================

Responsibilities:
- Groq API connection
- AI chat
- Marathi / Hindi / English support
- Roman Marathi / Hindi support
- Conversation context support
- Safe error handling
"""

import os
from typing import Optional

from groq import Groq

import os
from typing import Optional

from dotenv import load_dotenv
from groq import Groq


# =========================================================
# LOAD BACKEND .ENV
# =========================================================

BACKEND_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

ENV_FILE = os.path.join(
    BACKEND_DIR,
    ".env"
)

load_dotenv(ENV_FILE)


# =========================================================
# ENVIRONMENT
# =========================================================

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
    ""
).strip()

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
).strip()


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are JARVIS, an intelligent personal AI assistant.

You are helpful, natural, concise and conversational.

LANGUAGE RULES:
- Understand English.
- Understand Hindi.
- Understand Marathi.
- Understand Roman Marathi.
- Understand Roman Hindi.
- Reply in the same language/style used by the user.
- If the user writes Marathi in Roman script, reply naturally in Roman Marathi.
- If the user writes Marathi in Devanagari, reply in Marathi.
- Do not unnecessarily translate the user's message.

CONVERSATION:
- Maintain continuity using the supplied conversation context.
- Use relevant previous information.
- Do not ask the user to repeat information already available in context.
- Answer naturally.

IMPORTANT:
- Never claim that you performed an action unless the system actually performed it.
- Do not pretend to open applications, websites or files.
- Local commands are handled separately by JARVIS.
- Keep normal answers concise unless the user asks for details.

PERSONALITY:
- Calm.
- Intelligent.
- Respectful.
- Natural.
- Assistant-like.
- You may address the user as "Sir" naturally when appropriate.
"""


# =========================================================
# JARVIS GROQ
# =========================================================

class JarvisGroq:

    def __init__(self):

        self.name = "JARVIS Groq AI"
        self.version = "3.0"

        self.api_key = GROQ_API_KEY
        self.model = GROQ_MODEL

        self.client: Optional[Groq] = None

        self._initialize()


    # =====================================================
    # INITIALIZE
    # =====================================================

    def _initialize(self):

        if not self.api_key:

            print(
                "[GROQ] ERROR: GROQ_API_KEY missing."
            )

            return

        try:

            self.client = Groq(
                api_key=self.api_key
            )

            print(
                "[GROQ] Client initialized successfully."
            )

            print(
                "[GROQ] Model:",
                self.model
            )

        except Exception as error:

            self.client = None

            print(
                "[GROQ] Initialization ERROR:",
                repr(error)
            )


    # =====================================================
    # STATUS
    # =====================================================

    def is_available(self):

        return self.client is not None


    # =====================================================
    # BUILD MESSAGES
    # =====================================================

    def build_messages(
        self,
        message: str,
        context: str = ""
    ):

        messages = [

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }

        ]

        if context:

            messages.append(

                {
                    "role": "system",
                    "content": (
                        "CONVERSATION CONTEXT:\n\n"
                        + str(context)
                    )
                }

            )

        messages.append(

            {
                "role": "user",
                "content": str(message)
            }

        )

        return messages


    # =====================================================
    # CHAT
    # =====================================================

    async def chat(
        self,
        message: str,
        context: str = ""
    ):

        message = str(
            message or ""
        ).strip()


        # -------------------------------------------------
        # EMPTY
        # -------------------------------------------------

        if not message:

            return {

                "success": False,

                "message":
                    "Sir, message रिकामा आहे.",

                "error":
                    "empty_message"

            }


        # -------------------------------------------------
        # CLIENT
        # -------------------------------------------------

        if self.client is None:

            return {

                "success": False,

                "message":
                    "Sir, Groq API client उपलब्ध नाही.",

                "error":
                    "groq_client_unavailable",

                "model":
                    self.model

            }


        # -------------------------------------------------
        # MESSAGES
        # -------------------------------------------------

        try:

            messages = self.build_messages(
                message=message,
                context=context
            )

        except Exception as error:

            print(
                "[GROQ] Message build ERROR:",
                repr(error)
            )

            return {

                "success": False,

                "message":
                    "Sir, Groq request तयार करताना error आला.",

                "error":
                    repr(error)

            }


        # -------------------------------------------------
        # DEBUG
        # -------------------------------------------------

        print()
        print(
            "========================================"
        )
        print(
            "[GROQ REQUEST]"
        )
        print(
            "Model:",
            self.model
        )
        print(
            "Message:",
            message
        )
        print(
            "Context:",
            len(context or ""),
            "characters"
        )
        print(
            "========================================"
        )


        # =================================================
        # API REQUEST
        # =================================================

        try:

            response = (

                self.client
                .chat
                .completions
                .create(

                    model=self.model,

                    messages=messages,

                    temperature=0.7,

                    max_completion_tokens=1024,

                    stream=False

                )

            )


            # -------------------------------------------------
            # RESPONSE CHECK
            # -------------------------------------------------

            if response is None:

                return {

                    "success": False,

                    "message":
                        "Sir, Groq कडून response मिळाला नाही.",

                    "error":
                        "empty_response",

                    "model":
                        self.model

                }


            if not getattr(
                response,
                "choices",
                None
            ):

                print(
                    "[GROQ] No choices returned."
                )

                return {

                    "success": False,

                    "message":
                        "Sir, Groq कडून valid response मिळाला नाही.",

                    "error":
                        "no_choices",

                    "model":
                        self.model

                }


            # -------------------------------------------------
            # CONTENT
            # -------------------------------------------------

            content = (

                response
                .choices[0]
                .message
                .content

            )

            content = str(
                content or ""
            ).strip()


            # -------------------------------------------------
            # EMPTY CONTENT
            # -------------------------------------------------

            if not content:

                return {

                    "success": False,

                    "message":
                        "Sir, Groq ने रिकामा response दिला.",

                    "error":
                        "empty_content",

                    "model":
                        self.model

                }


            # -------------------------------------------------
            # SUCCESS
            # -------------------------------------------------

            print(
                "[GROQ SUCCESS]"
            )

            print(
                "[GROQ RESPONSE]:",
                content
            )

            print(
                "========================================"
            )

            return {

                "success": True,

                "message": content,

                "model": self.model

            }


        # =================================================
        # API ERROR
        # =================================================

        except Exception as error:

            print()
            print(
                "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            )

            print(
                "[GROQ API ERROR]"
            )

            print(
                "Type:",
                type(error).__name__
            )

            print(
                "Message:",
                str(error)
            )

            print(
                "Model:",
                self.model
            )

            print(
                "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            )

            print()

            return {

                "success": False,

                "message":
                    "Sorry Sir, Groq AI response generate करताना error आला.",

                "error":
                    repr(error),

                "error_type":
                    type(error).__name__,

                "model":
                    self.model

            }


# =========================================================
# SINGLE INSTANCE
# =========================================================

jarvis_groq = JarvisGroq()