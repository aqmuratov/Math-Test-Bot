from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# 1. Admin (Ustoz) ushín túymeler
def get_admin_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔑 Gilt kiritiw"), KeyboardButton(text="📥 Excel juklew")],
            [KeyboardButton(text="🔓 Testti aktivlestiriw"), KeyboardButton(text="❌ Testti jabiw")], # Testti basqarıw túymeleri
            [KeyboardButton(text="📊 Reytingdi kóriw")] # Maǵlıwmatlar túymesi
        ],
        resize_keyboard=True, # Túymelerdi ekranǵa maslap shıraylı kishireytedi
        input_field_placeholder="Ustaz, menudan birin saylań..."
    )
    return keyboard

# 2. Oqıwshı (Student) ushín túymeler
def get_student_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Test tapsiriw")], # Tiykarǵı háreket túymesi (bólek úlken qatarda)
            [KeyboardButton(text="📊 Reytingdi kóriw"), KeyboardButton(text="👤 Profil")] # Qosımsha túymeler (yonma-yon)
        ],
        resize_keyboard=True,
        input_field_placeholder="Tómendegi menudan birin saylań..."
    )
    return keyboard