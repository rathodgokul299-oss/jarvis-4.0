"""
JARVIS MEMORY SYSTEM
====================

Responsibilities:
- SQLite database
- Short-term conversation memory
- Recent messages
- User / assistant message storage
- Memory clearing
- Safe database initialization
"""

import sqlite3
import threading
from pathlib import Path
from datetime import datetime


# =========================================================
# PATHS
# =========================================================

MEMORY_DIR = Path(__file__).resolve().parent

DATABASE_FILE = MEMORY_DIR / "jarvis_memory.db"


# =========================================================
# MEMORY CLASS
# =========================================================

class JarvisMemory:

    def __init__(
        self,
        database_path=None
    ):

        self.name = "JARVIS Memory"
        self.version = "3.0"

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
    # DATABASE CONNECTION
    # =====================================================

    def _connect(self):

        connection = sqlite3.connect(
            str(self.database_path),
            timeout=10
        )

        connection.row_factory = sqlite3.Row

        return connection


    # =====================================================
    # INITIALIZE DATABASE
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
    # REMEMBER SHORT TERM
    # =====================================================

    def remember_short_term(
        self,
        role: str,
        content: str
    ):

        role = str(
            role or ""
        ).strip().lower()

        content = str(
            content or ""
        ).strip()

        if not role or not content:

            return False

        allowed_roles = {
            "user",
            "assistant",
            "system"
        }

        if role not in allowed_roles:

            role = "user"


        timestamp = datetime.now().isoformat(
            timespec="seconds"
        )


        try:

            with self.lock:

                connection = self._connect()

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
        limit: int = 12
    ):

        try:

            limit = int(limit)

        except Exception:

            limit = 12


        if limit <= 0:

            return []


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
                        "id": row["id"],
                        "role": row["role"],
                        "content": row["content"],
                        "created_at": row["created_at"],
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
                        "id": row["id"],
                        "role": row["role"],
                        "content": row["content"],
                        "created_at": row["created_at"],
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

            return int(result)


        except Exception as error:

            print(
                "[MEMORY COUNT ERROR]:",
                repr(error)
            )

            return 0


    # =====================================================
    # CLEAR SHORT TERM
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
    # DELETE LAST N
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


        if limit <= 0:

            return []


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
                        "id": row["id"],
                        "role": row["role"],
                        "content": row["content"],
                        "created_at": row["created_at"],
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


# =========================================================
# SINGLE INSTANCE
# =========================================================

jarvis_memory = JarvisMemory()