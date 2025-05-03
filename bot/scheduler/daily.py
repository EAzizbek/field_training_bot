# # import os
# #
# # import aiocron
# # from datetime import datetime, date
# # import requests
# # from bot.config import BACKEND_URL
# # from bot.config import ADMIN_ID  # kerak bo‘lsa log uchun
# # from aiogram import Bot
# # from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# # @aiocron.crontab('*/15 * * * * *', tz='Asia/Tashkent')
# # async def send_start_work_button():
# #     print('daily')
#
#
# import asyncio
# import aiocron
# from datetime import datetime
# import pytz
#
# # Define your cron job - runs every 15 seconds
# @aiocron.crontab('*/15 * * * * *', start=True)  # Added start=True
# async def send_start_work_button():
#     now = datetime.now(pytz.timezone("Asia/Tashkent"))
#     print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Task executed")
#
# # Keep the event loop alive
# async def main():
#     print("Running cron job every 15 seconds...")
#     # We don't need to do anything special here, just keep the loop running
#     while True:
#         await asyncio.sleep(60)  # Check every minute is enough
#
# if __name__ == '__main__':
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print("Script stopped by user")
# #     try:
# #         # Backenddan barcha foydalanuvchilarni olib chiqamiz
# #         res = requests.get(f"{BACKEND_URL}/api/users/")
# #         users = res.json()
# #
# #         for user in users:
# #             telegram_id = user["telegram_id"]
# #             user_id = user["id"]
# #
# #             # Bugungi sessiya mavjudligini tekshiramiz
# #             session_check = requests.get(
# #                 f"{BACKEND_URL}/api/sessions/",
# #                 params={"user": user_id, "date": str(datetime.now().date())}
# #             )
# #
# #             if session_check.status_code == 200 and session_check.json():
# #                 print(f"⏩ Session already exists for {telegram_id}")
# #                 continue
# #
# #             # Sessiya yaratamiz
# #             session = {
# #                 "user": user_id,
# #                 "date": str(datetime.now().date()),
# #                 "is_started": False,
# #                 "is_finished": False
# #             }
# #
# #             requests.post(f"{BACKEND_URL}/api/sessions/", json=session)
# #
# #             # Ishni boshlash tugmasi uchun inline keyboard
# #             keyboard = InlineKeyboardMarkup(
# #                 inline_keyboard=[
# #                     [InlineKeyboardButton(text="🚀 Ishni boshlash", callback_data="start_work")]
# #                 ]
# #             )
# #
# #             # Hozirgi soatni tekshiramiz
# #             current_time = datetime.now().hour
# #
# #             # Soatga qarab matnni o‘zgartiramiz
# #             if 8 <= current_time < 24:
# #                 text = "📅 Bugungi ish kunini boshlash uchun tugmani bosing:"
# #             else:
# #                 text = "⏹ Ish vaqti emas. Iltimos, ertaga soat 8:00 da bosing."
# #
# #             bot = Bot(token=os.getenv("BOT_TOKEN"))
# #             await bot.send_message(
# #                 chat_id= 1716549072,
# #                 text=text,
# #                 reply_markup=keyboard
# #             )
# #
# #     except Exception as e:
# #         print(f"❌ Error sending 'Start Work' button: {e}")
# #
# #
# # @aiocron.crontab('0 0 * * *', tz='Asia/Tashkent')
# # async def auto_finish_uncompleted_sessions():
# #     print("🕛 00:00 - Auto-finishing uncompleted sessions...")
# #
# #     try:
# #         # Django'dan barcha sessionlarni olamiz
# #         res = requests.get(f"{BACKEND_URL}/api/sessions/")
# #         all_sessions = res.json()
# #
# #         from aiogram import Bot
# #
# #         for session in all_sessions:
# #             if session["is_started"] and not session["is_finished"]:
# #                 session_id = session["id"]
# #                 telegram_id = None
# #                 finished_time = datetime.now().isoformat()
# #
# #                 # Foydalanuvchi haqida ma’lumot
# #                 user_id = session["user"]
# #                 user_res = requests.get(f"{BACKEND_URL}/api/users/{user_id}/")
# #                 if user_res.status_code == 200:
# #                     user = user_res.json()
# #                     telegram_id = user["telegram_id"]
# #
# #                 # PATCH orqali yangilaymiz
# #                 patch_url = f"{BACKEND_URL}/api/sessions/{session_id}/"
# #                 patch_payload = {
# #                     "is_finished": True,
# #                     "finished_at": finished_time
# #                 }
# #                 requests.patch(patch_url, json=patch_payload)
# #
# #                 # Foydalanuvchiga habar yuboramiz
# #                 if telegram_id:
# #                     bot = Bot(token=os.getenv("BOT_TOKEN"))
# #                     await bot.send_message(
# #                         chat_id=telegram_id,
# #                         text="⏹ Sizning ish kuningiz avtomatik tarzda yakunlandi (00:00)."
# #                     )
# #     except Exception as e:
# #         print(f"❌ Auto-finish error: {e}")
# #
# # print("✅ daily.py import bo‘ldi!")
