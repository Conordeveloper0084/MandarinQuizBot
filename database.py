# Bu file kelajakda PostgreSQL databasega o'tish uchun ochildi!

# import asyncpg
# from datetime import datetime

# class User:
#     def __init__(self, id, full_name):
#         self.id = id
#         self.full_name = full_name

# async def get_connection():
#     return await asyncpg.connect(
#         user='postgres',
#         password='postgres',
#         database='quizbot',
#         host='localhost'
#     )

# async def save_user_info(user):
#     conn = await get_connection()
#     await conn.execute(
#         """
#         INSERT INTO users (id, name, joined)
#         VALUES ($1, $2, $3)
#         ON CONFLICT (id) DO NOTHING
#         """,
#         user.id,
#         user.full_name,
#         datetime.now()
#     )
#     await conn.close()