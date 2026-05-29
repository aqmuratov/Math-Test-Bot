import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiohttp import web

from database import init_db

# Handlers faylından barlıq kerekli funkciyalardı hám halatlardı import qılamız
from handlers import (
    cmd_start, cmd_rating, handle_answers, cmd_profile, export_results,
    AdminStates, process_test_code, process_test_key, process_close_test_code, process_open_test_code,
    StudentStates, process_student_test_code, process_student_answers
)

# Render uchun oddiy veb-server funksiyasi (Botni "uyg'oq" saqlaydi)
async def handle(request):
    return web.Response(text="Bot is running!")

async def main():
    # 1. Loglardı jaǵamız
    logging.basicConfig(level=logging.INFO)

    # 2. Maǵlıwmatlar bazasın jaratamız
    init_db()

    # 3. Bot hám Dispatcher obyektlerin alamız
    # Eslatma: Render'dagi "Environment Variables" ga BOT_TOKEN qo'shgan bo'lsangiz, 
    # os.getenv("BOT_TOKEN") dan foydalanish xavfsizroq.
    bot = Bot(token=os.getenv("BOT_TOKEN", API_TOKEN))
    dp = Dispatcher()

    # 4. Handlerlerdi dizimnen ótkeremiz
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(export_results, F.text == "📥 Excel yuklew")
    
    # --- ADMIN HANDLERLAR ---
    dp.message.register(process_test_code, AdminStates.waiting_for_test_code)
    dp.message.register(process_test_key, AdminStates.waiting_for_test_key)
    dp.message.register(process_close_test_code, AdminStates.waiting_for_close_code)
    dp.message.register(process_open_test_code, AdminStates.waiting_for_open_code)
    
    # --- OQÍWSHÍ HANDLERLAR ---
    dp.message.register(process_student_test_code, StudentStates.waiting_for_test_code)
    dp.message.register(process_student_answers, StudentStates.waiting_for_student_answers)
    
    dp.message.register(cmd_rating, Command("rating"))
    dp.message.register(cmd_rating, F.text == "📊 Reytingdi kóriw")
    
    dp.message.register(cmd_profile, Command("profile"))
    dp.message.register(cmd_profile, F.text == "👤 Profil")
    
    dp.message.register(handle_answers, F.text)

    # --- Render uchun Web Serverni ishga tushiramiz ---
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 8080)))
    await site.start()

    # 5. Bottı iske túsiremiz
    print("Bot tabisli iske tusti...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
