import sqlite3

DB_PATH = "data/persona_bot.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def add_user(user_id, username, first_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
        (user_id, username, first_name)
    )
    conn.commit()
    conn.close()

def user_exists(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def save_result(user_id, mbti_type, ei_score, sn_score, tf_score, jp_score):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO test_results (user_id, mbti_type, ei_score, sn_score, tf_score, jp_score) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, mbti_type, ei_score, sn_score, tf_score, jp_score)
    )
    conn.commit()
    conn.close()

def get_latest_result(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT mbti_type, ei_score, sn_score, tf_score, jp_score FROM test_results WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
        (user_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result