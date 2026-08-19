"""
JARVIS 4.0 - OPTIMIZED MEMORY SYSTEM

Responsibilities:
- SQLite conversation memory
- Recent context
- Message length protection
- Duplicate protection
- Memory cleanup
- Search
"""

import sqlite3
import threading
from pathlib import Path
from datetime import datetime


# =========================================================
# PATHS
# =========================================================

MEMORY_DIR = Path(__file__).resolve().parent

DATABASE_FILE = (
    MEMORY_DIR / "jarvis_memory.db"
)


# =========================================================
# LIMITS
# =========================================================

MAX_MESSAGE_LENGTH = 4000

DEFAULT_RECENT_LIMIT = 12

MAX_RECENT_LIMIT = 30

MAX_DATABASE_ROWS = 500


# =========================================================
# MEMORY
# =========================================================

class JarvisMemory:

    def __init__(
        self,
        database_path=None
    ):

        self.name = "JARVIS Memory"

        self.version = "4.0"

        self.database_path = Path(
            database_path
            if database_path
            else DATABASE_FILE
        )

        self.lock = threading.Lock()

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self._initialize_database()


    # =====================================================
    # CONNECTION
    # =====================================================

    def _connect(self):

        connection = sqlite3.connect(
            str(self.database_path),
            timeout=10
        )

        connection.row_factory = (
            sqlite3.Row
        )

        return connection


    # =====================================================
    # INITIALIZE
    # =====================================================

    def _initialize_database(self):

        try:

            with self.lock:

                connection = self._connect()

                cursor = connection.cursor()


                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS conversations (

                        id INTEGER PRIMARY KEY AUTOINCREMENT,

                        role TEXT NOT NULL,

                        content TEXT NOT NULL,

                        created_at TEXT NOT NULL

                    )
                    """
                )


                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_conversations_created
                    ON conversations(created_at)
                    """
                )


                connection.commit()

                connection.close()


            print(
                "[MEMORY] Database initialized:",
                self.database_path
            )


        except Exception as error:

            print(
                "[MEMORY INIT ERROR]:",
                repr(error)
            )


    # =====================================================
    # NORMALIZE CONTENT
    # =====================================================

    def _normalize_content(
        self,
        content: str
    ):

        content = str(
            content or ""
        ).strip()


        if not content:

            return ""


        # -----------------------------------------------
        # Normalize excessive whitespace
        # -----------------------------------------------

        content = " ".join(
            content.split()
        )


        # -----------------------------------------------
        # Maximum length
        # -----------------------------------------------

        if len(content) > MAX_MESSAGE_LENGTH:

            content = (
                content[
                    :MAX_MESSAGE_LENGTH
                ].rstrip()
                +
                "..."
            )


        return content


    # =====================================================
    # DUPLICATE CHECK
    # =====================================================

    def _is_duplicate_last(
        self,
        connection,
        role: str,
        content: str
    ):

        cursor = connection.cursor()


        cursor.execute(
            """
            SELECT role, content
            FROM conversations
            ORDER BY id DESC
            LIMIT 1
            """
        )


        row = cursor.fetchone()


        if not row:

            return False


        return (

            row["role"] == role

            and

            row["content"] == content

        )


    # =====================================================
    # CLEAN OLD DATA
    # =====================================================

    def _cleanup_old_rows(
        self,
        connection
    ):

        cursor = connection.cursor()


        cursor.execute(
            """
            SELECT COUNT(*)
            FROM conversations
            """
        )


        count = int(
            cursor.fetchone()[0]
        )


        if count <= MAX_DATABASE_ROWS:

            return


        delete_count = (
            count - MAX_DATABASE_ROWS
        )


        cursor.execute(
            """
            DELETE FROM conversations
            WHERE id IN
            (
                SELECT id
                FROM conversations
                ORDER BY id ASC
                LIMIT ?
            )
            """,
            (delete_count,)
        )


    # =====================================================
    # REMEMBER
    # =====================================================

    def remember_short_term(
        self,
        role: str,
        content: str
    ):

        role = str(
            role or ""
        ).strip().lower()


        content = self._normalize_content(
            content
        )


        if not role or not content:

            return False


        allowed_roles = {

            "user",
            "assistant",
            "system",

        }


        if role not in allowed_roles:

            role = "user"


        timestamp = datetime.now().isoformat(
            timespec="seconds"
        )


        try:

            with self.lock:

                connection = self._connect()


                # -----------------------------------------
                # Duplicate protection
                # -----------------------------------------

                if self._is_duplicate_last(
                    connection,
                    role,
                    content
                ):

                    connection.close()

                    return True


                cursor = connection.cursor()


                cursor.execute(
                    """
                    INSERT INTO conversations
                    (
                        role,
                        content,
                        created_at
                    )
                    VALUES
                    (?, ?, ?)
                    """,
                    (
                        role,
                        content,
                        timestamp
                    )
                )


                self._cleanup_old_rows(
                    connection
                )


                connection.commit()

                connection.close()


            return True


        except Exception as error:

            print(
                "[MEMORY WRITE ERROR]:",
                repr(error)
            )

            return False


    # =====================================================
    # GET RECENT
    # =====================================================

    def get_recent(
        self,
        limit: int = DEFAULT_RECENT_LIMIT
    ):

        try:

            limit = int(limit)

        except Exception:

            limit = (
                DEFAULT_RECENT_LIMIT
            )


        limit = max(
            1,
            min(
                limit,
                MAX_RECENT_LIMIT
            )
        )


        try:

            with self.lock:

                connection = self._connect()

                cursor = connection.cursor()


                cursor.execute(
                    """
                    SELECT
                        id,
                        role,
                        content,
                        created_at
                    FROM conversations
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (limit,)
                )


                rows = cursor.fetchall()

                connection.close()


            rows = list(
                reversed(rows)
            )


            result = []


            for row in rows:

                result.append(

                    {
                        "id":
                            row["id"],

                        "role":
                            row["role"],

                        "content":
                            row["content"],

                        "created_at":
                            row["created_at"],

                    }

                )


            return result


        except Exception as error:

            print(
                "[MEMORY READ ERROR]:",
                repr(error)
            )

            return []


    # =====================================================
    # GET ALL
    # =====================================================

    def get_all(self):

        try:

            with self.lock:

                connection = self._connect()

                cursor = connection.cursor()


                cursor.execute(
                    """
                    SELECT
                        id,
                        role,
                        content,
                        created_at
                    FROM conversations
                    ORDER BY id ASC
                    """
                )


                rows = cursor.fetchall()

                connection.close()


            result = []


            for row in rows:

                result.append(

                    {
                        "id":
                            row["id"],

                        "role":
                            row["role"],

                        "content":
                            row["content"],

                        "created_at":
                            row["created_at"],

                    }

                )


            return result


        except Exception as error:

            print(
                "[MEMORY ALL ERROR]:",
                repr(error)
            )

            return []


    # =====================================================
    # COUNT
    # =====================================================

    def count(self):

        try:

            with self.lock:

                connection = self._connect()

                cursor = connection.cursor()


                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM conversations
                    """
                )


                result = cursor.fetchone()[0]

                connection.close()


            return int(
                result
            )


        except Exception as error:

            print(
                "[MEMORY COUNT ERROR]:",
                repr(error)
            )

            return 0


    # =====================================================
    # CLEAR
    # =====================================================

    def clear_short_term(self):

        try:

            with self.lock:

                connection = self._connect()

                cursor = connection.cursor()


                cursor.execute(
                    """
                    DELETE FROM conversations
                    """
                )


                connection.commit()

                connection.close()


            print(
                "[MEMORY] Short-term memory cleared."
            )


            return True


        except Exception as error:

            print(
                "[MEMORY CLEAR ERROR]:",
                repr(error)
            )

            return False


    # =====================================================
    # DELETE LAST
    # =====================================================

    def delete_last(
        self,
        count: int = 1
    ):

        try:

            count = int(count)

        except Exception:

            return False


        if count <= 0:

            return False


        try:

            with self.lock:

                connection = self._connect()

                cursor = connection.cursor()


                cursor.execute(
                    """
                    DELETE FROM conversations
                    WHERE id IN
                    (
                        SELECT id
                        FROM conversations
                        ORDER BY id DESC
                        LIMIT ?
                    )
                    """,
                    (count,)
                )


                connection.commit()

                connection.close()


            return True


        except Exception as error:

            print(
                "[MEMORY DELETE ERROR]:",
                repr(error)
            )

            return False


    # =====================================================
    # SEARCH
    # =====================================================

    def search(
        self,
        keyword: str,
        limit: int = 20
    ):

        keyword = str(
            keyword or ""
        ).strip()


        if not keyword:

            return []


        try:

            limit = int(limit)

        except Exception:

            limit = 20


        limit = max(
            1,
            min(
                limit,
                50
            )
        )


        try:

            with self.lock:

                connection = self._connect()

                cursor = connection.cursor()


                cursor.execute(
                    """
                    SELECT
                        id,
                        role,
                        content,
                        created_at
                    FROM conversations
                    WHERE content LIKE ?
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (
                        f"%{keyword}%",
                        limit
                    )
                )


                rows = cursor.fetchall()

                connection.close()


            result = []


            for row in rows:

                result.append(

                    {
                        "id":
                            row["id"],

                        "role":
                            row["role"],

                        "content":
                            row["content"],

                        "created_at":
                            row["created_at"],

                    }

                )


            return list(
                reversed(result)
            )


        except Exception as error:

            print(
                "[MEMORY SEARCH ERROR]:",
                repr(error)
            )

            return []


    # =====================================================
    # COMPACT DATABASE
    # =====================================================

    def compact(self):

        try:

            with self.lock:

                connection = self._connect()

                cursor = connection.cursor()


                self._cleanup_old_rows(
                    connection
                )


                cursor.execute(
                    "VACUUM"
                )


                connection.commit()

                connection.close()


            print(
                "[MEMORY] Database compacted."
            )


            return True


        except Exception as error:

            print(
                "[MEMORY COMPACT ERROR]:",
                repr(error)
            )

            return False


# =========================================================
# SINGLE INSTANCE
# =========================================================

jarvis_memory = JarvisMemory()