from io import BytesIO

import folium
import requests
from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from datetime import datetime, date, timedelta
from bot.states.workflow import WorkStates
from bot.config import BACKEND_URL
import os
from tempfile import NamedTemporaryFile
from aiogram.types import FSInputFile

router = Router()


@router.message(Command("ishni_boshlash"))
async def handle_start_work_command(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    today = datetime.now().date()

    try:
        # Session mavjudligini tekshiramiz
        session_res = requests.get(f"{BACKEND_URL}/api/sessions/", params={
            "telegram_id": telegram_id,
            "date": str(today)
        })
        if session_res.status_code == 200 and session_res.json():
            await message.answer("⚠️ Siz bugungi ish sessiyasini allaqachon boshlagansiz.")
            return

        # Yangi sessiya yaratamiz
        new_session = {
            "telegram_id": telegram_id,
            "date": str(today),
            "is_started": True,
            "started_at": datetime.now().isoformat(),
            "is_finished": False
        }

        response = requests.post(f"{BACKEND_URL}/api/sessions/", json=new_session)

        if response.status_code == 201:
            await message.answer("📸 Iltimos, selfi (rasm) yuboring:")
            await state.set_state(WorkStates.waiting_for_selfie)
        else:
            await message.answer("❌ Sessiyani yaratishda xatolik yuz berdi.")

    except Exception as e:
        await message.answer(f"⚠️ Xatolik: {str(e)}")


@router.message(WorkStates.waiting_for_selfie, F.photo)
async def handle_selfie(message: Message, state: FSMContext, bot: Bot):
    telegram_id = message.from_user.id
    today = datetime.now().date()

    try:
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        file_path = file.file_path
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_path}"

        response = requests.get(file_url)
        img_bytes = BytesIO(response.content)

        # Sessionni topamiz
        session_res = requests.get(f"{BACKEND_URL}/api/sessions/", params={
            "telegram_id": telegram_id,
            "date": str(today)
        })
        session = session_res.json()[0]
        session_id = session["id"]

        # Faylni yuboramiz
        files = {
            "selfie": ("selfie.jpg", img_bytes, "image/jpeg")
        }
        patch_url = f"{BACKEND_URL}/api/sessions/{session_id}/"
        patch_response = requests.patch(patch_url, files=files)

        if patch_response.status_code == 200:
            await message.answer("📍 Endi iltimos, live location yuboring:")
            await state.set_state(WorkStates.waiting_for_location)
        else:
            await message.answer("❌ Selfi saqlashda xatolik yuz berdi.")

    except Exception as e:
        await message.answer(f"❌ Selfi yuborishda xatolik: {str(e)}")


@router.message(WorkStates.waiting_for_location, F.location)
async def handle_live_location(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    lat = message.location.latitude
    lon = message.location.longitude
    timestamp = datetime.now().isoformat()

    try:
        # Sessionni topamiz
        session_res = requests.get(f"{BACKEND_URL}/api/sessions/", params={
            "telegram_id": telegram_id,
            "date": str(date.today())
        })
        sessions = session_res.json()
        if not sessions:
            await message.answer("❌ Sessiya topilmadi.")
            return

        session_id = sessions[0]["id"]

        # Live locationni yuboramiz
        payload = {
            "session": session_id,
            "lat": lat,
            "lon": lon,
            "timestamp": timestamp
        }

        location_res = requests.post(f"{BACKEND_URL}/api/locations/", json=payload)

        if location_res.status_code == 201:
            await message.answer("✅ Joylashuv qabul qilindi. Bot sizni kuzatishda davom etadi.")
            await state.clear()
        else:
            await message.answer("⚠️ Joylashuvni saqlashda xatolik.")

    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")


@router.message(Command("ishni_yakunlash"))
async def handle_end_work(message: Message):
    telegram_id = message.from_user.id
    today = datetime.now().date()

    try:
        # 1. Foydalanuvchini topamiz (telegram_id orqali user_id olish)
        user_res = requests.get(f"{BACKEND_URL}/api/users/", params={"telegram_id": telegram_id})
        user_list = user_res.json()
        if not user_list:
            await message.answer("❌ Siz ro'yxatdan o'tmagansiz.")
            return

        user = user_list[0]
        user_id = user["id"]

        # 2. Sessionni topamiz (user_id va date orqali)
        session_res = requests.get(f"{BACKEND_URL}/api/sessions/", params={
            "user": user_id,
            "date": str(today)
        })
        sessions = session_res.json()
        if not sessions:
            await message.answer("❌ Bugungi sessiya topilmadi.")
            return

        session = sessions[0]
        session_id = session["id"]

        # 3. 8 soat ishlaganmi — tekshiramiz
        started_at_str = session["started_at"]
        if not started_at_str:
            await message.answer("❌ Ish boshlanish vaqti yo‘q.")
            return

        started_at = datetime.fromisoformat(started_at_str.replace("Z", ""))
        now = datetime.now()

        if now - started_at < timedelta(hours=8):
            remaining = timedelta(hours=8) - (now - started_at)
            hours, minutes = divmod(remaining.seconds // 60, 60)
            await message.answer(
                f"⏳ Hali {hours} soat {minutes} daqiqa ishladingiz.\n"
                f"8 soat to‘lishi kerak."
            )
            return

        # 4. Joylashuvlarni olamiz
        locations_res = requests.get(f"{BACKEND_URL}/api/locations/", params={"session": session_id})
        locations = locations_res.json()
        if not locations:
            await message.answer("⚠️ Joylashuvlar topilmadi, xarita chizilmadi.")
            return

        # 5. Folium xarita tuzamiz
        start_coords = (locations[0]["lat"], locations[0]["lon"])
        folium_map = folium.Map(location=start_coords, zoom_start=15)

        points = []
        for loc in locations:
            lat = loc["lat"]
            lon = loc["lon"]
            timestamp = loc["timestamp"]
            points.append((lat, lon))
            folium.Marker(location=(lat, lon), popup=timestamp).add_to(folium_map)

        folium.PolyLine(points, color="blue").add_to(folium_map)

        # 6. HTML faylga saqlaymiz
        with NamedTemporaryFile(delete=False, suffix=".html") as tmp:
            folium_map.save(tmp.name)
            tmp_path = tmp.name

        # 7. Backendga map faylni yuboramiz
        with open(tmp_path, "rb") as f:
            files = {"map_file": ("map.html", f, "text/html")}
            requests.patch(f"{BACKEND_URL}/api/sessions/{session_id}/", files=files)

        # 8. Sessiyani yopamiz
        patch_res2 = requests.patch(f"{BACKEND_URL}/api/sessions/{session_id}/", json={
            "is_finished": True,
            "finished_at": now.isoformat()
        })

        # 9. Userga xaritani yuboramiz
        if patch_res2.status_code == 200:
            file = FSInputFile(tmp_path, filename="xarita.html")
            await message.answer("✅ Ishingiz yakunlandi. Quyida harakatlar xaritasi:")
            await message.answer_document(file)
        else:
            await message.answer("⚠️ Sessiyani yopishda xatolik.")

        # 10. Faylni tozalaymiz
        os.remove(tmp_path)

    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")
