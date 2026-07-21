import os
import asyncio
import logging
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8780483285:AAEvELoYzQtwG9jTo9ueLEm3Ve5idK3GfUg"
ADMIN_ID = 8620457869

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    stream=sys.stdout
)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- RENDER UCHUN VEB-SERVER QISMI ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

def start_web_server():
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
# ------------------------------------

class RegisterState(StatesGroup):
    full_name = State()
    phone = State()
    school = State()
    grade_type = State()
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
        "Sherobod tumanidagi 4-sonli texnikumining rasmiy qabul botiga xush kelibsiz. Kelajagingni biz bilan qur! Kerakli bo'limni tanlang:",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

@dp.message(F.text == "📚 Kasb yo'nalishlari")
async def show_courses(message: types.Message):
    text = (
        "🎓 <b>Sherobod 4-sonli texnikumida mavjud yo'nalishlar:</b>\n\n"
        "<b>📌 9-sinf bitiruvchilari uchun:</b>\n"
        "1. Moda va tikuv ishlab chiqarish texnologiyasi\n"
        "2. Kompyuter tarmoqlari va IT sevisi\n"
        "3. Raqamli va smart maishiy texnika jihozlariga servis\n"
        "4. Avtomobillar servisi\n\n"
        "<b>📌 11-sinf bitiruvchilari va yuqori yoshlar uchun:</b>\n"
        "5. Sport faoliyati va faoliyat turlari bo'yicha\n"
        "6. Kutubxona va bibliografiya (Dual ta'lim shaklida)\n"
        "7. Maktabgacha ta'lim tashkilotlari tarbiyachisi (Dual ta'lim)\n"
        "8. Axborot va kiber xavfsizligi (Dual ta'lim shaklida)\n\n"
        "Ro'yxatdan o'tish uchun '📝 Onlayn ro'yxatdan o'tish' tugmasini bosing."
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text == "❓ FAQ")
async def show_faq(message: types.Message):
    await message.answer("❓ Ko'p beriladigan savollar tez orada qo'shiladi.", parse_mode="HTML")

@dp.message(F.text == "📞 Bog'lanish va manzil")
async def show_contact(message: types.Message):
    text = (
        "📍 <b>Manzil:</b> Surxondaryo viloyati, Sherobod tumani, Do'stlik MFY, Mustaqillik 3-uy (4-son Texnikum).\n\n"
        "📞 <b>Qabul komissiyasi raqamlari:</b>\n"
        "• 94-205-62-46\n"
        "• 94-515-71-75\n"
        "• 94-516-28-82\n\n"
        "🌐 <i>Biz bilan kelajagingizni yarating! Sifatli ta'lim va amaliyotga yo'naltirilgan ta'lim.</i>"
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
            [InlineKeyboardButton(text="9-sinf bitiruvchisi", callback_data="category_9")],
            [InlineKeyboardButton(text="11-sinf / Yuqori yoshlar", callback_data="category_11")]
        ]
    )
    await message.answer("Ta'lim olmoqchi bo'lgan toifangizni tanlang:", reply_markup=kb)
    await state.set_state(RegisterState.grade_type)

@dp.callback_query(RegisterState.grade_type, F.data.startswith("category_"))
async def process_grade_type(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "category_9":
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="👗 Moda va tikuv ishlab chiqarish texnologiyasi", callback_data="dir_moda")],
                [InlineKeyboardButton(text="💻 Kompyuter tarmoqlari va IT sevisi", callback_data="dir_it")],
                [InlineKeyboardButton(text="🔧 Raqamli va smart maishiy texnika", callback_data="dir_texnika")],
                [InlineKeyboardButton(text="🚗 Avtomobillar servisi", callback_data="dir_auto")]
            ]
        )
        await callback.message.edit_text("9-sinf yo'nalishlaridan birini tanlang:", reply_markup=kb)
    else:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⚽ Sport faoliyati va faoliyat turlari", callback_data="dir_sport")],
                [InlineKeyboardButton(text="📚 Kutubxona va bibliografiya (Dual)", callback_data="dir_kutubxona")],
                [InlineKeyboardButton(text="👶 Maktabgacha ta'lim (Dual)", callback_data="dir_maktabgacha")],
                [InlineKeyboardButton(text="🛡️ Axborot va kiber xavfsizligi (Dual)", callback_data="dir_kiber")]
            ]
        )
        await callback.message.edit_text("11-sinf va yuqori yoshlar yo'nalishlaridan birini tanlang:", reply_markup=kb)
    
    await state.set_state(RegisterState.direction)
    await callback.answer()

@dp.callback_query(RegisterState.direction, F.data.startswith("dir_"))
async def process_direction(callback: types.CallbackQuery, state: FSMContext):
    directions = {
        "dir_moda": "Moda va tikuv ishlab chiqarish texnologiyasi (9-sinf)",
        "dir_it": "Kompyuter tarmoqlari va IT sevisi (9-sinf)",
        "dir_texnika": "Raqamli va smart maishiy texnika jihozlariga servis (9-sinf)",
        "dir_auto": "Avtomobillar servisi (9-sinf)",
        "dir_sport": "Sport faoliyati va faoliyat turlari bo'yicha (11-sinf)",
        "dir_kutubxona": "Kutubxona va bibliografiya - Dual ta'lim (11-sinf)",
        "dir_maktabgacha": "Maktabgacha ta'lim tashkilotlari tarbiyachisi - Dual ta'lim (11-sinf)",
        "dir_kiber": "Axborot va kiber xavfsizligi - Dual ta'lim (11-sinf)"
    }
    
    selected_dir = directions.get(callback.data, "Noma'lum")
    data = await state.get_data()
    
    report_text = (
        "🚨 <b>Yangi ariza keldi!</b>\n\n"
        f"👤 <b>F.I.SH:</b> {data.get('full_name')}\n"
        f"📱 <b>Telefon:</b> {data.get('phone')}\n"
        f"🏫 <b>Maktab/Sinf:</b> {data.get('school')}\n"
        f"📚 <b>Tanlangan yo'nalish:</b> {selected_dir}\n"
        f"🔗 <b>Foydalanuvchi:</b> @{callback.from_user.username or 'mavjud_emas'} (ID: {callback.from_user.id})"
    )
    
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=report_text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Adminga yuborishda xatolik: {e}")
    
    await callback.message.answer("✅ Ma'lumotlaringiz muvaffaqiyatli qabul qilindi! Tez orada qabul komissiyasi siz bilan bog'lanadi.", reply_markup=get_main_menu())
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
    # 1. Render talabini bajarish uchun veb-serverni ishga tushiramiz
    start_web_server()
    
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
            
