import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from config import API_TOKEN
from database import init_db

# Handlers faylından barlıq kerekli funkciyalardı hám halatlardı import qılamız
from handlers import (
    cmd_start, cmd_rating, handle_answers, cmd_profile, export_results,
    AdminStates, process_test_code, process_test_key, process_close_test_code, process_open_test_code,  # Ustoz funkciyaları (Yaqınlaw hám Janlandırıw)
    StudentStates, process_student_test_code, process_student_answers
)

async def main():
    # 1. Loglardı jaǵamız
    logging.basicConfig(level=logging.INFO)

    # 2. Maǵlıwmatlar bazasın jaratamız
    init_db()

    # 3. Bot hám Dispatcher obyektlerin alamız
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    # 4. Handlerlerdi (buyrıqlardı hám túymelerdi) dizimnen ótkeremiz
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(export_results, F.text == "📥 Excel yuklew")
    
    # --- ADMIN (USTOZ) FSM HANDLERLARIN DIZIMNEN ÓTKERIW ---
    dp.message.register(process_test_code, AdminStates.waiting_for_test_code)
    dp.message.register(process_test_key, AdminStates.waiting_for_test_key)
    dp.message.register(process_close_test_code, AdminStates.waiting_for_close_code)  # Testti yaqunlaw handleri
    dp.message.register(process_open_test_code, AdminStates.waiting_for_open_code)    # Testti qayta janlandırıw handleri
    
    # --- OQÍWSHÍ (STUDENT) FSM HANDLERLARIN DIZIMNEN ÓTKERIW ---
    # Bul handlerlar da uliwma tekst tekseriwshiden (handle_answers) joqarıda turıwı shart!
    dp.message.register(process_student_test_code, StudentStates.waiting_for_test_code)
    dp.message.register(process_student_answers, StudentStates.waiting_for_student_answers)
    
    # Reyting: buyrıq hám túyme ushın
    dp.message.register(cmd_rating, Command("rating"))
    dp.message.register(cmd_rating, F.text == "📊 Reytingdi kóriw")
    
    # Profil: buyrıq hám túyme ushın
    dp.message.register(cmd_profile, Command("profile"))
    dp.message.register(cmd_profile, F.text == "👤 Profil")
    
    # Oqıwshınıń hár qanday ápiwayı tekstli xabarın tekseriwge jiberemiz
    # Diqqat: Bul hár dayım eń tómende turıwı shart!
    dp.message.register(handle_answers, F.text)

    # 5. Bottı iske túsiremiz
    print("Bot tabisli iske tusti...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())