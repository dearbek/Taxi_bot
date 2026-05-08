import asyncio
import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import DefaultBotProperties

async def main():
    logging.basicConfig(level=logging.INFO)
    
    while True: # Aloqa uzilsa bot o'chib qolmasligi uchun tsikl
        try:
            print("Bot ishga tushmoqda...")
            await dp.start_polling(bot)
        except Exception as e:
            print(f"Aloqada xatolik: {e}")
            print("5 soniyadan so'ng qayta ulanishga harakat qilinadi...")
            await asyncio.sleep(5) # 5 soniya kutib, keyin qayta urinadi
# Load .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# 1. Registration States
class DriverForm(StatesGroup):
    name = State()
    phone = State()
    license = State()

# Setup Bot with longer timeout to prevent "Semaphore" errors
session = AiohttpSession()
bot = Bot(
    token=TOKEN, 
    session=session,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()

# --- HANDLERS ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        "<b>Assalomu alaykum!</b> 👋\n\n"
        "Taxi xizmatimizga ishga taklif qilamiz. Ro'yxatdan o'tish uchun iltimos <b>F.I.SH. (Ism, Familiya)</b>ingizni yuboring:"
    )
    await state.set_state(DriverForm.name)

@dp.message(DriverForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    
    # Keyboard for phone sharing
    kb = [[types.KeyboardButton(text="📱 Kontaktni yuborish", request_contact=True)]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    
    await message.answer(
        f"Rahmat, {message.text}! Endi pastdagi tugmani bosib <b>telefon raqamingizni</b> yuboring:",
        reply_markup=keyboard
    )
    await state.set_state(DriverForm.phone)

@dp.message(DriverForm.phone, F.contact)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    
    await message.answer(
        "Ajoyib! Oxirgi bosqich: Iltimos, <b>haydovchilik guvohnomangiz</b> (prava) rasmini yuboring.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(DriverForm.license)

@dp.message(DriverForm.license, F.photo)
async def process_license(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photo_id = message.photo[-1].file_id # Get the highest quality photo
    
    # Simulation: Printing the data to terminal
    print(f"--- YANGI ARIZA ---")
    print(f"Ism: {data['full_name']}")
    print(f"Tel: {data['phone']}")
    print(f"Rasm ID: {photo_id}")
    
    await message.answer(
        "✅ <b>Tabriklaymiz!</b> Arizangiz qabul qilindi.\n"
        "Tez orada operatorlarimiz siz bilan bog'lanishadi. Rahmat!"
    )
    await state.clear()

async def main():
    logging.basicConfig(level=logging.INFO)
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")

if __name__ == "__main__":
    asyncio.run(main())