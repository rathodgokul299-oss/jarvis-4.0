"""
JARVIS 4.0 - CENTRAL CORE

Responsibilities:
- Conversation routing
- SQLite memory
- Recent conversation context
- Groq AI chat
- Tavily web search
- Compact web memory
- Marathi / Hindi / English support
"""

import re


# =========================================================
# IMPORTS
# =========================================================

from memory.memory import JarvisMemory
from core.router import jarvis_router
from ai.groq import jarvis_groq
from web_search import create_web_search_engine


# =========================================================
# JARVIS CORE
# =========================================================

class JarvisCore:

    def __init__(self):

        self.name = "JARVIS Core"
        self.version = "2.1"

        # -------------------------------------------------
        # MEMORY
        # -------------------------------------------------

        self.memory = JarvisMemory()

        self.context_limit = 12


        # -------------------------------------------------
        # ROUTER
        # -------------------------------------------------

        self.router = jarvis_router


        # -------------------------------------------------
        # GROQ
        # -------------------------------------------------

        self.groq = jarvis_groq


        # -------------------------------------------------
        # WEB SEARCH
        # -------------------------------------------------

        try:

            self.web_search = create_web_search_engine(

                groq_client=(
                    self.groq.client
                    if self.groq
                    else None
                ),

                groq_model=(
                    self.groq.model
                    if self.groq
                    else ""
                ),

            )

            print(
                "[CORE] Web Search initialized."
            )

        except Exception as error:

            print(
                "[CORE] Web Search initialization ERROR:",
                repr(error)
            )

            self.web_search = None


        # -------------------------------------------------
        # CONVERSATION CONTEXT
        # -------------------------------------------------

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

    def normalize(
        self,
        text: str
    ):

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

        # Search
        "search",
        "google",
        "online",
        "internet",
        "look up",

        # Market
        "sensex",
        "nifty",
        "bank nifty",
        "banknifty",
        "share market",
        "stock market",
        "bse",
        "nse",

        # Roman Marathi / Hindi
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


        if not value:

            return False


        return any(

            keyword.lower() in value

            for keyword in self.WEB_KEYWORDS

        )


    # =====================================================
    # GET RECENT MEMORY
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
                "[CORE MEMORY READ ERROR]:",
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

            return self.memory.remember_short_term(

                "user",

                message

            )

        except Exception as error:

            print(
                "[CORE USER MEMORY ERROR]:",
                repr(error)
            )

            return False


    # =====================================================
    # SAVE ASSISTANT MESSAGE
    # =====================================================

    def save_assistant_message(
        self,
        message: str
    ):

        try:

            return self.memory.remember_short_term(

                "assistant",

                message

            )

        except Exception as error:

            print(
                "[CORE ASSISTANT MEMORY ERROR]:",
                repr(error)
            )

            return False


    # =====================================================
    # SAVE COMPACT WEB MEMORY
    # =====================================================

    def save_web_memory(
        self,
        query: str,
        answer: str
    ):

        try:

            query = str(
                query or ""
            ).strip()


            answer = str(
                answer or ""
            ).strip()


            if not query or not answer:

                return False


            # -------------------------------------------------
            # Only save a compact snapshot.
            # Frontend still receives the full answer.
            # -------------------------------------------------

            compact_answer = answer[:700].strip()


            if len(answer) > 700:

                compact_answer += "..."


            memory_text = (

                "[WEB SEARCH]\n"

                f"Query: {query}\n"

                f"Answer: {compact_answer}"

            )


            success = (
                self.memory.remember_short_term(
                    "assistant",
                    memory_text
                )
            )


            if success:

                print(
                    "[CORE] Compact web memory saved."
                )


            return success


        except Exception as error:

            print(
                "[CORE WEB MEMORY ERROR]:",
                repr(error)
            )

            return False


    # =====================================================
    # BUILD CONTEXT
    # =====================================================

    def build_context(self):

        memory = self.get_memory()

        lines = []


        # -------------------------------------------------
        # Active conversation context
        # -------------------------------------------------

        context = (
            self.conversation_context
        )


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


        # -------------------------------------------------
        # Recent conversation
        # -------------------------------------------------

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


        return "\n".join(
            lines
        )


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


        # -------------------------------------------------
        # Travel
        # -------------------------------------------------

        travel_words = [

            "travel",
            "trip",
            "tour",
            "visit",
            "destination",

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


        # -------------------------------------------------
        # Duration
        # -------------------------------------------------

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

                +
                " days"

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


            if item.get(
                "role"
            ) != "user":

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
    # PROCESS WEB QUERY
    # =====================================================

    async def process_web_query(
        self,
        message: str
    ):

        print(
            "[CORE] Processing web query:",
            message
        )


        # -------------------------------------------------
        # Check engine
        # -------------------------------------------------

        if self.web_search is None:

            return {

                "type":
                    "error",

                "message":
                    "Sir, web search engine available नाही.",

                "route":
                    {
                        "route":
                            "web",

                        "reason":
                            "web_engine_missing"

                    },

            }


        # -------------------------------------------------
        # Search
        # -------------------------------------------------

        try:

            answer = self.web_search.answer(
                message
            )


        except Exception as error:

            print(
                "[CORE WEB ERROR]:",
                repr(error)
            )


            return {

                "type":
                    "error",

                "message":
                    "Sir, web search करताना problem आली.",

                "error":
                    repr(error),

                "route":
                    {
                        "route":
                            "web",

                        "reason":
                            "web_search_error"

                    },

            }


        answer = str(
            answer or ""
        ).strip()


        # -------------------------------------------------
        # No answer
        # -------------------------------------------------

        if not answer:

            answer = (
                "Sir, मला web वरून योग्य answer मिळाला नाही."
            )


        # -------------------------------------------------
        # IMPORTANT:
        # Save only compact web memory.
        # -------------------------------------------------

        self.save_web_memory(

            query=
                message,

            answer=
                answer

        )


        # -------------------------------------------------
        # Return FULL answer
        # -------------------------------------------------

        return {

            "type":
                "web",

            "message":
                answer,

            "memory":
                self.get_memory(),

            "context":
                self.build_context(),

            "route":
                {
                    "route":
                        "web",

                    "message":
                        message,

                    "reason":
                        "fresh_web_query",

                },

        }


    # =====================================================
    # MAIN PROCESS
    # =====================================================

    async def process(
        self,
        message: str
    ):

        message = str(
            message or ""
        ).strip()


        # -------------------------------------------------
        # Empty
        # -------------------------------------------------

        if not message:

            return {

                "type":
                    "error",

                "message":
                    "Empty request",

                "memory":
                    self.get_memory(),

                "context":
                    self.build_context(),

            }


        # -------------------------------------------------
        # Save user
        # -------------------------------------------------

        self.save_user_message(
            message
        )


        # -------------------------------------------------
        # Memory
        # -------------------------------------------------

        memory = self.get_memory()


        self.restore_context(
            memory
        )


        self.update_context(
            message
        )


        # -------------------------------------------------
        # Context
        # -------------------------------------------------

        context = self.build_context()


        print()
        print(
            "========================================"
        )

        print(
            "[CORE REQUEST]"
        )

        print(
            "Message:",
            message
        )

        print(
            "Context:",
            len(context),
            "characters"
        )

        print(
            "Web:",
            self.is_web_query(
                message
            )
        )

        print(
            "========================================"
        )


        # =================================================
        # ROUTER
        # =================================================

        try:

            route_result = self.router.route(

                message,

                is_web=
                    self.is_web_query(
                        message
                    )

            )


        except Exception as error:

            print(
                "[CORE ROUTER ERROR]:",
                repr(error)
            )


            route_result = {

                "route":

                    (
                        "web"
                        if self.is_web_query(
                            message
                        )
                        else
                        "chat"
                    ),

                "message":
                    message,

                "reason":
                    "fallback",

            }


        route = str(

            route_result.get(
                "route",
                "chat"
            )

        ).strip().lower()


        print(
            "[CORE ROUTE]:",
            route
        )


        # =================================================
        # WEB ROUTE
        # =================================================

        if route == "web":

            return await self.process_web_query(
                message
            )


        # =================================================
        # GROQ CHECK
        # =================================================

        if self.groq is None:

            return {

                "type":
                    "error",

                "message":
                    "Sir, Groq AI available नाही.",

                "memory":
                    self.get_memory(),

                "context":
                    context,

                "route":
                    route_result,

            }


        # =================================================
        # NORMAL GROQ CHAT
        # =================================================

        try:

            groq_result = await self.groq.chat(

                message=
                    message,

                context=
                    context,

            )


        except Exception as error:

            print(
                "[CORE GROQ ERROR]:",
                repr(error)
            )


            return {

                "type":
                    "error",

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

                "type":
                    "error",

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

            or

            ""

        ).strip()


        if not response_message:

            response_message = (
                "Sir, मला योग्य response मिळाला नाही."
            )


        # -------------------------------------------------
        # Save normal assistant response
        # -------------------------------------------------

        self.save_assistant_message(
            response_message
        )


        # =================================================
        # FINAL CHAT
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

            return self.memory.remember_short_term(

                role,

                content

            )


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

        groq_ok = False

        web_ok = False


        # -------------------------------------------------
        # Groq
        # -------------------------------------------------

        try:

            if self.groq:

                groq_ok = (
                    self.groq.is_available()
                )

        except Exception:

            groq_ok = False


        # -------------------------------------------------
        # Web
        # -------------------------------------------------

        try:

            if self.web_search:

                web_ok = (
                    self.web_search.is_available()
                )

        except Exception:

            web_ok = False


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
                groq_ok,

            "web_search":
                web_ok,

        }


# =========================================================
# SINGLE INSTANCE
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