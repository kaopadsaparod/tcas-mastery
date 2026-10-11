import sqlite3
from collections.abc import Generator
from contextlib import contextmanager

from app.config import DB_PATH


def get_db_connection() -> sqlite3.Connection:
    """Creates a database connection with WAL mode, busy timeout, and row factory."""
    conn = sqlite3.connect(str(DB_PATH), timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections with automatic commit/rollback."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Initializes tables and indexes if they do not exist."""
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id TEXT NOT NULL,
            subject TEXT,
            topic TEXT,
            user_answer TEXT,
            is_correct INTEGER NOT NULL,
            status TEXT NOT NULL, -- 'correct_first_try', 'correct_assisted', 'wrong', 'retry_correct'
            confidence TEXT,      -- 'sure', 'unsure', 'guessed'
            hints_opened INTEGER DEFAULT 0,
            plan_step_answer TEXT,
            plan_step_correct INTEGER,
            error_tag TEXT,
            time_spent_sec REAL DEFAULT 0.0,
            review_time_sec REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS review_queue (
            question_id TEXT PRIMARY KEY,
            subject TEXT,
            topic TEXT,
            next_review_at TIMESTAMP,
            interval_days INTEGER DEFAULT 1,
            repetition_count INTEGER DEFAULT 0,
            priority TEXT DEFAULT 'normal', -- 'high', 'normal', 'low'
            last_status TEXT,
            last_error_tag TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS procedural_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drill_type TEXT NOT NULL,
            question_stem TEXT NOT NULL,
            user_answer TEXT,
            expected_answer TEXT,
            is_correct INTEGER NOT NULL,
            time_spent_sec REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS formula_reviews (
            formula_id TEXT PRIMARY KEY,
            subject TEXT,
            correct_count INTEGER DEFAULT 0,
            wrong_count INTEGER DEFAULT 0,
            next_review_at TIMESTAMP,
            last_reviewed_at TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS answer_sheet_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id TEXT NOT NULL,
            paper_title TEXT NOT NULL,
            total_questions INTEGER NOT NULL,
            correct_count INTEGER NOT NULL,
            score_percent REAL NOT NULL,
            answers_json TEXT NOT NULL,
            details_json TEXT NOT NULL,
            time_taken_min REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
            question_id TEXT PRIMARY KEY,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS topic_priorities (
            topic_id TEXT PRIMARY KEY,
            subject TEXT NOT NULL,
            topic_name TEXT NOT NULL,
            priority_level INTEGER DEFAULT 1, -- 1 = เร่งด่วนอันดับ 1, 2 = ลำดับถัดไป, 3 = อ่านเสริม
            target_score_pct REAL DEFAULT 80.0,
            notes TEXT DEFAULT '',
            order_index INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS imported_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            page_count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mock_exam_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            exam_type TEXT NOT NULL,       -- 'alevel_physics', 'tpat3', 'custom'
            title TEXT NOT NULL,
            time_limit_min INTEGER NOT NULL,
            time_spent_min REAL DEFAULT 0.0,
            status TEXT NOT NULL,           -- 'in_progress', 'completed', 'timed_out'
            total_questions INTEGER NOT NULL,
            correct_count INTEGER DEFAULT 0,
            total_score REAL DEFAULT 0.0,
            max_score REAL DEFAULT 100.0,
            score_percent REAL DEFAULT 0.0,
            questions_json TEXT DEFAULT '[]',
            answers_json TEXT DEFAULT '{}',
            flagged_json TEXT DEFAULT '[]',
            report_json TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        );
        """)

        # Migration: ensure questions_json column exists
        cursor.execute("PRAGMA table_info(mock_exam_sessions);")
        mock_cols = {c["name"] for c in cursor.fetchall()}
        if "questions_json" not in mock_cols:
            cursor.execute("ALTER TABLE mock_exam_sessions ADD COLUMN questions_json TEXT DEFAULT '[]';")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            target_exam TEXT NOT NULL,
            daily_minutes INTEGER NOT NULL,
            blocks_completed_json TEXT DEFAULT '[]',
            total_time_spent_min REAL DEFAULT 0.0,
            status TEXT DEFAULT 'in_progress',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        );
        """)

        # Seed and ensure essential topic priorities exist
        default_topics = [
            (
                "physics.vectors",
                "physics",
                "เวกเตอร์และการแตกแรงพื้นฐาน",
                1,
                80.0,
                "พื้นฐานสำคัญที่สุดของฟิสิกส์ทุกบท (Prerequisite ของ Kinematics & แรง)",
                1,
            ),
            (
                "physics.kinematics.1d",
                "physics",
                "การเคลื่อนที่แนวตรง (1D Kinematics)",
                1,
                85.0,
                "หัวใจสำคัญของกลศาสตร์ ต้องทำให้แม่นยำก่อนบทอื่น",
                2,
            ),
            (
                "physics.forces_energy",
                "physics",
                "แรง กฎนิวตัน และงาน-พลังงาน",
                1,
                80.0,
                "บทที่ออกข้อสอบ A-Level สัดส่วนสูงที่สุด",
                3,
            ),
            (
                "physics.waves",
                "physics",
                "คลื่น แสง และเสียง",
                2,
                75.0,
                "ออกสอบ A-Level สม่ำเสมอ",
                4,
            ),
            (
                "physics.electricity",
                "physics",
                "ไฟฟ้าและแม่เหล็ก",
                2,
                75.0,
                "สัดส่วนคะแนนสูงในข้อสอบฟิสิกส์",
                5,
            ),
            (
                "physics.modern_physics",
                "physics",
                "ฟิสิกส์ยุคใหม่และนิวเคลียร์",
                2,
                80.0,
                "บทเก็บคะแนนเร็ว เนื้อหาตรงไปตรงมา",
                6,
            ),
            (
                "math.algebra.basics",
                "math",
                "พีชคณิตพื้นฐานและการแยกตัวประกอบ",
                1,
                80.0,
                "พื้นฐานสมการของคณิตและฟิสิกส์ (Prerequisite ของ Functions)",
                7,
            ),
            (
                "math.algebra.functions",
                "math",
                "พีชคณิตและฟังก์ชัน",
                2,
                75.0,
                "พื้นฐานสำคัญของคณิตประยุกต์ 1",
                8,
            ),
            (
                "tpat3.quantitative",
                "tpat3",
                "ความถนัดเชิงปริมาณและกลศาสตร์ TPAT3",
                1,
                80.0,
                "สอบช่วงปลาย ม.ค. ต้องเก็บก่อน A-Level",
                9,
            ),
            (
                "tpat3.spatial_relations",
                "tpat3",
                "มิติสัมพันธ์และการมองภาพ 3 มิติ",
                1,
                85.0,
                "พาร์ทเก็บคะแนนหลักของ TPAT3",
                10,
            ),
            (
                "tpat3.engineering_mechanics",
                "tpat3",
                "กลศาสตร์เชิงกลและฟิสิกส์วิศวกรรม",
                1,
                80.0,
                "วิเคราะห์ระบบกลไก คาน รอก เฟือง",
                11,
            ),
        ]
        cursor.executemany(
            """
            INSERT INTO topic_priorities (topic_id, subject, topic_name, priority_level, target_score_pct, notes, order_index)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(topic_id) DO NOTHING;
        """,
            default_topics,
        )

        # Indexes for query performance
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_attempts_qid ON attempts(question_id);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_attempts_status ON attempts(status);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_review_next ON review_queue(next_review_at, priority);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_topic_prio ON topic_priorities(priority_level, order_index);"
        )
