from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from bot.states.registration import RegistrationStates
from bot.config import BACKEND_URL, ADMIN_ID
import requests
from bot.utils.pending_users import pending_approvals


router = Router()

@router.message(CommandStart())
async def start_registration(message: Message, state: FSMContext):
    user_telegram_id = message.from_user.id

    try:
        # 🔎 Backend orqali userni qidiramiz
        user_res = requests.get(f"{BACKEND_URL}/api/users/", params={"telegram_id": user_telegram_id})
        user_list = user_res.json()

        if user_list:  # User mavjud
            await message.answer("✅ Siz allaqachon ro'yxatdan o'tgansiz.")
            return

    except Exception as e:
        await message.answer(f"❌ Server bilan bog‘lanishda xatolik: {str(e)}")
        return

    await message.answer("Assalomu alaykum!\nIltimos, foydalanuvchi ID raqamingizni kiriting:")
    await state.set_state(RegistrationStates.waiting_for_user_id)

@router.message(RegistrationStates.waiting_for_user_id)
async def get_user_id(message: Message, state: FSMContext):
    await state.update_data(user_id=message.text)
    await message.answer("Ismingizni kiriting:")
    await state.set_state(RegistrationStates.waiting_for_first_name)

@router.message(RegistrationStates.waiting_for_first_name)
async def get_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Familiyangizni kiriting:")
    await state.set_state(RegistrationStates.waiting_for_last_name)

@router.message(RegistrationStates.waiting_for_last_name)
async def get_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("Sharifingizni kiriting:")
    await state.set_state(RegistrationStates.waiting_for_middle_name)

@router.message(RegistrationStates.waiting_for_middle_name)
async def get_middle_name(message: Message, state: FSMContext):
    await state.update_data(middle_name=message.text)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await message.answer("📱 Telefon raqamingizni yuboring:", reply_markup=keyboard)
    await state.set_state(RegistrationStates.waiting_for_phone)

@router.message(RegistrationStates.waiting_for_phone, F.contact)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(
        phone_number=message.contact.phone_number,
        telegram_id=message.from_user.id
    )
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="TM")],
            [KeyboardButton(text="TS")],
            [KeyboardButton(text="TA")]
        ],
        resize_keyboard=True, one_time_keyboard=True
    )
    await message.answer("Lavozimingizni tanlang:", reply_markup=keyboard)
    await state.set_state(RegistrationStates.waiting_for_role)

@router.message(RegistrationStates.waiting_for_role)
async def confirm_data(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(role=message.text)
    data = await state.get_data()

    full_name = f"{data['last_name']} {data['first_name']} {data['middle_name']}"
    user_telegram_id = data["telegram_id"]

    # Saqlab qo‘yamiz
    pending_approvals[user_telegram_id] = {
        "user_id": data["user_id"],
        "telegram_id": user_telegram_id,
        "full_name": full_name,
        "phone_number": data["phone_number"],
        "role": data["role"]
    }

    text = (
        f"🆕 Yangi foydalanuvchi ro'yxatdan o'tmoqchi:\n\n"
        f"🆔 ID: {data['user_id']}\n"
        f"👤 Ismi: {full_name}\n"
        f"📞 Tel: {data['phone_number']}\n"
        f"🎯 Rol: {data['role']}\n"
        f"Telegram ID: {user_telegram_id}\n\n"
        f"Ruxsat berilsinmi?"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ruxsat berish", callback_data=f"approve:{user_telegram_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject:{user_telegram_id}")
            ]
        ]
    )

    await bot.send_message(chat_id=int(ADMIN_ID), text=text, reply_markup=keyboard)
    await message.answer("⏳ Ma’lumotlaringiz adminga yuborildi. Tasdiqlanishini kuting.")
    await state.set_state(RegistrationStates.waiting_for_approval)


@router.callback_query(F.data.startswith("approve:"))
async def approve_user(callback: CallbackQuery, bot: Bot):
    user_telegram_id = int(callback.data.split(":")[1])

    # Ma’lumotni pending_approvals dan olamiz
    from bot.utils.pending_users import pending_approvals
    user_data = pending_approvals.get(user_telegram_id)

    if not user_data:
        await callback.message.edit_text("❌ Ma’lumotlar topilmadi yoki allaqachon tasdiqlangan.")
        return

    try:
        response = requests.post(f"{BACKEND_URL}/api/users/", json=user_data)
        if response.status_code == 201:
            await bot.send_message(user_telegram_id, "✅ Ro‘yxatdan o‘tish tasdiqlandi.", reply_markup=None)
            await callback.message.edit_text("✅ Tasdiqlandi va backendga yuborildi.")
        else:
            await bot.send_message(user_telegram_id, "❌ Ro‘yxatdan o‘tishda xatolik.")
            await callback.message.edit_text("⚠️ Xatolik: " + response.text[:500])
    except Exception as e:
        await bot.send_message(user_telegram_id, "⚠️ Server bilan bog‘lanib bo‘lmadi.")
        await callback.message.edit_text(f"❌ Ulanishda xatolik: {str(e)}")

    # Ma'lumotni tozalaymiz
    pending_approvals.pop(user_telegram_id, None)


@router.callback_query(F.data.startswith("reject:"))
async def reject_user(callback: CallbackQuery, bot: Bot):
    user_telegram_id = int(callback.data.split(":")[1])
    await bot.send_message(user_telegram_id, "❌ Ro‘yxatdan o‘tish rad etildi.")
    await callback.message.edit_text("🚫 Foydalanuvchi ro‘yxatdan o‘tkazilmadi.")
