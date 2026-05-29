from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from strings import *
from config import ADMIN_ID
# Maǵlıwmatlar bazası funkciyaları
from database import (
    save_result, get_rating, get_test_key, set_test_key, 
    get_user_attempts, get_user_profile, get_all_results_for_export,
    toggle_test_status, is_test_active
)
from keyboards import get_admin_keyboard, get_student_keyboard
import time
import pandas as pd
import os

# --- EXCEL FORMATTA NATÍYJELERDI JÚKLEW ---
async def export_results(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    data = get_all_results_for_export()
    if not data:
        await message.answer("📊 Bazada házirshe maǵlıwmatlar joq.")
        return

    # Maǵlıwmatlardı shıraylı keste kórinisine keltiremiz
    df = pd.DataFrame(data, columns=['Oqıwshı Atı', 'Telegram ID', 'Test Kodi', 'Durıs juwaplar', 'Urınıs'])
    
    # Telegram ID baǵanasındaǵı sanlar ilmiy formatqa ótip ketpesi ushın tekst (str) halatına ótkeremiz
    df['Telegram ID'] = df['Telegram ID'].astype(str)
    
    file_name = "Natiyjeler_Export.xlsx"
    
    # Excel fayldı openpyxl arqalı shıraylı formatta jazamız
    with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Natiyjeler')
        
        # Hár bir baǵana keńligin ishindegi tekst uzınlıǵına qarap avtomat keńeytemiz
        worksheet = writer.sheets['Natiyjeler']
        for idx, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 3
            col_letter = chr(65 + idx)
            worksheet.column_dimensions[col_letter].width = max_len

    # Fayldı jiberemiz
    try:
        file = types.FSInputFile(file_name)
        await message.answer_document(file, caption="📊 *Barlıq test nátiyjeleri (Tolıq Excel kestesi)*", parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Fayl jiberiwde qátelik júz berdi: {e}")
    finally:
        # Jibergennen keyin server yaddan tazalaymiz
        if os.path.exists(file_name):
            os.remove(file_name)

# --- 1. ANTI-CHEAT SAZLAMASÍ (Sekundlarda) ---
COOLDOWN_TIME = 300  # 5 minuta sheklev
user_last_attempt = {}  # Paydalanıwshılar vaqtın saqlaw ushın lúgát

# --- 2. ADMIN (USTOZ) PANEL USHÍN HALATLAR (FSM) ---
class AdminStates(StatesGroup):
    waiting_for_test_code = State()
    waiting_for_test_key = State()
    waiting_for_close_code = State()  # Testti yaqunlaw ushın halat
    waiting_for_open_code = State()   # Testti qayta janlandırıw ushın halat

# --- 3. OQÍWSHÍLAR USHÍN HALATLAR (FSM) ---
class StudentStates(StatesGroup):
    waiting_for_test_code = State()
    waiting_for_student_answers = State()

# --- 4. /start BUYRÍǴÍ ---
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()  # Hár sapar start basılǵanda halattı tazalaymız
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "👨‍🏫 *Xosh kelipsiz, Ustaz!*\n\n"
            "Tómendegi túymeler arqalı botıńızdı basqarıń.", 
            parse_mode="Markdown",
            reply_markup=get_admin_keyboard()
        )
    else:
        await message.answer(
            MSG_START, 
            parse_mode="Markdown", 
            reply_markup=get_student_keyboard()
        )

# --- USTOZ USHÍN FSM STEP-BY-STEP TEST QOSÍW ---
async def start_set_key(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("📝 *Jańa test kodın kiritiń:* (Mısalı: `math10`)", parse_mode="Markdown")
    await state.set_state(AdminStates.waiting_for_test_code)

async def process_test_code(message: types.Message, state: FSMContext):
    test_code = message.text.strip().lower()
    await state.update_data(test_code=test_code)
    await message.answer(f"📦 *Test kodi qabıllandı:* `{test_code}`\n\n🎯 *Endi usı testtiń durıs juwapların (giltlerin) jiberiń:*", parse_mode="Markdown")
    await state.set_state(AdminStates.waiting_for_test_key)

async def process_test_key(message: types.Message, state: FSMContext):
    data = await state.get_data()
    test_code = data['test_code']
    correct_key = message.text.strip().lower()
    
    set_test_key(test_code, correct_key)  # Bazada saqlaymız
    toggle_test_status(test_code, 'active')  # Jańa test jaratılǵanda avtomat belsendi (active) boladı
    
    await message.answer(
        f"🚀 *Tayyar! Test tabıslı jaratıldı.*\n\n"
        f"📦 *Test kodi:* `{test_code}`\n"
        f"🔑 *Giltler uzınlıǵı:* `{len(correct_key)}` dana", 
        parse_mode="Markdown",
        reply_markup=get_admin_keyboard()
    )
    await state.clear()  # FSM procesin yaqunlaymız

# --- USTOZ USHÍN TESTTI MAJBURIY YAQUANLAW LOGIKASÍ ---
async def start_close_test(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("❌ *Toqtatpaqshı bolǵan test kodın kiritiń:*", parse_mode="Markdown")
    await state.set_state(AdminStates.waiting_for_close_code)

async def process_close_test_code(message: types.Message, state: FSMContext):
    test_code = message.text.strip().lower()
    correct_key = get_test_key(test_code)
    
    if not correct_key:
        await message.answer("⚠️ *Bunday test kodi tabılmadı!* Qaytadan kiritiń yamasa bıykarlaw ushın /start basıń.", parse_mode="Markdown")
        return
        
    toggle_test_status(test_code, 'inactive')  # Testti belsensizlendiremiz (jabamız)
    await message.answer(f"🛑 *Tabıslı tamamlandi!* `{test_code}` testi oqıwshılar ushın jabıldı.", parse_mode="Markdown", reply_markup=get_admin_keyboard())
    await state.clear()

# --- USTOZ USHÍN TESTTI QAYTA JANLANDÍRÍW (FAOLLASHTIRISH) ---
async def start_open_test(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("🔓 *Qayta jaqpaqshı bolǵan test kodın kiritiń:*", parse_mode="Markdown")
    await state.set_state(AdminStates.waiting_for_open_code)

async def process_open_test_code(message: types.Message, state: FSMContext):
    test_code = message.text.strip().lower()
    correct_key = get_test_key(test_code)
    
    if not correct_key:
        await message.answer("⚠️ *Bunday test kodi tabılmadı!* Qaytadan kiritiń yamasa /start basıń.", parse_mode="Markdown")
        return
        
    toggle_test_status(test_code, 'active')  # Testti qayta belsendi qılamız
    await message.answer(f"✅ *Tabıslı ashıldı!* `{test_code}` testi qayta janlandırıldı. Oqıwshılar testti tapsıra aladı.", parse_mode="Markdown", reply_markup=get_admin_keyboard())
    await state.clear()

# --- OQÍWSHÍ USHÍN FSM STEP-BY-STEP TEST TAPSÍRAW ---
async def start_student_test(message: types.Message, state: FSMContext):
    await message.answer("📝 *Test tapsırıw ushın Test kodın kiritiń:* (Mısalı: `math10`)", parse_mode="Markdown")
    await state.set_state(StudentStates.waiting_for_test_code)

async def process_student_test_code(message: types.Message, state: FSMContext):
    test_code = message.text.strip().lower()
    correct_key = get_test_key(test_code)
    
    if not correct_key:
        await message.answer("⚠️ *Bunday test kodi tabılmadı!* Qaytadan kiritiń yamasa toqtatıw ushın /start basıń.", parse_mode="Markdown")
        return
        
    # --- TEST BELSENDI EKANLIGIN TEKSERIW ---
    if not is_test_active(test_code):
        await message.answer("🛑 *Keshiresiz! Bul test ustaz tárepinen juwmaqlanǵan!* Jańa testlerdi kútiń.", parse_mode="Markdown")
        await state.clear()
        return
        
    await state.update_data(student_test_code=test_code)
    await message.answer(f"✅ *Test tabıldı!* `{test_code}`\n\n🎯 *Endi óz juwaplarıńızdı ketma-ket tekst kórinisinde jiberiń:* (Mısalı: `abcdabcd...`)", parse_mode="Markdown")
    await state.set_state(StudentStates.waiting_for_student_answers)

async def process_student_answers(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    student_answer = message.text.strip().lower()
    
    # Anti-Cheat sisteması
    current_time = time.time()
    if user_id in user_last_attempt:
        elapsed_time = current_time - user_last_attempt[user_id]
        if elapsed_time < COOLDOWN_TIME:
            remaining_time = int((COOLDOWN_TIME - elapsed_time) / 60)
            if remaining_time < 1:
                remaining_time = int(COOLDOWN_TIME - elapsed_time)
                await message.answer(f"⏳ *Anti-Cheat!* Kúte turıń. Keyingi urınıstı `{remaining_time}` sekundtan keyin jiberiw múmkin.", parse_mode="Markdown")
            else:
                await message.answer(f"⏳ *Anti-Cheat!* Kúte turıń. Keyingi urınıstı `{remaining_time}` minuttan keyin jiberiw múmkin.", parse_mode="Markdown")
            return

    data = await state.get_data()
    test_code = data['student_test_code']
    correct_key = get_test_key(test_code)

    # Sheklev vaqtın jańalaymız
    user_last_attempt[user_id] = current_time

    # Urınıslar
    current_attempts = get_user_attempts(user_id, test_code)
    new_attempt = current_attempts + 1
    
    # Tekseriw hám Tolıq qáteler tahlili
    correct_count = 0
    analysis_list = []
    
    for i in range(len(correct_key)):
        if i < len(student_answer):
            if student_answer[i] == correct_key[i]:
                correct_count += 1
                analysis_list.append(f"{i+1}:✅")
            else:
                analysis_list.append(f"{i+1}:❌")
        else:
            analysis_list.append(f"{i+1}:➖") # Oqıwshı juwap jazbay qaldırıp ketken bolsa
            
    wrong_count = len(correct_key) - correct_count
    score_percent = round((correct_count / len(correct_key)) * 100)
    
    # Nátiyjeni saqlaw
    save_result(user_id, full_name, test_code, correct_count, new_attempt)
    
    # Shıraylı kórinis ushın tahlil sızıǵın formatlaymız
    analysis_text = " | ".join(analysis_list)
    
    # Juwap qaytaramız
    response = MSG_RESULT.format(
        name=full_name,
        test_code=test_code,
        attempt=new_attempt,
        correct=correct_count,
        wrong=wrong_count,
        score=score_percent
    )
    
    # Tahlil blokın qosamız
    response += f"\n\n📊 *Qa'teler ústinde islew (Analiz):*\n`{analysis_text}`"
    
    await message.answer(response, parse_mode="Markdown", reply_markup=get_student_keyboard())
    await state.clear()

# --- 5. REYTINGDI KÓRIW ---
async def cmd_rating(message: types.Message):
    ratings = get_rating() # Bazadan uliwma dizimdi aladı
    
    if not ratings:
        await message.answer("📊 *Házirshe esh qanday nátiyje joq.*", parse_mode="Markdown")
        return
    
    text = f"{MSG_RATING_TITLE}\n"
    text += "━━━━━━━━━━━━━━━\n"
    for i, (name, total_score) in enumerate(ratings, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        text += f"{medal} *{name}* — `{total_score}` ball\n"
        
    await message.answer(text, parse_mode="Markdown")

# --- 6. PROFIL BÓLIMI ---
async def cmd_profile(message: types.Message):
    user_id = message.from_user.id
    stats, last_results = get_user_profile(user_id)
    
    # Aqırǵı 5 nátiyjeni tekst kórinisine keltiremiz
    results_text = ""
    if not last_results:
        results_text = "ℹ️ Házirshe nátiyjeler joq."
    else:
        for res in last_results:
            results_text += f"🔹 `{res[0]}`: {res[1]} ball ({res[2]}-m)\n"
            
    await message.answer(
        MSG_PROFILE.format(
            name=message.from_user.full_name,
            user_id=user_id,
            total_tests=stats[0],
            total_score=stats[1],
            last_results=results_text
        ),
        parse_mode="Markdown"
    )

# --- 7. XABARLARDÍ SARALAW HÁM JUWAPLARDÍ TEKSERIW ---
async def handle_answers(message: types.Message, state: FSMContext = None):
    user_id = message.from_user.id
    raw_text = message.text.strip()
    
    # --- TÚYME LOGIKALARÍ ---
    if raw_text == "🔑 Gilt kiritiw":
        if user_id == ADMIN_ID:
            await start_set_key(message, state)
        return

    if raw_text == "❌ Testti jabiw":
        if user_id == ADMIN_ID:
            await start_close_test(message, state)
        return

    if raw_text == "🔓 Testti aktivlestiriw":
        if user_id == ADMIN_ID:
            await start_open_test(message, state)
        return
    
    if raw_text == "📊 Reytingdi kóriw":
        await cmd_rating(message) 
        return
        
    if raw_text == "📝 Test tapsiriw":
        await start_student_test(message, state)
        return

    if raw_text == "👤 Profil":
        await cmd_profile(message)
        return

    if raw_text == "📥 Excel juklew":
        if user_id == ADMIN_ID:
            await export_results(message)
        return

    # --- ESKI FORMAT YAMASA ÁPIWAYÍ TEKSTLER ---
    if user_id == ADMIN_ID and "*" in raw_text:
        await message.answer("👨‍🏫 *Ustaz, test qosıw ushın* `🔑 gilt kiritiw` *túymesinen paydalanıń.*", parse_mode="Markdown")
        return

    # Oqıwshı eski formatta (kod*juwap) jiberiwge urınsa eskertemiz
    if "*" in raw_text and user_id != ADMIN_ID:
        await message.answer("⚠️ *Format ózgerdi!* Iltimas, aldin `📝 Test tapsiriw` túymesin basıń.", parse_mode="Markdown")
        return