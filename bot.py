import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8780483285:AAEvELoYzQtwG9jTo9ueLEm3Ve5idK3GfUg"
ADMIN_ID = 8620457869

# Xatoliklarni aniq ko'rsatib turish uchun sozlama
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    stream=sys.stdout
)

bot = Bot(token=TOKEN)
dp = Dispatcher()

class RegisterState(StatesGroup):
    full_name = State()
    phone = State()
    school = State()
    direction = State()

def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Onlayn ro'yxatdan o'tish")],
            [KeyboardButton(text="📚 Kasb yo'nalishlari"), KeyboardButton(text="❓ FAQ")],
            [KeyboardButton(text="📞 Bog'lanish va manzil")]
        ],
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n"
        "Sherobod tumanidagi 4-sonli texnikumining rasmiy qabul botiga xush kelibsiz. Kerakli bo'limni tanlang:",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

@dp.message(F.text == "📚 Kasb yo'nalishlari")
async def show_courses(message: types.Message):
    text = (
        "📚 <b>Sherobod 4-sonli texnikumida mavjud yo'nalishlar:</b>\n\n"
        "1. Tikuvchilik va bichish texnologiyasi\n"
        "2. Payvandlovchi (elektrogazpayvandchi)\n"
        "3. Buhgalteriya hisobi va audit\n"
        "4. Kompyuter injineringi\n\n"
        "Ro'yxatdan o'tish uchun '📝 Onlayn ro'yxatdan o'tish' tugmasini bosing."
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text == "❓ FAQ")
async def show_faq(message: types.Message):
    await message.answer("❓ Ko'p beriladigan savollar tez orada qo'shiladi.", parse_mode="HTML")

@dp.message(F.text == "📞 Bog'lanish va manzil")
async def show_contact(message: types.Message):
    text = (
        "📍 <b>Manzil:</b> Surxondaryo viloyati, Sherobod tumani.\n"
        "📞 <b>Qabul komissiyasi:</b> +998 90 123 45 67\n"
        "🌐 <b>Mo'ljal:</b> Texnikum binosi."
    )
    await message.answer(text, parse_mode="HTML")

# --- ANKETA JARAYONI ---

@dp.message(F.text == "📝 Onlayn ro'yxatdan o'tish")
async def start_register(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Iltimos, to'liq F.I.SH. (Familiya Ism Sharifingiz)ni kiriting:")
    await state.set_state(RegisterState.full_name)

@dp.message(RegisterState.full_name)
async def process_fullname(message: types.Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 3:
        await message.answer("⚠️ Iltimos, ism va familiyangizni to'g'ri kiriting:")
        return
    
    await state.update_data(full_name=message.text.strip())
    
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Endi telefon raqamingizni yuboring (pastdagi tugmani bosing yoki yozib yuboring):", reply_markup=kb)
    await state.set_state(RegisterState.phone)

@dp.message(RegisterState.phone)
async def process_phone(message: types.Message, state: FSMContext):
    if message.contact:
        phone_number = message.contact.phone_number
    elif message.text:
        phone_number = message.text.strip()
    else:
        await message.answer("⚠️ Iltimos, telefon raqamingizni kiriting:")
        return
        
    await state.update_data(phone=phone_number)
    await message.answer("Qaysi maktabni tamomlagansiz va nechanchi sinf?", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(RegisterState.school)

@dp.message(RegisterState.school)
async def process_school(message: types.Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 2:
        await message.answer("⚠️ Iltimos, maktab va sinfingizni kiriting:")
        return
        
    await state.update_data(school=message.text.strip())
    
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Tikuvchilik", callback_data="dir_tikuv")],
            [InlineKeyboardButton(text="Payvandlovchi", callback_data="dir_payvand")],
            [InlineKeyboardButton(text="Buxgalteriya", callback_data="dir_bux")],
            [InlineKeyboardButton(text="Kompyuter injineringi", callback_data="dir_komp")]
        ]
    )
    await message.answer("Qaysi yo'nalishda o'qishni xohlaysiz? Tanlang:", reply_markup=kb)
    await state.set_state(RegisterState.direction)

@dp.callback_query(RegisterState.direction, F.data.startswith("dir_"))
async def process_direction(callback: types.CallbackQuery, state: FSMContext):
    directions = {
        "dir_tikuv": "Tikuvchilik va bichish texnologiyasi",
        "dir_payvand": "Payvandlovchi",
        "dir_bux": "Buxgalteriya",
        "dir_komp": "Kompyuter injineringi"
    }
    
    selected_dir = directions.get(callback.data, "Noma'lum")
    data = await state.get_data()
    
    report_text = (
        "🚨 <b>Yangi ariza keldi!</b>\n\n"
        f"👤 <b>F.I.SH:</b> {data.get('full_name')}\n"
        f"📱 <b>Telefon:</b> {data.get('phone')}\n"
        f"🏫 <b>Maktab/Sinf:</b> {data.get('school')}\n"
        f"📚 <b>Yo'nalish:</b> {selected_dir}\n"
        f"🔗 <b>Foydalanuvchi:</b> @{callback.from_user.username or 'mavjud_emas'} (ID: {callback.from_user.id})"
    )
    
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=report_text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Adminga yuborishda xatolik: {e}")
    
    await callback.message.answer("✅ Ma'lumotlaringiz muvaffaqiyatli qabul qilindi! Tez orada siz bilan bog'lanishadi.", reply_markup=get_main_menu())
    await callback.answer()
    await state.clear()

@dp.message()
async def fallback_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Iltimos, tugmalardan birini tanlang yoki /start buyrug'ini bosing:", reply_markup=get_main_menu())
    else:
        await message.answer("⚠️ Iltimos, yuqoridagi ko'rsatmaga muvofiq ma'lumot kiriting.")

async def main():
    while True:
        try:
            logging.info("Bot ishga tushmoqda...")
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
        except Exception as e:
            logging.error(f"Xatolik yuz berdi: {e}. 5 soniyadan so'ng qayta ulanadi...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi!")
  
