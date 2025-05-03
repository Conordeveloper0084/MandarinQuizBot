from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json, os
from config import ADMINS
from keyboards.reply import main_menu
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pathlib import Path

ADMINS = list(map(int, os.getenv("ADMINS", "").split(",")))

def get_file_path(tech):
    tech = tech.strip().lower()
    base_path = os.path.join("data", "Data Analytics" if tech in ["numpy", "pandas"] else "Front End")
    return os.path.join(base_path, f"{tech}.json")

def get_users_file_path():
    return os.path.join("data", "Users", "users.json")

with open(get_users_file_path(), "r", encoding="utf-8") as f:
    users = json.load(f)


MAX_MESSAGE_LENGTH = 4096

def split_text(text):
    return [text[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(text), MAX_MESSAGE_LENGTH)]

class AdminAddQuestion(StatesGroup):
    # Add
    waiting_for_tech = State()
    waiting_for_question = State()
    waiting_for_options = State()
    waiting_for_correct_answer = State()
    asking_next_action = State()

    # Delete
    choosing_tech_for_delete = State()
    choosing_question_index_for_delete = State()

    # Edit
    choosing_tech_for_edit = State()
    choosing_question_index_for_edit = State()
    editing_question_text = State()
    editing_options = State()
    editing_answer = State()

class AdminBroadcastState(StatesGroup):
    waiting_for_message = State()

admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
admin_keyboard.add(
    KeyboardButton("➕ Yangi savol qo‘shish"),
    KeyboardButton("🗑 Savolni o‘chirish"),
    KeyboardButton("✏️ Savolni tahrirlash"),
    KeyboardButton("📢 Broadcast"),
    KeyboardButton("❌ Yakunlash")
)

def register_admin_handlers(dp):
    admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    admin_keyboard.add(
        KeyboardButton("➕ Yangi savol qo‘shish"),
        KeyboardButton("✏️ Savolni tahrirlash"),
        KeyboardButton("🗑 Savolni o‘chirish"),
        KeyboardButton("📢 Broadcast"),
        KeyboardButton("❌ Yakunlash")
    )

    @dp.message_handler(commands=["admin"])
    async def admin_panel(message: types.Message, state: FSMContext):
        await state.finish()

        if message.from_user.id in ADMINS:
            await message.answer("🔧 Admin menyu:", reply_markup=admin_keyboard)
        else:
            await message.answer("❌ Sizda admin huquqlari mavjud emas!")

    @dp.message_handler(lambda m: m.text == "➕ Yangi savol qo‘shish" and m.from_user.id in ADMINS)
    async def start_add_question(message: types.Message, state: FSMContext):
        await state.finish()
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton("NumPy"), KeyboardButton("Pandas"))
        markup.add(KeyboardButton("HTML"), KeyboardButton("CSS"), KeyboardButton("JavaScript"))
        await message.answer("📚 Qaysi texnologiyaga savol qo‘shmoqchisiz?", reply_markup=markup)
        await AdminAddQuestion.waiting_for_tech.set()

    @dp.message_handler(state=AdminAddQuestion.waiting_for_tech, user_id=ADMINS)
    async def get_tech(message: types.Message, state: FSMContext):
        await state.update_data(tech=message.text.strip().lower())
        await message.answer("✍️ Savol matnini yuboring:")
        await AdminAddQuestion.waiting_for_question.set()

    @dp.message_handler(state=AdminAddQuestion.waiting_for_question, user_id=ADMINS)
    async def get_question(message: types.Message, state: FSMContext):
        await state.update_data(question=message.text.strip())
        await message.answer("🧾 Variantlarni yuboring (har birini yangi qatordan yozing, 4 ta bo‘lsin):")
        await AdminAddQuestion.waiting_for_options.set()

    @dp.message_handler(state=AdminAddQuestion.waiting_for_options, user_id=ADMINS)
    async def get_options(message: types.Message, state: FSMContext):
        options = message.text.strip().split("\n")
        if len(options) != 4:
            return await message.answer("❗ Iltimos, aniq 4 ta variant yuboring.")
        await state.update_data(options=options)
        await message.answer("✅ To‘g‘ri javobni tanlang (A, B, C yoki D):")
        await AdminAddQuestion.waiting_for_correct_answer.set()

    @dp.message_handler(state=AdminAddQuestion.waiting_for_correct_answer, user_id=ADMINS)
    async def save_question(message: types.Message, state: FSMContext):
        data = await state.get_data()
        answer_letter = message.text.strip().upper()
        letter_to_index = {'A': 0, 'B': 1, 'C': 2, 'D': 3}

        if answer_letter not in letter_to_index:
            return await message.answer("⚠️ Faqat A, B, C yoki D harflaridan birini tanlang.")

        answer_index = letter_to_index[answer_letter]
        options = data['options']
        answer = options[answer_index]

        new_question = {
            "question": data["question"],
            "options": options,
            "answer": answer
        }

        file_path = get_file_path(data["tech"])

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    questions = json.load(f)
                except json.JSONDecodeError:
                    questions = []
        else:
            questions = []

        questions.append(new_question)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=4)

        await message.answer(f"✅ Savol '{data['tech']}' texnologiyasiga saqlandi.")
        await ask_next_action(message, state)

    async def ask_next_action(message: types.Message, state: FSMContext):
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton("Ha"), KeyboardButton("Yo‘q"))
        await message.answer("🔁 Yana amal bajarmoqchimisiz?", reply_markup=markup)
        await AdminAddQuestion.asking_next_action.set()

    async def admin_panel_actions(message: types.Message):
        await message.answer("🔧 Admin menyu:", reply_markup=admin_keyboard)

    @dp.message_handler(state=AdminAddQuestion.asking_next_action, user_id=ADMINS)
    async def handle_next_action(message: types.Message, state: FSMContext):
        if message.text == "Ha":
            await state.finish()
            await admin_panel_actions(message) 
        else:
            await message.answer("✅ Ish yakunlandi, admin paneldan chiqdingiz 🔚",     reply_markup=main_menu)
            await state.finish()

    @dp.message_handler(lambda m: m.text == "❌ Yakunlash" and m.from_user.id in ADMINS)
    async def handle_exit_action(message: types.Message, state: FSMContext):
        await state.finish()
        await message.answer("🔚 Admin paneldan chiqdingiz.", reply_markup=main_menu)    

# ========================== ✏️ SAVOLNI TAHRIRLASH ============================

    @dp.message_handler(lambda m: m.text == "✏️ Savolni tahrirlash" and m.from_user.id in ADMINS)
    async def handle_edit_question(message: types.Message, state: FSMContext):
        await state.finish()
        await message.answer("🛠 Tahrir qilmoqchi bo‘lgan texnologiya nomini kiriting:")
        await AdminAddQuestion.choosing_tech_for_edit.set()

    @dp.message_handler(state=AdminAddQuestion.choosing_tech_for_edit, user_id=ADMINS)
    async def choose_tech_for_edit(message: types.Message, state: FSMContext):
        tech = message.text.strip().lower()
        file_path = get_file_path(tech)
        if not os.path.exists(file_path):
            await message.answer("❌ Fayl topilmadi.")
            return await state.finish()

        with open(file_path, "r", encoding="utf-8") as f:
            questions = json.load(f)

        if not questions:
            return await message.answer("📭 Hozircha savollar mavjud emas.")

        text = f"📋 {tech.title()} savollar ro‘yxati:\n"
        for i, q in enumerate(questions):
            text += f"{i+1}. {q['question']}\n"

        for part in split_text(text + "\n✏️ Qaysi savolni tahrirlamoqchisiz? Raqamini yuboring:"):
            await message.answer(part)

        await state.update_data(tech=tech, file_path=file_path, questions=questions)
        await AdminAddQuestion.choosing_question_index_for_edit.set()

    @dp.message_handler(state=AdminAddQuestion.choosing_question_index_for_edit, user_id=ADMINS)
    async def get_edit_index(message: types.Message, state: FSMContext):
        try:
            index = int(message.text.strip()) - 1
            await state.update_data(edit_index=index)
            await message.answer("✍️ Yangi savol matni (bo‘sh qoldirsangiz o‘zgarmaydi):")
            await AdminAddQuestion.editing_question_text.set()
        except ValueError:
            await message.answer("⚠️ Iltimos, faqat raqam yuboring.")

    @dp.message_handler(state=AdminAddQuestion.editing_question_text, user_id=ADMINS)
    async def get_new_question_text(message: types.Message, state: FSMContext):
        await state.update_data(new_question=message.text.strip())
        await message.answer("🧾 Yangi variantlarni yuboring (4 ta, bo‘sh qoldirsangiz o‘zgarmaydi):")
        await AdminAddQuestion.editing_options.set()

    @dp.message_handler(state=AdminAddQuestion.editing_options, user_id=ADMINS)
    async def get_new_options(message: types.Message, state: FSMContext):
        options = message.text.strip().split("\n") if message.text.strip() else []
        await state.update_data(new_options=options)
        await message.answer("✅ Yangi to‘g‘ri javobni kiriting (A/B/C/D, bo‘sh qoldirsangiz o‘zgarmaydi):")
        await AdminAddQuestion.editing_answer.set()

    @dp.message_handler(state=AdminAddQuestion.editing_answer, user_id=ADMINS)
    async def finalize_edit(message: types.Message, state: FSMContext):
        data = await state.get_data()
        index = data["edit_index"]
        questions = data["questions"]
        file_path = data["file_path"]

        if index < 0 or index >= len(questions):
            return await message.answer("❗ Noto‘g‘ri indeks.")

        if data.get("new_question"):
            questions[index]["question"] = data["new_question"]
        if data.get("new_options"):
            questions[index]["options"] = data["new_options"]

        if message.text.strip().upper() in ["A", "B", "C", "D"]:
            answer_index = ord(message.text.strip().upper()) - 65
            if data.get("new_options") and 0 <= answer_index < len(data["new_options"]):
                questions[index]["answer"] = data["new_options"][answer_index]

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=4)

        await message.answer("✅ Savol tahrirlandi.")
        await state.finish()

# ========================== 🗑 SAVOLNI O‘CHIRISH ==========================
    @dp.message_handler(lambda m: m.text == "🗑 Savolni o‘chirish", user_id=ADMINS)
    async def handle_delete_question(message: types.Message, state: FSMContext):
        await message.answer("🛠 O‘chirmoqchi bo‘lgan texnologiya nomini kiriting:")
        await AdminAddQuestion.choosing_tech_for_delete.set()

    @dp.message_handler(state=AdminAddQuestion.choosing_tech_for_delete, user_id=ADMINS)
    async def choose_tech_to_delete(message: types.Message, state: FSMContext):
        tech = message.text.strip().lower()
        file_path = get_file_path(tech)

        if not os.path.exists(file_path):
            await message.answer(f"❌ Fayl topilmadi: {tech.title()}. Iltimos, to‘g‘ri texnologiya nomini kiriting.")
            return await state.finish()

        with open(file_path, "r", encoding="utf-8") as f:
            questions = json.load(f)

        if not questions:
            return await message.answer("📭 Hozircha savollar mavjud emas.")

        text = f"📋 {tech.title()} savollar:\n"
        for i, q in enumerate(questions):
            text += f"{i+1}. {q['question']}\n"

        for part in split_text(text + "\n🗑 Qaysi savolni o‘chirmoqchisiz? Raqamini yuboring:"):
            await message.answer(part)

        await state.update_data(tech=tech, file_path=file_path, questions=questions)
        await AdminAddQuestion.choosing_question_index_for_delete.set()

    @dp.message_handler(state=AdminAddQuestion.choosing_question_index_for_delete, user_id=ADMINS)
    async def delete_question_by_index(message: types.Message, state: FSMContext):
        try:
            index = int(message.text.strip()) - 1
            data = await state.get_data()
            questions = data["questions"]
            file_path = data["file_path"]

            if 0 <= index < len(questions):
                deleted = questions.pop(index)
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(questions, f, ensure_ascii=False, indent=4)
                await message.answer(f"🗑 Savol o‘chirildi: {deleted['question']}")
            else:
                await message.answer("⚠️ Noto‘g‘ri raqam kiritildi. Iltimos, ro‘yxatdan mavjud bo‘lgan raqamni tanlang.")
        except ValueError:
            await message.answer("⚠️ Iltimos, faqat raqam yuboring.")

        await state.finish()

# Broadcasting part
    users_path = Path("data/Users/users.json")

    @dp.message_handler(lambda message: message.text == "📢 Broadcast")
    async def start_broadcast(message: types.Message, state: FSMContext):
        if message.from_user.id != ADMINS[0]:
            return await message.answer("⛔ Faqatgina bosh admin 📢 Broadcast qila oladi, sizga ruxsat yo'q!")

        await message.answer("✉️ Iltimos, yuboriladigan xabar matnini kiriting:")
        await AdminBroadcastState.waiting_for_message.set()    

    @dp.message_handler(state=AdminBroadcastState.waiting_for_message)
    async def send_broadcast_to_all(message: types.Message, state: FSMContext):
        if message.from_user.id != ADMINS[0]:
            return await message.answer("⛔ Faqatgina bosh admin 📢 Broadcast qila oladi, sizga ruxsat yo'q!")

        if not users_path.exists():
            await message.answer("📭 Hozircha foydalanuvchilar ro‘yxati mavjud emas.")
            return await state.finish()

        with open(users_path, "r", encoding="utf-8") as f:
            users = json.load(f)

        success, failed = 0, 0
        for user in users:
            try:
                await dp.bot.send_message(user["id"], message.text)
                success += 1
            except:
                failed += 1

        await message.answer(f"✅ Xabar yuborildi: {success} ta\n❌ Xatolik: {failed} ta")
        await state.finish()