import asyncio
import json
import os
from uuid import uuid4
from datetime import datetime
from pathlib import Path
from typing import Any

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ContentType
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")
NOTIFY_CHAT_ID = GROUP_CHAT_ID or ADMIN_CHAT_ID
DATA_DIR = Path("data")
APPLICATIONS_FILE = DATA_DIR / "applications.jsonl"
WELCOME_IMAGES = [Path("imagee.png"), Path("image.png")]


DIRECTIONS = [
    "Backend",
    "Frontend",
    "Sotuv",
    "Sun'iy intellekt",
    "Call center",
    "Mobil dasturlash",
    "Grafik dizayn",
    "SMM",
    "HR",
    "Boshqa",
]

PURPOSES = ["Ishchi", "Amaliyot", "Stajirovka", "Hamkorlik"]
START_BUTTON_TEXT = "🚀 Anketani to'ldirish"


class ApplicationForm(StatesGroup):
    full_name = State()
    age = State()
    phone = State()
    photo = State()
    direction = State()
    purpose = State()
    cv = State()
    intro_video = State()
    skills = State()
    experience_years = State()
    previous_jobs = State()
    gained_experience = State()
    projects = State()
    ai_tools = State()
    ai_tools_reason = State()
    special_skills = State()
    cooperation_period = State()
    offline_work = State()


def make_keyboard(items: list[str], row_width: int = 2) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=item) for item in items[index : index + row_width]]
        for index in range(0, len(items), row_width)
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def start_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=START_BUTTON_TEXT)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def yes_no_keyboard() -> ReplyKeyboardMarkup:
    return make_keyboard(["Ha", "Yo'q"], row_width=2)


def format_stage(title: str) -> str:
    return f"━━━━━━━━━━━━━━━\n{title}\n━━━━━━━━━━━━━━━"


async def save_application(data: dict[str, Any], message: Message) -> dict[str, Any]:
    DATA_DIR.mkdir(exist_ok=True)
    application = {
        "id": uuid4().hex,
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "telegram_user": {
            "id": message.from_user.id if message.from_user else None,
            "username": message.from_user.username if message.from_user else None,
            "first_name": message.from_user.first_name if message.from_user else None,
            "last_name": message.from_user.last_name if message.from_user else None,
        },
        "answers": data,
    }

    with APPLICATIONS_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(application, ensure_ascii=False) + "\n")

    return application


def find_application(application_id: str) -> dict[str, Any] | None:
    if not APPLICATIONS_FILE.exists():
        return None

    with APPLICATIONS_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            application = json.loads(line)
            if application.get("id") == application_id:
                return application

    return None


def format_admin_summary(application: dict[str, Any]) -> str:
    answers = application["answers"]
    user = application["telegram_user"]
    username = f"@{user['username']}" if user.get("username") else "username yo'q"

    return (
        "🆕 Yangi anketa\n\n"
        f"👤 Telegram: {username} | ID: {user.get('id')}\n"
        f"Ism-familiya: {answers.get('full_name')}\n"
        f"Yosh: {answers.get('age')}\n"
        f"Telefon: {answers.get('phone')}\n"
        f"Yo'nalish: {answers.get('direction')}\n"
        f"Maqsad: {answers.get('purpose')}\n"
        f"Tajriba: {answers.get('experience_years')}\n"
        f"Offline: {answers.get('offline_work')}\n\n"
        f"Ko'nikmalar: {answers.get('skills')}\n\n"
        f"AI vositalar: {answers.get('ai_tools')}\n"
        f"Maxsus ko'nikmalar: {answers.get('special_skills')}"
    )


def admin_application_keyboard(application: dict[str, Any]) -> InlineKeyboardMarkup:
    application_id = application["id"]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📸 Rasm",
                    callback_data=f"app:{application_id}:photo",
                ),
                InlineKeyboardButton(
                    text="📄 CV",
                    callback_data=f"app:{application_id}:cv",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🎥 Video",
                    callback_data=f"app:{application_id}:video",
                ),
            ],
        ]
    )


async def start_form(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(ApplicationForm.purpose)
    await message.answer(
        "Anketa maqsadini tanlang.\n"
        "Nima uchun ariza topshiryapsiz?",
        reply_markup=make_keyboard(PURPOSES, row_width=2),
    )


async def show_welcome(message: Message, state: FSMContext) -> None:
    await state.clear()
    welcome_text = (
        "👋 Assalomu alaykum!\n"
        "ASOS IT jamoasiga xush kelibsiz.\n\n"
        "📋 HODIMLAR UCHUN ANKETA\n"
        "Jamoamizga qo'shilishni istasangiz, quyidagi savollarga to'liq va aniq javob yuboring.\n\n"
        "📌 Anketa 16 ta savoldan iborat va 5 bosqichga bo'lingan:\n"
        "  1️⃣ Shaxsiy ma'lumotlar\n"
        "  2️⃣ Kasbiy ma'lumotlar\n"
        "  3️⃣ Tajriba va loyihalar\n"
        "  4️⃣ AI va zamonaviy bilimlar\n"
        "  5️⃣ Hamkorlik shartlari\n\n"
        "⏱ Taxminiy vaqt: 5-10 daqiqa\n"
        "❌ Istalgan paytda /cancel orqali bekor qilishingiz mumkin.\n\n"
        "Boshlash uchun pastdagi «🚀 Anketani to'ldirish» tugmasini bosing. 🚀"
    )
    welcome_image = next((image for image in WELCOME_IMAGES if image.exists()), None)

    if welcome_image:
        await message.answer_photo(
            FSInputFile(welcome_image),
            caption=welcome_text,
            reply_markup=start_keyboard(),
        )
        return

    await message.answer(welcome_text, reply_markup=start_keyboard())


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN .env faylida berilmagan.")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    @dp.message(CommandStart())
    async def command_start(message: Message, state: FSMContext) -> None:
        await show_welcome(message, state)

    @dp.message(F.text == START_BUTTON_TEXT)
    async def process_start_button(message: Message, state: FSMContext) -> None:
        await start_form(message, state)

    @dp.message(Command("cancel"))
    async def command_cancel(message: Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer(
            "Anketa bekor qilindi. Qayta boshlash uchun /start bosing.",
            reply_markup=ReplyKeyboardRemove(),
        )

    @dp.message(ApplicationForm.full_name, F.text)
    async def process_full_name(message: Message, state: FSMContext) -> None:
        await state.update_data(full_name=message.text.strip())
        await state.set_state(ApplicationForm.age)
        await message.answer("2. Yoshingiz nechida?\n(Masalan: 25)")

    @dp.message(ApplicationForm.age, F.text)
    async def process_age(message: Message, state: FSMContext) -> None:
        text = message.text.strip()
        if not text.isdigit() or not 14 <= int(text) <= 100:
            await message.answer("Iltimos, yoshingizni faqat raqam bilan yozing. Masalan: 25")
            return

        await state.update_data(age=int(text))
        await state.set_state(ApplicationForm.phone)
        await message.answer(
            "3. Telefon raqamingizni yuboring\n📱 «Raqamni yuborish» tugmasini bosing.",
            reply_markup=contact_keyboard(),
        )

    @dp.message(ApplicationForm.phone, F.contact)
    async def process_phone_contact(message: Message, state: FSMContext) -> None:
        await state.update_data(phone=message.contact.phone_number)
        await state.set_state(ApplicationForm.photo)
        await message.answer(
            "4. O'zingizning rasmingizni yuboring 📸",
            reply_markup=ReplyKeyboardRemove(),
        )

    @dp.message(ApplicationForm.phone, F.text)
    async def process_phone_text(message: Message, state: FSMContext) -> None:
        await state.update_data(phone=message.text.strip())
        await state.set_state(ApplicationForm.photo)
        await message.answer(
            "4. O'zingizning rasmingizni yuboring 📸",
            reply_markup=ReplyKeyboardRemove(),
        )

    @dp.message(ApplicationForm.photo, F.photo)
    async def process_photo(message: Message, state: FSMContext) -> None:
        await state.update_data(photo_file_id=message.photo[-1].file_id)
        await state.set_state(ApplicationForm.cv)
        await message.answer(
            format_stage("2-BOSQICH: KASBIY MA'LUMOTLAR") + "\n\n"
            "5. CV faylingizni yuboring 📄\n(PDF yoki Word formatida)",
            reply_markup=ReplyKeyboardRemove(),
        )

    @dp.message(ApplicationForm.photo)
    async def invalid_photo(message: Message) -> None:
        await message.answer("Iltimos, o'zingizning rasmingizni foto sifatida yuboring 📸")

    @dp.message(ApplicationForm.direction, F.text)
    async def process_direction(message: Message, state: FSMContext) -> None:
        await state.update_data(direction=message.text.strip())
        await state.set_state(ApplicationForm.full_name)
        await message.answer(
            format_stage("1-BOSQICH: SHAXSIY MA'LUMOTLAR") + "\n\n"
            "1. Ism-familiyangizni to'liq yozing\n"
            "(Masalan: Ali Valiyev)",
            reply_markup=ReplyKeyboardRemove(),
        )

    @dp.message(ApplicationForm.purpose, F.text)
    async def process_purpose(message: Message, state: FSMContext) -> None:
        await state.update_data(purpose=message.text.strip())
        await state.set_state(ApplicationForm.direction)
        await message.answer(
            "Qaysi yo'nalish uchun ariza topshiryapsiz?",
            reply_markup=make_keyboard(DIRECTIONS),
        )

    @dp.message(ApplicationForm.cv, F.document)
    async def process_cv(message: Message, state: FSMContext) -> None:
        document = message.document
        allowed_extensions = (".pdf", ".doc", ".docx")
        file_name = (document.file_name or "").lower()

        if file_name and not file_name.endswith(allowed_extensions):
            await message.answer("CV fayli PDF yoki Word formatida bo'lishi kerak: .pdf, .doc, .docx")
            return

        await state.update_data(
            cv_file_id=document.file_id,
            cv_file_name=document.file_name,
        )
        await state.set_state(ApplicationForm.intro_video)
        await message.answer(
            "6. O'zingiz haqingizda 1-2 daqiqalik video yuboring 🎥\n"
            "(Kim ekanligingiz, nima bilan shug'ullanishingiz haqida qisqacha)"
        )

    @dp.message(ApplicationForm.cv)
    async def invalid_cv(message: Message) -> None:
        await message.answer("Iltimos, CV faylingizni document sifatida yuboring 📄")

    @dp.message(ApplicationForm.intro_video, F.content_type.in_({ContentType.VIDEO, ContentType.VIDEO_NOTE}))
    async def process_intro_video(message: Message, state: FSMContext) -> None:
        video = message.video or message.video_note
        await state.update_data(
            intro_video_file_id=video.file_id,
            intro_video_type=message.content_type,
        )
        await state.set_state(ApplicationForm.skills)
        await message.answer(
            "7. Qaysi soha yoki yo'nalishda ishlaysiz va nimalarni bilasiz?\n"
            "(texnologiyalar, ko'nikmalar, dasturlar)"
        )

    @dp.message(ApplicationForm.intro_video)
    async def invalid_intro_video(message: Message) -> None:
        await message.answer("Iltimos, o'zingiz haqingizda video yuboring 🎥")

    @dp.message(ApplicationForm.skills, F.text)
    async def process_skills(message: Message, state: FSMContext) -> None:
        await state.update_data(skills=message.text.strip())
        await state.set_state(ApplicationForm.experience_years)
        await message.answer("8. Umumiy ish tajribangiz necha yil?")

    @dp.message(ApplicationForm.experience_years, F.text)
    async def process_experience_years(message: Message, state: FSMContext) -> None:
        await state.update_data(experience_years=message.text.strip())
        await state.set_state(ApplicationForm.previous_jobs)
        await message.answer(
            format_stage("3-BOSQICH: TAJRIBA VA LOYIHALAR") + "\n\n"
            "9. Avval qaysi joylarda ishlagansiz?\n"
            "(Kompaniya nomi, lavozim, ishlagan muddati)"
        )

    @dp.message(ApplicationForm.previous_jobs, F.text)
    async def process_previous_jobs(message: Message, state: FSMContext) -> None:
        await state.update_data(previous_jobs=message.text.strip())
        await state.set_state(ApplicationForm.gained_experience)
        await message.answer("10. O'sha joylarda qanday tajribalar oldingiz?\n(Qisqacha yozing)")

    @dp.message(ApplicationForm.gained_experience, F.text)
    async def process_gained_experience(message: Message, state: FSMContext) -> None:
        await state.update_data(gained_experience=message.text.strip())
        await state.set_state(ApplicationForm.projects)
        await message.answer(
            "11. Qanday loyihalarda qatnashgansiz?\n"
            "(Loyiha nomi, sizning rolingiz, natija)"
        )

    @dp.message(ApplicationForm.projects, F.text)
    async def process_projects(message: Message, state: FSMContext) -> None:
        await state.update_data(projects=message.text.strip())
        await state.set_state(ApplicationForm.ai_tools)
        await message.answer(
            format_stage("4-BOSQICH: AI VA ZAMONAVIY BILIMLAR") + "\n\n"
            "12. Hozirda qanday AI vositalardan foydalanasiz?\n"
            "(ChatGPT, Claude, Midjourney va h.k.)"
        )

    @dp.message(ApplicationForm.ai_tools, F.text)
    async def process_ai_tools(message: Message, state: FSMContext) -> None:
        await state.update_data(ai_tools=message.text.strip())
        await state.set_state(ApplicationForm.ai_tools_reason)
        await message.answer(
            "13. Nima uchun aynan shu AI vositalardan foydalanasiz?\n"
            "Ish jarayoningizda qanday yordam beradi?"
        )

    @dp.message(ApplicationForm.ai_tools_reason, F.text)
    async def process_ai_tools_reason(message: Message, state: FSMContext) -> None:
        await state.update_data(ai_tools_reason=message.text.strip())
        await state.set_state(ApplicationForm.special_skills)
        await message.answer(
            "14. Boshqalar qiynaladigan yoki bilmaydigan qanday maxsus bilim va ko'nikmalaringiz bor?\n"
            "(Sizni boshqalardan ajratib turadigan tomonlaringiz)"
        )

    @dp.message(ApplicationForm.special_skills, F.text)
    async def process_special_skills(message: Message, state: FSMContext) -> None:
        await state.update_data(special_skills=message.text.strip())
        await state.set_state(ApplicationForm.cooperation_period)
        await message.answer(
            format_stage("5-BOSQICH: HAMKORLIK SHARTLARI") + "\n\n"
            "15. Biz bilan qancha vaqt ishlashni rejalashtiryapsiz?\n"
            "(1 yil, uzoq muddat va h.k.)"
        )

    @dp.message(ApplicationForm.cooperation_period, F.text)
    async def process_cooperation_period(message: Message, state: FSMContext) -> None:
        await state.update_data(cooperation_period=message.text.strip())
        await state.set_state(ApplicationForm.offline_work)
        await message.answer(
            "16. Farg'onaga kelib offline (ofisda) ishlay olasizmi?",
            reply_markup=yes_no_keyboard(),
        )

    @dp.message(ApplicationForm.offline_work, F.text)
    async def process_offline_work(message: Message, state: FSMContext, bot: Bot) -> None:
        await state.update_data(offline_work=message.text.strip())
        data = await state.get_data()
        application = await save_application(data, message)
        await state.clear()

        await message.answer(
            "Rahmat! Anketangiz qabul qilindi. Tez orada siz bilan bog'lanamiz.",
            reply_markup=ReplyKeyboardRemove(),
        )

        if NOTIFY_CHAT_ID:
            await bot.send_message(
                NOTIFY_CHAT_ID,
                format_admin_summary(application),
                reply_markup=admin_application_keyboard(application),
            )

    @dp.callback_query(F.data.startswith("app:"))
    async def process_admin_application_button(callback: CallbackQuery, bot: Bot) -> None:
        parts = (callback.data or "").split(":")
        if len(parts) != 3:
            await callback.answer("Noto'g'ri tugma ma'lumoti.", show_alert=True)
            return

        _, application_id, file_type = parts
        application = find_application(application_id)
        if not application:
            await callback.answer("Anketa topilmadi.", show_alert=True)
            return

        answers = application["answers"]
        chat_id = callback.message.chat.id

        if file_type == "photo":
            file_id = answers.get("photo_file_id")
            if not file_id:
                await callback.answer("Rasm topilmadi.", show_alert=True)
                return
            await bot.send_photo(chat_id, file_id, caption="📸 Nomzod rasmi")

        elif file_type == "cv":
            file_id = answers.get("cv_file_id")
            if not file_id:
                await callback.answer("CV topilmadi.", show_alert=True)
                return
            await bot.send_document(chat_id, file_id, caption="📄 Nomzod CV fayli")

        elif file_type == "video":
            file_id = answers.get("intro_video_file_id")
            if not file_id:
                await callback.answer("Video topilmadi.", show_alert=True)
                return

            if answers.get("intro_video_type") == ContentType.VIDEO_NOTE:
                await bot.send_video_note(chat_id, file_id)
            else:
                await bot.send_video(chat_id, file_id, caption="🎥 Nomzod videosi")

        else:
            await callback.answer("Bunday fayl turi yo'q.", show_alert=True)
            return

        await callback.answer("Yuborildi.")

    @dp.message()
    async def unknown_message(message: Message) -> None:
        await message.answer("Anketani boshlash uchun /start buyrug'ini bosing.")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
