"""
JARVIS ROUTER

Central routing layer for JARVIS.

Responsibilities:
- Normal chat detection
- Web/current query detection
- Clean routing result
- Simple and reliable architecture
"""


# =========================================================
# JARVIS ROUTER
# =========================================================

class JarvisRouter:

    def __init__(self):

        self.name = "JARVIS Router"
        self.version = "2.0"


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

        # Search / web
        "search",
        "google",
        "look up",
        "find online",
        "on internet",
        "internet",

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
    # NORMALIZE
    # =====================================================

    def normalize(self, text: str) -> str:

        text = str(text or "").strip().lower()

        text = text.replace("’", "'")
        text = text.replace("“", '"')
        text = text.replace("”", '"')

        return " ".join(text.split())


    # =====================================================
    # CHECK WEB QUERY
    # =====================================================

    def is_web_query(self, message: str) -> bool:

        value = self.normalize(message)

        if not value:
            return False

        return any(
            keyword in value
            for keyword in self.WEB_KEYWORDS
        )


    # =====================================================
    # ROUTE
    # =====================================================

    def route(
        self,
        message: str,
        is_web: bool = False
    ):

        message = str(
            message or ""
        ).strip()


        # -------------------------------------------------
        # EMPTY
        # -------------------------------------------------

        if not message:

            return {
                "route": "error",
                "message": "Empty request",
                "reason": "empty_message"
            }


        # -------------------------------------------------
        # WEB
        # -------------------------------------------------

        if is_web:

            return {
                "route": "web",
                "message": message,
                "reason": "web_query"
            }


        # -------------------------------------------------
        # NORMAL CHAT
        # -------------------------------------------------

        return {
            "route": "chat",
            "message": message,
            "reason": "normal_conversation"
        }


    # =====================================================
    # AUTO ROUTE
    # =====================================================

    def auto_route(self, message: str):

        web = self.is_web_query(message)

        return self.route(
            message=message,
            is_web=web
        )


# =========================================================
# SINGLE ROUTER INSTANCE
# =========================================================

jarvis_router = JarvisRouter()