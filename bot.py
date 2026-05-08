import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import DefaultBotProperties

# --- SOZLAMALAR ---
TOKEN = token
ADMIN_CHANNEL = "-1003929280594"

class DriverForm(StatesGroup):
    name = State()
    phone = State()
    license = State()

session = AiohttpSession()
bot = Bot(token=TOKEN, session=session, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("<b>Assalomu alaykum!</b>\nRo'yxatdan o'tish uchun ismingizni yuboring:")
    await state.set_state(DriverForm.name)

@dp.message(DriverForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    kb = [[types.KeyboardButton(text="📱 Kontaktni yuborish", request_contact=True)]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Telefon raqamingizni yuboring:", reply_markup=keyboard)
    await state.set_state(DriverForm.phone)

@dp.message(DriverForm.phone, F.contact)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await message.answer("Guvohnoma (prava) rasmini yuboring:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(DriverForm.license)

@dp.message(DriverForm.license, F.photo)
async def process_license(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photo_id = message.photo[-1].file_id
    
    # Text for the channel
    admin_caption = (
        "🚕 <b>YANGI ARIZA</b>\n\n"
        f"👤 Ism: {data['full_name']}\n"
        f"📞 Tel: {data['phone']}\n"
        f"🆔 User: @{message.from_user.username if message.from_user.username else 'Nomaum'}"
    )

    print(f"DEBUG: Attempting to send to {ADMIN_CHANNEL}")
    
    try:
        await bot.send_photo(
            chat_id=ADMIN_CHANNEL,
            photo=photo_id,
            caption=admin_caption
        )
        print("DEBUG: Channel update sent successfully!")
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
    
    await message.answer("✅ Arizangiz qabul qilindi!")
    await state.clear()

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
