import json
import os
import random
from pathlib import Path
from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from loader import dp
from config import CHANNEL_ID
from keyboards.reply import main_menu
from states.quiz_states import QuizState
from datetime import datetime
from keyboards.reply import quiz_end_menu
from config import ADMINS
from aiogram.utils.exceptions import MessageNotModified

def get_home_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton("🧠 Quiz boshlash"),
        KeyboardButton("📊 Natijalar"),
        KeyboardButton("ℹ️ About")
    )

def get_file_path(tech):
    tech = tech.lower()
    base_path = "data"
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.lower() == f"{tech}.json":
                return os.path.join(root, file)
    return None

results_path = Path("data/Results/results.json")
progress_path = Path("data/Results/progress.json")

async def is_subscribed(user_id: int, bot) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False
    
users_path = Path("data/Users/users.json")

async def save_user_info(user: types.User):
    new_user = {
        "id": user.id,
        "name": user.full_name,
        "joined": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    if users_path.exists():
        with open(users_path, "r", encoding="utf-8") as f:
            users = json.load(f)
    else:
        users = []

    if all(u["id"] != user.id for u in users):
        users.append(new_user)
        with open(users_path, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

@dp.message_handler(commands=['start'],state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text == "/start":
        await state.finish()
    subscribed = await is_subscribed(message.from_user.id, message.bot)

    if not subscribed:
        buttons = InlineKeyboardMarkup(row_width=1)
        buttons.add(
            InlineKeyboardButton("📢 Kanalga o‘tish", url="https://t.me/Conordevs_Blogs"),
            InlineKeyboardButton("✅ Obuna bo‘ldim", callback_data="check_subscription")
        )
        await message.answer("🛑 Quizni boshlashdan oldin iltimos kanalimizga obuna bo'ling!", reply_markup=buttons)
        return

    await message.answer(
        f"<b>Assalomu aleykum, {message.from_user.full_name}!</b>👋\n\n"
        "Quizni boshlash uchun <b>\"🎯 Quizni boshlash\"</b> tugmasini bosing!",
        reply_markup=main_menu,
        parse_mode="HTML"
    )
    await state.finish()

    await save_user_info(message.from_user)

@dp.callback_query_handler(lambda c: c.data == "check_subscription")
async def process_check_subscription(callback_query: types.CallbackQuery):
    subscribed = await is_subscribed(callback_query.from_user.id, callback_query.bot)

    if subscribed:
        await callback_query.message.edit_text("✅ Obuna bo'ldingiz! Endi quizni boshlashingiz mumkin!")
        await callback_query.message.answer("Quizni boshlash uchun \"🎯 Quizni boshlash\" tugmasini bosing!", reply_markup=main_menu, parse_mode="HTML")
    else:
        await callback_query.answer("🚫 Siz hali obuna bo‘lmagansiz!", show_alert=True)

@dp.message_handler(lambda message: message.text == "🎯 Quizni boshlash")
async def start_quiz(message: types.Message, state: FSMContext):
    if message.text == "/admin" and message.from_user.id in ADMINS:
        await state.finish()
        await message.answer("🔧 Admin menyu:")
        return
    await state.finish()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("Data Analitika"), KeyboardButton("Front End"))
    await message.answer("🧑‍💻 Qaysi yo‘nalishni tanlaysiz?", reply_markup=markup)
    await QuizState.choose_direction.set()

@dp.message_handler(state=QuizState.choose_direction)
async def choose_direction(message: types.Message, state: FSMContext):
    if message.text == "/admin" and message.from_user.id in ADMINS:
        await state.finish()
        await message.answer("🔧 Admin menyu:")
        return

    direction = message.text
    await state.update_data(direction=direction)

    techs = ["NumPy", "Pandas"] if direction == "Data Analitika" else ["HTML", "CSS", "JavaScript"]

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for tech in techs:
        markup.add(KeyboardButton(tech))
    markup.add(KeyboardButton("🔙 Ortga"))

    await message.answer("📚 Qaysi texnologiya bo‘yicha quiz ishlamoqchisiz?", reply_markup=markup)
    await QuizState.choose_technology.set()

@dp.message_handler(state=QuizState.choose_technology)
async def choose_technology(message: types.Message, state: FSMContext):
    if message.text == "/admin" and message.from_user.id in ADMINS:
        await state.finish()
        await message.answer("🔧 Admin menyu:")
        return
    
    if message.text == "🔙 Ortga":
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton("Data Analitika"), KeyboardButton("Front End"))
        await message.answer("🔙 Qaytildi. Qayta yo‘nalish tanlang:", reply_markup=markup)
        await QuizState.choose_direction.set()
        return
    
    await state.update_data(technology=message.text.strip())
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("5 ta savol"), KeyboardButton("10 ta savol"))
    markup.add(KeyboardButton("🔙 Ortga"))
    await message.answer("📝 Nechta quiz ishlamoqchisiz?", reply_markup=markup)
    await QuizState.choose_question_count.set()

def get_main_menu_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton("📂Boshqa quizlar"), KeyboardButton("🔄Qayta boshlash")
    )

@dp.message_handler(state=QuizState.choose_question_count)
async def choose_question_count(message: types.Message, state: FSMContext):
    text = message.text.strip().lower()

    if text == "🔙 ortga":
        user_data = await state.get_data()
        direction = user_data.get("direction", "Data Analitika")

        techs = ["NumPy", "Pandas"] if direction == "Data Analitika" else ["HTML", "CSS", "JavaScript"]
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for tech in techs:
            markup.add(KeyboardButton(tech))
        markup.add(KeyboardButton("🔙 Ortga"))

        await message.answer("📚 Qayta texnologiya tanlang:", reply_markup=markup)
        await QuizState.choose_technology.set()
        return

    if "qayta boshlash" in text:
        await restart_quiz(message, state)
        return

    if "boshqa quizlar" in text:
        await return_to_main_menu(message, state)
        return

    if text == "5 ta savol":
        count = 5
    elif text == "10 ta savol":
        count = 10
    else:
        await message.answer("❌ Noto‘g‘ri tanlov. Iltimos, \"5 ta savol\" yoki \"10 ta savol\" ni tanlang.")
        return

    user_data = await state.get_data()
    tech = user_data['technology']
    file_path = get_file_path(tech)

    if not file_path or not os.path.exists(file_path):
        await message.answer("❌ Savollar topilmadi.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        all_questions = json.load(f)

    user_id = str(message.from_user.id)

    if progress_path.exists():
        with open(progress_path, "r", encoding="utf-8") as f:
            progress_data = json.load(f)
    else:
        progress_data = {}

    user_progress = progress_data.get(user_id, {}).get(tech, [])
    remaining_questions = [q for q in all_questions if q["question"] not in user_progress]

    if not remaining_questions:
        await message.answer(
            "🎉 Siz ushbu texnologiyadagi barcha savollarni ishlab tugatibsiz, tabriklayman🥳!\n\n"
            "- Qayta quiz boshlash uchun <b>\"🔄Qayta boshlash\"</b> tugmasini bosing!\n\n"
            "<b>❗️Ishlagan quizlaringiz o'chib ketadi va quizlar qayta takrorlanishi mumkin!\n\n"
            "✅Lekin bu takrorlash foydali bo'ladi!☺️</b>",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
        return

    if len(remaining_questions) < count:
        await message.answer(f"⚠️ Faqat {len(remaining_questions)} ta ishlanmagan savol bor. Shular bilan boshlaymiz.")
        count = len(remaining_questions)

    selected = random.sample(remaining_questions, count)

    if not selected:
        await message.answer("❌ Tanlash uchun yetarli savollar topilmadi.")
        return

    if user_id not in progress_data:
        progress_data[user_id] = {}
    if tech not in progress_data[user_id]:
        progress_data[user_id][tech] = []

    for q in selected:
        progress_data[user_id][tech].append(q["question"])

    with open(progress_path, "w", encoding="utf-8") as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)

    await state.update_data(questions=selected, current_q=0, score=0)
    await send_question(message, selected[0], 1)
    await QuizState.answering.set()

@dp.message_handler(lambda message: message.text == "🔄Qayta boshlash", state="*")
async def restart_quiz(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_data = await state.get_data()
    tech = user_data['technology'] 

    if progress_path.exists():
        with open(progress_path, "r", encoding="utf-8") as f:
            progress_data = json.load(f)
        if user_id in progress_data and tech in progress_data[user_id]:
            del progress_data[user_id][tech]  # faqat shu texnologiyaga tegishli progressni o'chirish
            with open(progress_path, "w", encoding="utf-8") as f:
                json.dump(progress_data, f, ensure_ascii=False, indent=2)

    await state.finish()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("Data Analitika"), KeyboardButton("Front End"))
    await message.answer("🧑‍💻 Qaysi yo‘nalishni tanlaysiz?", reply_markup=markup)
    await QuizState.choose_direction.set()

@dp.message_handler(lambda message: message.text == "📂Boshqa quizlar", state="*")
async def return_to_main_menu(message: types.Message, state: FSMContext):
    await state.finish()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("Data Analitika"), KeyboardButton("Front End"))
    await message.answer("🧑‍💻 Qaysi yo‘nalishni tanlaysiz?", reply_markup=markup)
    await QuizState.choose_direction.set()

async def send_question(message, question, index):
    markup = InlineKeyboardMarkup(row_width=2)
    options = question["options"]
    
    for idx, opt in enumerate(options):
        markup.add(
            InlineKeyboardButton(text=opt, callback_data=f"answer:{idx}")
        )

    await message.answer(f"{index}-savol:\n\n{question['question']}", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data.startswith("answer:"), state=QuizState.answering)
async def handle_answer(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_q = data['current_q']
    questions = data['questions']
    score = data['score']

    selected_index = int(call.data.split(":")[1])
    selected_option = questions[current_q]['options'][selected_index]
    correct_answer = questions[current_q]['answer']

    if selected_option == correct_answer:
        score += 1
        await call.answer("✅ To‘g‘ri!")
    else:
        await call.answer(f"❌ Noto‘g‘ri! To‘g‘ri javob: {correct_answer}")

    current_q += 1
    if current_q < len(questions):
        await state.update_data(current_q=current_q, score=score)

        new_text = "⏳"
        try:
            if call.message.text != new_text:
                await call.message.edit_text(new_text)
        except MessageNotModified:
            pass

        await send_question(call.message, questions[current_q], current_q + 1)
    else:
        await state.update_data(score=score)
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("🔁 Qayta boshlash", callback_data="restart_quiz"),
            InlineKeyboardButton("❌ Chiqish", callback_data="exit_quiz")
        )
        new_text = f"🎉 Quiz tugadi!\n<b>🏆 Sizning natijangiz: {score}/{len(questions)}</b>\n\nQuizni qayta boshlamoqchimisiz?"
        if call.message.text != new_text: 
            await call.message.edit_text(new_text, reply_markup=keyboard, parse_mode="HTML")
    
        await save_result(call.from_user, score)
        await state.finish()

async def save_result(user: types.User, new_score: int):
    if results_path.exists():
        with open(results_path, "r", encoding="utf-8") as f:
            results = json.load(f)
    else:
        results = {}

    user_id = str(user.id)
    previous_score = results.get(user_id, {}).get("score", 0)
    results[user_id] = {
        "name": user.full_name,
        "score": previous_score + new_score,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

@dp.message_handler(lambda message: message.text == "📊 Mening natijalarim")
async def show_results(message: types.Message):
    user_id = str(message.from_user.id)
    if results_path.exists():
        with open(results_path, "r", encoding="utf-8") as f:
            results = json.load(f)
        user_result = results.get(user_id)
        if user_result:
            await message.answer(
                f"📝 Name: {user_result['name']}\n"
                f"🏆 Score: {user_result['score']}\n"
                f"🕒 Last Online: {user_result['date']}"
            )
        else:
            await message.answer("🚫 Siz hali quiz ishlamagansiz.")
    else:
        await message.answer("📭 Hozircha natijalar mavjud emas.")

@dp.message_handler(lambda message: message.text == "ℹ️ About")
async def show_about_info(message: types.Message):
    await message.answer("<b>Assalomu aleykum, bu Mandarin Quiz Bot☺️🍊!</b> \n \n - Bu Bot IT olamidagi turli xil sohalarni hamda texnalogiyalarni o'z ichiga olgan holda Quiz Savollar beradi. Bu orqali siz olgan bilimlaringizni qiziqarli o'yin ko'rinishida takrorlashingiz hamda Job Interviewlarga qisman tayyorlanishingiz mumkin! \n \n - Bot hozircha MVP ko'rinishida ya'ni hozircha kam sohalar va texnalogiyalar bo'yicha Quizlar mavjud, va savollar soni ham cheklangan, lekin kelajakda Botni yaxshilash hamda yangi funksiyalar qo'shishni rejalashtirganman! \n \n <b>- Kelajakdagi rejalar: \n \n 💡1 - Yangi Sohalar! \n ⚙️2 - Yangi Texnalogiyalar! \n 📁3 - Yangi Quizlar! \n ⏱️4 - Quiz Timer! \n 🗣️5 - Multi Lang funksiyasi! \n 🏆6 - Leader Board! \n 📈7 - Statistikalar! \n 🖥️8 - Real life interviewlar! \n 🤖9 - AI integration! \n\n 💻10 - Web Application! \n 📱11 - Mobile App!</b>\n \n - Botni muntazam tarzda update qilib yaxshilab boraman, o'ylaymanki Bot siz uchun manfaatli bo'ladi, Inshaalloh!😊",

    parse_mode="HTML")

def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_message_handler(start_quiz, lambda message: message.text == "🎯 Quizni boshlash")
    dp.register_message_handler(show_results, lambda message: message.text == "📊 Mening natijalarim")

    dp.register_message_handler(choose_direction, state=QuizState.choose_direction)
    dp.register_message_handler(choose_technology, state=QuizState.choose_technology)
    dp.register_message_handler(choose_question_count, state=QuizState.choose_question_count)

@dp.callback_query_handler(lambda c: c.data == "exit_quiz")
async def exit_quiz_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback_query.answer()
    await callback_query.message.answer("Quiz o'yin tugadi, ishtirok uchun Rahmat☺️!", reply_markup=main_menu)

@dp.callback_query_handler(lambda c: c.data == "restart_quiz")
async def quiz_restart_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback_query.answer()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("Data Analitika"), KeyboardButton("Front End"))
    await callback_query.message.answer("🧑‍💻 Qaysi yo‘nalishni tanlaysiz?", reply_markup=markup)
    await QuizState.choose_direction.set()

# In the future
@dp.message_handler(commands=["reset_progress"])
async def reset_user_progress(message: types.Message):
    user_id = str(message.from_user.id)
    if progress_path.exists():
        with open(progress_path, "r+", encoding="utf-8") as f:
            data = json.load(f)
            if user_id in data:
                del data[user_id]
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.truncate()
        await message.answer("🔄 Sizning progress muvaffaqiyatli tozalandi.")
    else:
        await message.answer("🚫 Sizda progress mavjud emas.")