from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Boshlang'ich menyu uchun tugmalar
btn_start_quiz = KeyboardButton("🎯 Quizni boshlash")
btn_my_score = KeyboardButton("📊 Mening natijalarim")
btn_about = KeyboardButton("ℹ️ About")

# Asosiy menyu (reply keyboard)
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [btn_start_quiz],
        [btn_my_score, btn_about]
    ],
    resize_keyboard=True
)

# "Boshidan boshlash" va "Boshqa quizlar" tugmalari
btn_restart_quiz = KeyboardButton("🔄Qayta boshlash")
btn_other_quizzes = KeyboardButton("📂Boshqa quizlar")

# Yangi tugmalar uchun menyu
quiz_end_menu = ReplyKeyboardMarkup(
    keyboard=[
        [btn_restart_quiz, btn_other_quizzes]
    ],
    resize_keyboard=True
)