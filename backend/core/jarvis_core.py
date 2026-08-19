"""
JARVIS CORE

Central intelligence layer for JARVIS 4.0.

Responsibilities:
- Conversation processing
- Memory integration
- Router integration
- Groq AI integration
- Conversation context
- Web query routing
- Marathi / Hindi / English support
"""

import re


# =========================================================
# IMPORTS
# =========================================================

from memory.memory import JarvisMemory
from core.router import jarvis_router
from ai.groq import jarvis_groq


# =========================================================
# JARVIS CORE
# =========================================================

class JarvisCore:

    def __init__(self):

        self.name = "JARVIS Core"
        self.version = "1.0"

        # -----------------------------------------------
        # Components
        # -----------------------------------------------

        self.memory = JarvisMemory()

        self.router = jarvis_router

        self.groq = jarvis_groq

        # -----------------------------------------------
        # Context
        # -----------------------------------------------

        self.context_limit = 12

        self.conversation_context = {
            "topic": "",
            "destination": "",
            "source": "",
            "duration": "",
        }

        print(
            "[CORE] JARVIS Core initialized."
        )


    # =====================================================
    # NORMALIZE
    # =====================================================

    def normalize(self, text: str):

        text = str(
            text or ""
        ).strip().lower()

        text = text.replace(
            "’",
            "'"
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text


    # =====================================================
    # WEB KEYWORDS
    # =====================================================

    WEB_KEYWORDS = [

        # English
        "latest",
        "today",
        "current",
        "now",
        "recent",
        "news",
        "breaking",
        "live",
        "price",
        "rate",
        "weather",
        "temperature",

        # Market
        "sensex",
        "nifty",
        "bank nifty",
        "banknifty",
        "share market",
        "stock market",
        "bse",
        "nse",

        # Roman
        "aaj",
        "ata",
        "sadhya",
        "navin batmya",
        "tajya batmya",
        "bhav",
        "dar",
        "havaman",

        # Marathi
        "आज",
        "आत्ता",
        "सध्या",
        "ताज्या बातम्या",
        "बातम्या",
        "भाव",
        "दर",
        "हवामान",
        "शेअर बाजार",
        "सेन्सेक्स",
        "निफ्टी",

        # Hindi
        "अभी",
        "ताज़ा खबर",
        "ताजा खबर",
        "समाचार",
        "मौसम",
        "शेयर बाजार",
    ]


    # =====================================================
    # WEB QUERY DETECTION
    # =====================================================

    def is_web_query(
        self,
        message: str
    ):

        value = self.normalize(
            message
        )

        return any(
            keyword.lower() in value
            for keyword in self.WEB_KEYWORDS
        )


    # =====================================================
    # GET MEMORY
    # =====================================================

    def get_memory(self):

        try:

            memory = self.memory.get_recent(
                limit=self.context_limit
            )

            if not memory:
                return []

            return memory[
                -self.context_limit:
            ]

        except Exception as error:

            print(
                "[CORE MEMORY ERROR]:",
                repr(error)
            )

            return []


    # =====================================================
    # SAVE USER MESSAGE
    # =====================================================

    def save_user_message(
        self,
        message: str
    ):

        try:

            self.memory.remember_short_term(
                "user",
                message
            )

        except Exception as error:

            print(
                "[CORE USER MEMORY ERROR]:",
                repr(error)
            )


    # =====================================================
    # SAVE ASSISTANT MESSAGE
    # =====================================================

    def save_assistant_message(
        self,
        message: str
    ):

        try:

            self.memory.remember_short_term(
                "assistant",
                message
            )

        except Exception as error:

            print(
                "[CORE ASSISTANT MEMORY ERROR]:",
                repr(error)
            )


    # =====================================================
    # BUILD CONTEXT
    # =====================================================

    def build_context(self):

        memory = self.get_memory()

        lines = []


        # -----------------------------------------------
        # Conversation context
        # -----------------------------------------------

        context = self.conversation_context

        if any(
            value
            for value in context.values()
        ):

            lines.append(
                "ACTIVE CONVERSATION CONTEXT:"
            )

            if context.get("topic"):

                lines.append(
                    f"Topic: {context['topic']}"
                )

            if context.get("destination"):

                lines.append(
                    f"Destination: {context['destination']}"
                )

            if context.get("source"):

                lines.append(
                    f"Starting location: {context['source']}"
                )

            if context.get("duration"):

                lines.append(
                    f"Trip duration: {context['duration']}"
                )

            lines.append("")


        # -----------------------------------------------
        # Recent memory
        # -----------------------------------------------

        if memory:

            lines.append(
                "RECENT CONVERSATION:"
            )

            for item in memory:

                if not isinstance(
                    item,
                    dict
                ):
                    continue

                role = str(
                    item.get(
                        "role",
                        ""
                    )
                ).strip()

                content = str(
                    item.get(
                        "content",
                        ""
                    )
                ).strip()

                if not content:
                    continue

                lines.append(
                    f"{role}: {content}"
                )


        return "\n".join(lines)


    # =====================================================
    # UPDATE CONTEXT
    # =====================================================

    def update_context(
        self,
        message: str
    ):

        value = self.normalize(
            message
        )

        # -----------------------------------------------
        # Simple topic detection
        # -----------------------------------------------

        travel_words = [

            "travel",
            "trip",
            "tour",
            "visit",
            "प्रवास",
            "फिरायला",
            "जायचं",
            "जायचे",
            "जाना है",
            "घूमने",
        ]

        if any(
            word in value
            for word in travel_words
        ):

            self.conversation_context[
                "topic"
            ] = "Travel"


        # -----------------------------------------------
        # Duration
        # -----------------------------------------------

        duration = re.search(

            r"(\d+)\s*"
            r"(days?|day|दिवस|दिवसांचा)",

            value,

            flags=re.IGNORECASE
        )

        if duration:

            self.conversation_context[
                "duration"
            ] = (
                duration.group(1)
                + " days"
            )


    # =====================================================
    # RESTORE CONTEXT
    # =====================================================

    def restore_context(
        self,
        memory
    ):

        if not memory:
            return

        for item in memory:

            if not isinstance(
                item,
                dict
            ):
                continue

            if item.get("role") != "user":
                continue

            content = str(
                item.get(
                    "content",
                    ""
                )
            ).strip()

            if content:

                self.update_context(
                    content
                )


    # =====================================================
    # PROCESS
    # =====================================================

    async def process(
        self,
        message: str
    ):

        message = str(
            message or ""
        ).strip()


        # -----------------------------------------------
        # Empty
        # -----------------------------------------------

        if not message:

            return {

                "type": "error",

                "message":
                    "Empty request",

                "memory":
                    self.get_memory(),

                "context":
                    self.build_context(),

            }


        # -----------------------------------------------
        # Save user
        # -----------------------------------------------

        self.save_user_message(
            message
        )


        # -----------------------------------------------
        # Restore context
        # -----------------------------------------------

        memory = self.get_memory()

        self.restore_context(
            memory
        )

        self.update_context(
            message
        )


        # -----------------------------------------------
        # Context
        # -----------------------------------------------

        context = self.build_context()


        print()
        print(
            "[CORE]"
        )

        print(
            "Message:",
            message
        )

        print(
            "Context length:",
            len(context)
        )


        # =================================================
        # ROUTER
        # =================================================

        try:

            route_result = self.router.auto_route(
                message
            )

        except Exception as error:

            print(
                "[CORE ROUTER ERROR]:",
                repr(error)
            )

            route_result = {

                "route":
                    "web"
                    if self.is_web_query(message)
                    else "chat",

                "message":
                    message,

                "reason":
                    "fallback"

            }


        route = route_result.get(
            "route",
            "chat"
        )


        print(
            "[CORE ROUTE]:",
            route
        )


        # =================================================
        # WEB
        # =================================================

        if route == "web":

            return {

                "type": "web",

                "message":
                    message,

                "memory":
                    self.get_memory(),

                "context":
                    context,

                "route":
                    route_result,

            }


        # =================================================
        # GROQ
        # =================================================

        try:

            groq_result = await self.groq.chat(

                message=message,

                context=context

            )

        except Exception as error:

            print(
                "[CORE GROQ ERROR]:",
                repr(error)
            )

            return {

                "type": "error",

                "message":
                    "Groq AI response generate करताना error आला.",

                "error":
                    repr(error),

                "memory":
                    self.get_memory(),

                "context":
                    context,

                "route":
                    route_result,

            }


        # =================================================
        # GROQ FAILURE
        # =================================================

        if not groq_result.get(
            "success",
            False
        ):

            return {

                "type": "error",

                "message":
                    groq_result.get(

                        "message",

                        "AI response generate करण्यात error आला."

                    ),

                "memory":
                    self.get_memory(),

                "context":
                    context,

                "route":
                    route_result,

                "groq":
                    groq_result,

            }


        # =================================================
        # RESPONSE
        # =================================================

        response_message = str(

            groq_result.get(
                "message",
                ""
            )

        ).strip()


        # -----------------------------------------------
        # Save response
        # -----------------------------------------------

        if response_message:

            self.save_assistant_message(
                response_message
            )


        # =================================================
        # FINAL
        # =================================================

        return {

            "type":
                "chat",

            "message":
                response_message,

            "memory":
                self.get_memory(),

            "context":
                self.build_context(),

            "route":
                route_result,

            "model":
                groq_result.get(
                    "model",
                    getattr(
                        self.groq,
                        "model",
                        ""
                    )
                ),

        }


    # =====================================================
    # REMEMBER
    # =====================================================

    def remember(
        self,
        role: str,
        content: str
    ):

        try:

            self.memory.remember_short_term(
                role,
                content
            )

            return True

        except Exception as error:

            print(
                "[CORE REMEMBER ERROR]:",
                repr(error)
            )

            return False


    # =====================================================
    # CLEAR MEMORY
    # =====================================================

    def clear_memory(self):

        try:

            if hasattr(
                self.memory,
                "clear_short_term"
            ):

                self.memory.clear_short_term()


            self.conversation_context = {

                "topic": "",

                "destination": "",

                "source": "",

                "duration": "",

            }

            return True

        except Exception as error:

            print(
                "[CORE CLEAR MEMORY ERROR]:",
                repr(error)
            )

            return False


    # =====================================================
    # STATUS
    # =====================================================

    def status(self):

        return {

            "name":
                self.name,

            "version":
                self.version,

            "memory":
                self.memory is not None,

            "router":
                self.router is not None,

            "groq":
                (
                    self.groq is not None
                    and self.groq.is_available()
                ),

        }


# =========================================================
# SINGLE CORE INSTANCE
# =========================================================

try:

    jarvis_core = JarvisCore()

    print(
        "[CORE] JARVIS Core ready."
    )

except Exception as error:

    print(
        "[CORE INIT ERROR]:",
        repr(error)
    )

    jarvis_core = None