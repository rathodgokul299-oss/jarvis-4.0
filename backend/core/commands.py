"""
JARVIS COMMAND ENGINE

Local command execution layer.

Responsibilities:
- Chrome
- Calculator
- YouTube
- YouTube search
- YouTube play
- Sleep / Wake
- Marathi / Hindi / English / Roman commands

IMPORTANT:
This file executes LOCAL commands only.
AI conversation and web routing are handled separately.
"""

import os
import re
import subprocess
import threading
import time
import urllib.parse
import webbrowser


# =========================================================
# OPTIONAL SELENIUM
# =========================================================

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    SELENIUM_AVAILABLE = True

except ImportError:
    SELENIUM_AVAILABLE = False
    print("[COMMANDS] Selenium not installed.")


# =========================================================
# GLOBAL STATE
# =========================================================

youtube_driver = None
youtube_lock = threading.Lock()


# =========================================================
# NORMALIZE
# =========================================================

def normalize_text(text: str) -> str:

    text = str(text or "").strip().lower()

    text = text.replace("’", "'")
    text = text.replace("“", '"')
    text = text.replace("”", '"')

    text = re.sub(
        r"[.,!?।,:;]+",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# CLEAN COMMAND
# =========================================================

def clean_command(text: str) -> str:

    value = normalize_text(text)

    prefixes = [
        "hey jarvis ",
        "hey jarvis",
        "jarvis ",
        "jarvis",
    ]

    for prefix in prefixes:

        if value.startswith(prefix):

            value = value[len(prefix):].strip()
            break

    return value


# =========================================================
# CHROME PATHS
# =========================================================

def get_chrome_paths():

    return [

        r"C:\Program Files\Google\Chrome\Application\chrome.exe",

        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",

        os.path.expandvars(
            r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
        ),

    ]


# =========================================================
# OPEN CHROME
# =========================================================

def open_chrome() -> bool:

    try:

        print("[COMMAND] Opening Chrome...")

        for path in get_chrome_paths():

            if os.path.isfile(path):

                subprocess.Popen(
                    [path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                print(
                    "[CHROME] Started:",
                    path
                )

                return True


        # -------------------------------------------------
        # PATH / WINDOWS FALLBACK
        # -------------------------------------------------

        try:

            subprocess.Popen(
                ["chrome"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            print(
                "[CHROME] Started through PATH."
            )

            return True

        except Exception:

            pass


        # -------------------------------------------------
        # WINDOWS START FALLBACK
        # -------------------------------------------------

        try:

            subprocess.Popen(
                [
                    "cmd",
                    "/c",
                    "start",
                    "",
                    "chrome"
                ],
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            print(
                "[CHROME] Started through Windows shell."
            )

            return True

        except Exception:

            pass


        print(
            "[CHROME] Chrome executable not found."
        )

        return False


    except Exception as error:

        print(
            "[CHROME ERROR]:",
            repr(error)
        )

        return False


# =========================================================
# OPEN CALCULATOR
# =========================================================

def open_calculator() -> bool:

    try:

        print(
            "[COMMAND] Opening Calculator..."
        )

        subprocess.Popen(
            ["calc.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return True

    except Exception as error:

        print(
            "[CALCULATOR ERROR]:",
            repr(error)
        )

        return False


# =========================================================
# OPEN YOUTUBE
# =========================================================

def open_youtube() -> bool:

    try:

        print(
            "[COMMAND] Opening YouTube..."
        )

        result = webbrowser.open(
            "https://www.youtube.com"
        )

        return bool(result)

    except Exception as error:

        print(
            "[YOUTUBE OPEN ERROR]:",
            repr(error)
        )

        return False


# =========================================================
# YOUTUBE SEARCH
# =========================================================

def youtube_search(query: str) -> bool:

    query = str(query or "").strip()

    if not query:
        return False

    try:

        encoded = urllib.parse.quote_plus(
            query
        )

        url = (
            "https://www.youtube.com/results"
            "?search_query="
            + encoded
        )

        print(
            "[YOUTUBE SEARCH]:",
            query
        )

        result = webbrowser.open(url)

        return bool(result)

    except Exception as error:

        print(
            "[YOUTUBE SEARCH ERROR]:",
            repr(error)
        )

        return False


# =========================================================
# GET SELENIUM DRIVER
# =========================================================

def get_youtube_driver():

    global youtube_driver

    if not SELENIUM_AVAILABLE:
        return None

    try:

        if youtube_driver is not None:

            try:

                _ = youtube_driver.current_url

                return youtube_driver

            except Exception:

                youtube_driver = None


        options = Options()

        options.add_argument(
            "--start-maximized"
        )

        options.add_argument(
            "--disable-notifications"
        )

        options.add_argument(
            "--disable-infobars"
        )

        options.add_argument(
            "--disable-blink-features=AutomationControlled"
        )

        options.add_experimental_option(
            "excludeSwitches",
            ["enable-automation"]
        )

        options.add_experimental_option(
            "useAutomationExtension",
            False
        )

        youtube_driver = webdriver.Chrome(
            options=options
        )

        print(
            "[YOUTUBE] Selenium Chrome started."
        )

        return youtube_driver


    except Exception as error:

        print(
            "[YOUTUBE DRIVER ERROR]:",
            repr(error)
        )

        youtube_driver = None

        return None


# =========================================================
# CLOSE YOUTUBE DRIVER
# =========================================================

def close_youtube_driver():

    global youtube_driver

    try:

        if youtube_driver is not None:

            youtube_driver.quit()

    except Exception:
        pass

    youtube_driver = None


# =========================================================
# CLOSE YOUTUBE POPUPS
# =========================================================

def close_youtube_popups(driver):

    selectors = [

        "button[aria-label='Accept all']",

        "button[aria-label='Reject all']",

        "tp-yt-paper-button#dismiss-button",

        "button[aria-label*='Accept']",

        "button[aria-label*='Reject']",

    ]

    for selector in selectors:

        try:

            buttons = driver.find_elements(
                By.CSS_SELECTOR,
                selector
            )

            for button in buttons:

                try:

                    if button.is_displayed():

                        driver.execute_script(
                            "arguments[0].click();",
                            button
                        )

                        time.sleep(0.3)

                except Exception:
                    continue

        except Exception:
            continue


# =========================================================
# SKIP YOUTUBE ADS
# =========================================================

def skip_youtube_ads(driver):

    selectors = [

        "button.ytp-ad-skip-button",

        "button.ytp-ad-skip-button-modern",

        ".ytp-ad-skip-button",

        ".ytp-ad-skip-button-modern",

    ]

    end_time = time.time() + 20

    while time.time() < end_time:

        try:

            for selector in selectors:

                buttons = driver.find_elements(
                    By.CSS_SELECTOR,
                    selector
                )

                for button in buttons:

                    try:

                        if button.is_displayed():

                            driver.execute_script(
                                "arguments[0].click();",
                                button
                            )

                            print(
                                "[YOUTUBE] Advertisement skipped."
                            )

                            return True

                    except Exception:
                        continue

            time.sleep(0.5)

        except Exception:

            time.sleep(0.5)

    return False


# =========================================================
# YOUTUBE PLAY
# =========================================================

def youtube_play(query: str):

    query = str(query or "").strip()

    if not query:

        return (
            False,
            "song query missing"
        )


    # -----------------------------------------------------
    # WITHOUT SELENIUM
    # -----------------------------------------------------

    if not SELENIUM_AVAILABLE:

        youtube_search(query)

        return (
            False,
            "selenium not installed"
        )


    with youtube_lock:

        driver = get_youtube_driver()

        if driver is None:

            youtube_search(query)

            return (
                False,
                "selenium driver unavailable"
            )


        try:

            print(
                "[YOUTUBE] Playing:",
                query
            )

            driver.get(
                "https://www.youtube.com"
            )

            time.sleep(1.5)

            close_youtube_popups(
                driver
            )


            # -------------------------------------------------
            # SEARCH BOX
            # -------------------------------------------------

            search_box = WebDriverWait(
                driver,
                15
            ).until(

                EC.presence_of_element_located(
                    (
                        By.NAME,
                        "search_query"
                    )
                )
            )


            search_box.clear()

            search_box.send_keys(
                query
            )

            search_box.send_keys(
                Keys.ENTER
            )


            # -------------------------------------------------
            # WAIT RESULTS
            # -------------------------------------------------

            WebDriverWait(
                driver,
                15
            ).until(

                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "ytd-video-renderer"
                    )
                )
            )


            time.sleep(1)


            videos = driver.find_elements(
                By.CSS_SELECTOR,
                "ytd-video-renderer"
            )


            selected = None
            selected_title = ""


            # -------------------------------------------------
            # SELECT FIRST VALID VIDEO
            # -------------------------------------------------

            for video in videos:

                try:

                    link = video.find_element(
                        By.CSS_SELECTOR,
                        "a#video-title"
                    )

                    title = (
                        link.get_attribute("title")
                        or link.text
                        or ""
                    ).strip()


                    if title:

                        selected = link

                        selected_title = title

                        break

                except Exception:

                    continue


            if selected is None:

                return (
                    False,
                    "video not found"
                )


            print(
                "[YOUTUBE] Selected:",
                selected_title
            )


            # -------------------------------------------------
            # CLICK VIDEO
            # -------------------------------------------------

            driver.execute_script(
                """
                arguments[0].scrollIntoView({
                    block: 'center'
                });
                """,
                selected
            )

            time.sleep(0.5)


            try:

                selected.click()

            except Exception:

                driver.execute_script(
                    "arguments[0].click();",
                    selected
                )


            # -------------------------------------------------
            # WAIT VIDEO
            # -------------------------------------------------

            WebDriverWait(
                driver,
                15
            ).until(

                lambda d:
                "/watch" in d.current_url
            )


            time.sleep(1)


            # -------------------------------------------------
            # PLAY VIDEO
            # -------------------------------------------------

            try:

                driver.execute_script(
                    """
                    const video =
                        document.querySelector('video');

                    if (video) {
                        video.muted = false;
                        video.play().catch(() => {});
                    }
                    """
                )

            except Exception:
                pass


            # -------------------------------------------------
            # SKIP ADS
            # -------------------------------------------------

            threading.Thread(
                target=skip_youtube_ads,
                args=(driver,),
                daemon=True
            ).start()


            return (
                True,
                selected_title
            )


        except Exception as error:

            print(
                "[YOUTUBE PLAY ERROR]:",
                repr(error)
            )

            return (
                False,
                str(error)
            )


# =========================================================
# SONG QUERY EXTRACTION
# =========================================================

def extract_song_query(text: str) -> str:

    original = str(
        text or ""
    ).strip()

    value = clean_command(
        original
    )


    patterns = [

        r"^play\s+the\s+song\s+",

        r"^play\s+song\s+",

        r"^play\s+",

        r"^song\s+play\s+kar\s+",

        r"^song\s+play\s+",

        r"^gana\s+play\s+kar\s+",

        r"^gana\s+play\s+",

        r"^gana\s+chalu\s+kar\s+",

        r"^play\s+kar\s+",

        r"^प्ले\s+कर\s+",

        r"^प्ले\s+करा\s+",

        r"^गाणं\s+प्ले\s+कर\s+",

        r"^गाणे\s+प्ले\s+कर\s+",

        r"^गाना\s+प्ले\s+कर\s+",

        r"^गाणं\s+लाव\s+",

        r"^गाणे\s+लाव\s+",

        r"^गाना\s+लगा\s+",

        r"^गाणं\s+चालू\s+कर\s+",

        r"^गाणे\s+चालू\s+कर\s+",

    ]


    cleaned = value


    for pattern in patterns:

        cleaned = re.sub(
            pattern,
            "",
            cleaned,
            flags=re.IGNORECASE
        )


    cleaned = re.sub(
        r"\bplease\b",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = re.sub(
        r"\bpls\b",
        "",
        cleaned,
        flags=re.IGNORECASE
    )


    cleaned = re.sub(
        r"\s+(play|song|kar|kara|lav|laav|chalu)\s*$",
        "",
        cleaned,
        flags=re.IGNORECASE
    )


    cleaned = re.sub(
        r"\s+(कर|करा|लाव|लावा|चालू|चालु)\s*$",
        "",
        cleaned
    )


    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned
    ).strip()


    return cleaned or original


# =========================================================
# YOUTUBE PLAY COMMAND
# =========================================================

def is_youtube_play_command(text: str) -> bool:

    value = clean_command(text)

    generic = [

        "play",

        "play song",

        "song play",

        "song play kar",

        "gana play",

        "gana play kar",

        "gana chalu",

        "gana chalu kar",

        "song lav",

        "गाणं प्ले",

        "गाणं प्ले कर",

        "गाणे प्ले",

        "गाणे प्ले कर",

        "गाना प्ले",

        "गाना प्ले कर",

        "गाणं लाव",

        "गाणे लाव",

        "गाना लगा",

    ]


    if value in generic:
        return True


    patterns = [

        value.startswith("play "),

        value.startswith("song play "),

        value.startswith("gana play "),

        value.startswith("gana chalu "),

        value.startswith("गाणं लाव "),

        value.startswith("गाणे लाव "),

        value.startswith("गाना लगा "),

        value.startswith("गाणं प्ले "),

        value.startswith("गाणे प्ले "),

        value.startswith("गाना प्ले "),

    ]


    return any(patterns)


# =========================================================
# OPEN YOUTUBE COMMAND
# =========================================================

def is_open_youtube_command(text: str) -> bool:

    value = clean_command(text)

    commands = [

        "open youtube",

        "youtube open",

        "youtube ughad",

        "youtube ugad",

        "youtube open kar",

        "youtube kholo",

        "youtube khol",

        "youtube lagao",

        "youtube lava",

        "youtube lav",

        "ओपन यूट्यूब",

        "यूट्यूब ओपन",

        "यूट्यूब उघड",

        "यूट्यूब उघडा",

        "यूट्यूब खोल",

        "यूट्यूब लावा",

        "यूट्यूब लाव",

    ]

    return value in commands


# =========================================================
# YOUTUBE SEARCH COMMAND
# =========================================================

def is_youtube_search_command(text: str) -> bool:

    value = clean_command(text)

    return (

        value.startswith(
            "youtube search "
        )

        or

        value.startswith(
            "search youtube "
        )

        or

        value.startswith(
            "youtube var "
        )

        or

        value.startswith(
            "youtube वर "
        )

    )


# =========================================================
# CALCULATOR COMMAND
# =========================================================

def is_calculator_command(text: str) -> bool:

    value = clean_command(text)

    commands = [

        "open calculator",

        "calculator open",

        "calculator ughad",

        "calculator ugad",

        "calculator open kar",

        "calculator kholo",

        "calculator khol",

        "open calc",

        "calc open",

        "ओपन कॅल्क्युलेटर",

        "कॅल्क्युलेटर ओपन",

        "कॅल्क्युलेटर उघड",

        "कॅल्क्युलेटर उघडा",

        "ओपन कैलकुलेटर",

        "कैलकुलेटर खोल",

        "कैलकुलेटर ओपन",

    ]

    return value in commands


# =========================================================
# CHROME COMMAND
# =========================================================

def is_chrome_command(text: str) -> bool:

    value = clean_command(text)

    commands = [

        "open chrome",

        "chrome open",

        "chrome ughad",

        "chrome open kar",

        "chrome kholo",

        "chrome khol",

        "ओपन क्रोम",

        "क्रोम ओपन",

        "क्रोम उघड",

        "क्रोम उघडा",

        "क्रोम खोल",

    ]

    return value in commands


# =========================================================
# SLEEP COMMAND
# =========================================================

def is_sleep_command(text: str) -> bool:

    value = clean_command(text)

    commands = [

        "sleep",

        "go to sleep",

        "sleep jarvis",

        "jarvis sleep",

        "jarvis go to sleep",

        "स्लीप",

        "जार्विस स्लीप",

        "झोप",

        "झोप जा",

        "झोप जार्विस",

    ]

    return value in commands


# =========================================================
# WAKE COMMAND
# =========================================================

def is_wake_command(text: str) -> bool:

    value = clean_command(text)

    commands = [

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

    if value in commands:
        return True

    if "wake up jarvis" in value:
        return True

    if "jarvis wake up" in value:
        return True

    return False


# =========================================================
# COMMAND IDENTIFICATION
# =========================================================

def identify_command(text: str):

    value = clean_command(text)

    if is_wake_command(value):

        return "wake"


    if is_sleep_command(value):

        return "sleep"


    if is_youtube_play_command(value):

        return "youtube_play"


    if is_open_youtube_command(value):

        return "open_youtube"


    if is_youtube_search_command(value):

        return "youtube_search"


    if is_calculator_command(value):

        return "calculator"


    if is_chrome_command(value):

        return "chrome"


    return None


# =========================================================
# LOCAL COMMAND HANDLER
# =========================================================

def handle_local_command(
    original_text: str,
    sleeping: bool = False,
    whatsapp_handler=None
):

    text = clean_command(
        original_text
    )

    print(
        "[LOCAL COMMAND]:",
        text
    )


    # =====================================================
    # WAKE
    # =====================================================

    if is_wake_command(
        original_text
    ):

        return (
            True,
            "Ready Sir.",
            False
        )


    # =====================================================
    # SLEEP
    # =====================================================

    if is_sleep_command(
        original_text
    ):

        return (
            True,
            "Okay Sir, sleeping now.",
            True
        )


    # =====================================================
    # SLEEPING MODE
    # =====================================================

    if sleeping:

        return (
            True,
            None,
            True
        )


    # =====================================================
    # WHATSAPP
    # =====================================================

    if whatsapp_handler:

        try:

            handled, reply = (
                whatsapp_handler(
                    original_text
                )
            )

            if handled:

                return (
                    True,
                    reply,
                    sleeping
                )

        except Exception as error:

            print(
                "[WHATSAPP ERROR]:",
                repr(error)
            )

            return (
                True,
                "Sir, WhatsApp command मध्ये problem आली.",
                sleeping
            )


    # =====================================================
    # YOUTUBE PLAY
    # =====================================================

    if is_youtube_play_command(
        original_text
    ):

        query = extract_song_query(
            original_text
        )

        generic = [

            "play",

            "song",

            "play song",

            "song play",

            "gana",

            "gana play",

            "गाणं",

            "गाणे",

            "गाना",

        ]


        if normalize_text(query) in generic:

            return (
                True,
                "Sir, कोणतं गाणं play करायचं?",
                sleeping
            )


        def play_background():

            success, details = youtube_play(
                query
            )

            print(
                "[YOUTUBE RESULT]:",
                success,
                details
            )


        threading.Thread(
            target=play_background,
            daemon=True
        ).start()


        return (
            True,
            f"नक्की Sir, {query} play करतोय.",
            sleeping
        )


    # =====================================================
    # OPEN YOUTUBE
    # =====================================================

    if is_open_youtube_command(
        original_text
    ):

        success = open_youtube()


        if success:

            return (
                True,
                "ठीक आहे Sir, YouTube उघडलं आहे.",
                sleeping
            )


        return (
            True,
            "Sir, YouTube उघडता आलं नाही.",
            sleeping
        )


    # =====================================================
    # YOUTUBE SEARCH
    # =====================================================

    if is_youtube_search_command(
        original_text
    ):

        query = text


        query = re.sub(
            r"^youtube\s+search\s+",
            "",
            query,
            flags=re.IGNORECASE
        )


        query = re.sub(
            r"^search\s+youtube\s+",
            "",
            query,
            flags=re.IGNORECASE
        )


        query = re.sub(
            r"^youtube\s+var\s+",
            "",
            query,
            flags=re.IGNORECASE
        )


        query = re.sub(
            r"^youtube\s+वर\s+",
            "",
            query,
            flags=re.IGNORECASE
        )


        query = query.strip()


        if not query:

            return (
                True,
                "Sir, YouTube वर काय search करू?",
                sleeping
            )


        success = youtube_search(
            query
        )


        if success:

            return (
                True,
                f"Sir, YouTube वर {query} शोधलं आहे.",
                sleeping
            )


        return (
            True,
            "Sir, YouTube search उघडता आलं नाही.",
            sleeping
        )


    # =====================================================
    # CALCULATOR
    # =====================================================

    if is_calculator_command(
        original_text
    ):

        success = open_calculator()


        if success:

            return (
                True,
                "ठीक आहे Sir, Calculator उघडला आहे.",
                sleeping
            )


        return (
            True,
            "Sir, Calculator उघडता आला नाही.",
            sleeping
        )


    # =====================================================
    # CHROME
    # =====================================================

    if is_chrome_command(
        original_text
    ):

        success = open_chrome()


        if success:

            return (
                True,
                "ठीक आहे Sir, Chrome उघडलं आहे.",
                sleeping
            )


        return (
            True,
            "Sir, Chrome उघडता आलं नाही.",
            sleeping
        )


    # =====================================================
    # UNKNOWN
    # =====================================================

    return (
        False,
        None,
        sleeping
    )


# =========================================================
# EXPORTS
# =========================================================

__all__ = [

    "open_chrome",

    "open_calculator",

    "open_youtube",

    "youtube_search",

    "youtube_play",

    "extract_song_query",

    "is_youtube_play_command",

    "is_open_youtube_command",

    "is_youtube_search_command",

    "is_calculator_command",

    "is_chrome_command",

    "is_sleep_command",

    "is_wake_command",

    "identify_command",

    "handle_local_command",

]