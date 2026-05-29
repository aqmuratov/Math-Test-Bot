import sqlite3

def init_db():
    import sqlite3
    conn = sqlite3.connect("test_bot.db")
    cursor = conn.cursor()
    
    # Mavjud jadvallarni yaratish
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tests (
            test_code TEXT PRIMARY KEY,
            correct_key TEXT,
            status TEXT DEFAULT 'active'
        )
    """)
    
    # AGAR JADVAL OLDIN BOR BO'LSA, STATUS USTUNINI QO'SHISH
    try:
        cursor.execute("ALTER TABLE tests ADD COLUMN status TEXT DEFAULT 'active'")
    except sqlite3.OperationalError:
        # Agar ustun allaqachon bo'lsa, xato bermasligi uchun
        pass
        
    # Boshqa jadvallaringiz (results va h.k.) shu yerda davom etadi...
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            user_id INTEGER,
            full_name TEXT,
            test_code TEXT,
            score INTEGER,
            attempt INTEGER
        )
    """)
    
    conn.commit()
    conn.close()

# Yangi test qo'shish yoki eskisini yangilash
def set_test_key(test_code, correct_key):
    conn = sqlite3.connect("test_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO tests (test_code, correct_key) 
        VALUES (?, ?)
    """, (test_code, correct_key))
    conn.commit()
    conn.close()

# Test kodiga qarab kalitni olish
def get_test_key(test_code):
    conn = sqlite3.connect("test_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT correct_key FROM tests WHERE test_code = ?", (test_code,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

# O'quvchining ma'lum bir test bo'yicha nechta urinish qilganini aniqlash
def get_user_attempts(user_id, test_code):
    conn = sqlite3.connect("test_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM results 
        WHERE user_id = ? AND test_code = ?
    """, (user_id, test_code))
    count = cursor.fetchone()[0]
    conn.close()
    return count

# Natijani saqlash (urinish raqami bilan)
def save_result(user_id, full_name, test_code, correct_count, attempt):
    conn = sqlite3.connect("test_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO results (user_id, full_name, test_code, correct_count, attempt) 
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, full_name, test_code, correct_count, attempt))
    conn.commit()
    conn.close()

# Reytingni test kodi bo'yicha olish
def get_rating(): # test_code argumentini olib tashladik
    conn = sqlite3.connect("test_bot.db")
    cursor = conn.cursor()
    # Har bir foydalanuvchining jami to'g'ri javoblari yig'indisini hisoblaymiz
    cursor.execute("""
        SELECT full_name, SUM(correct_count) as total_score 
        FROM results 
        GROUP BY user_id 
        ORDER BY total_score DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

# O'quvchi profil ma'lumotlarini olish (Yangi qo'shilgan qism)
def get_user_profile(user_id):
    conn = sqlite3.connect("test_bot.db")
    cursor = conn.cursor()
    
    # Umumiy topshirilgan testlar soni va jami to'g'ri javoblar yig'indisi
    cursor.execute("""
        SELECT COUNT(*), IFNULL(SUM(correct_count), 0) FROM results 
        WHERE user_id = ?
    """, (user_id,))
    stats = cursor.fetchone()
    
    # O'quvchining oxirgi topshirgan 5 ta testi tarixi
    cursor.execute("""
        SELECT test_code, correct_count, attempt FROM results 
        WHERE user_id = ? 
        ORDER BY id DESC LIMIT 5
    """, (user_id,))
    last_results = cursor.fetchall()
    
    conn.close()
    return stats, last_results

def get_all_results_for_export():
    conn = sqlite3.connect("test_bot.db")
    cursor = conn.cursor()
    # Barcha natijalarni o'quvchi ismi, kodi va ballari bilan olamiz
    cursor.execute("""
        SELECT full_name, user_id, test_code, correct_count, attempt 
        FROM results 
        ORDER BY test_code ASC, correct_count DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def check_and_update_schema():
    """Jadvalda status ustuni borligini tekshiradi, yo'q bo'lsa qo'shadi"""
    import sqlite3
    conn = sqlite3.connect("test_bot.db")
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE tests ADD COLUMN status TEXT DEFAULT 'active'")
        conn.commit()
    except sqlite3.OperationalError:
        # Agar status ustuni allaqachon mavjud bo'lsa, xato bermaydi
        pass
    conn.close()

def toggle_test_status(test_code, status):
    """Test holatini active yoki inactive ga o'zgartiradi"""
    import sqlite3
    conn = sqlite3.connect("test_bot.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE tests SET status = ? WHERE test_code = ?", (status, test_code))
    conn.commit()
    conn.close()

def is_test_active(test_code):
    """Test faol ekanligini tekshiradi (True/False)"""
    import sqlite3
    conn = sqlite3.connect("test_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM tests WHERE test_code = ?", (test_code,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0] == 'inactive':
        return False
    return True