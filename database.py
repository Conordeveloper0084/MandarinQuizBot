# In the future

# import psycopg2
# from psycopg2.extras import RealDictCursor
# from datetime import datetime

# DB_NAME = "mandarin_datas"
# DB_USER = "postgres"
# DB_PASSWORD = "your_password"
# DB_HOST = "localhost"  # yoki '127.0.0.1'

# def get_connection():
#     return psycopg2.connect(
#         dbname=DB_NAME,
#         user=DB_USER,
#         password=DB_PASSWORD,
#         host=DB_HOST
#     )

# def get_questions_from_db(tech: str, count: int):
#     conn = get_connection()
#     cur = conn.cursor()
#     cur.execute("""
#         SELECT question, options, correct_option
#         FROM questions
#         WHERE technology = %s
#         ORDER BY RANDOM()
#         LIMIT %s
#     """, (tech, count))
#     rows = cur.fetchall()
#     cur.close()
#     conn.close()
#     return rows

# def save_user_info(user_id, full_name):
#     conn = get_connection()
#     cur = conn.cursor()
#     cur.execute("""
#         INSERT INTO users (id, name, joined)
#         VALUES (%s, %s, %s)
#         ON CONFLICT (id) DO NOTHING
#     """, (user_id, full_name, datetime.now().strftime("%Y-%m-%d %H:%M")))
#     conn.commit()
#     cur.close()
#     conn.close()

# def save_result(user_id, full_name, new_score):
#     conn = get_connection()
#     cur = conn.cursor()

#     cur.execute("SELECT score FROM results WHERE user_id = %s", (str(user_id),))
#     row = cur.fetchone()

#     now = datetime.now().strftime("%Y-%m-%d %H:%M")
#     if row:
#         previous_score = row[0]
#         cur.execute("""
#             UPDATE results
#             SET score = %s, date = %s
#             WHERE user_id = %s
#         """, (previous_score + new_score, now, str(user_id)))
#     else:
#         cur.execute("""
#             INSERT INTO results (user_id, name, score, date)
#             VALUES (%s, %s, %s, %s)
#         """, (str(user_id), full_name, new_score, now))

#     conn.commit()
#     cur.close()
#     conn.close()

# def get_user_result(user_id):
#     conn = get_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT name, score, date FROM results WHERE user_id = %s", (str(user_id),))
#     result = cur.fetchone()
#     cur.close()
#     conn.close()
#     return result