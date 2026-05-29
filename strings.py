# strings.py

MSG_START = (
    "👋 *Assalawma áleykum! Test botqa xosh kelipsiz.*\n\n"
    "📝 **Test tapsırıw ushın:**\n"
    "Tómendegi `kod*juwaplar` formatında jiberiń:\n"
    "Mısalı: `math10*abcd...`\n\n"
    "📊 **Reytingdi kóriw:**\n"
    "`/rating kod` buyrıǵın jiberiń.\n\n"
    "👤 **Profil:**\n"
    "Óz nátiyjelerińizdi kóriw ushın túymeni basıń."
)

MSG_RESULT = (
    "📋 *TEST NÁTIYJESI*\n"
    "━━━━━━━━━━━━━━━\n"
    "👤 *Oqıwshı:* {name}\n"
    "🔑 *Test kodi:* `{test_code}`\n"
    "🔢 *Urinis:* `{attempt}-marte`\n"
    "✅ *Durıs juwaplar:* {correct}\n"
    "❌ *Qáte juwaplar:* {wrong}\n"
    "━━━━━━━━━━━━━━━\n"
    "📊 *Ulıwma ball:* `{score}%`"
)

# Profil bo'limi uchun estetik matn
MSG_PROFILE = (
    "👤 *SIZDIŃ PROFILIŃIZ*\n"
    "━━━━━━━━━━━━━━━\n"
    "👨‍🎓 *Atı:* {name}\n"
    "🆔 *ID:* `{user_id}`\n"
    "📝 *Jámi testler:* `{total_tests}`\n"
    "🏆 *Jámi ball:* `{total_score}`\n"
    "━━━━━━━━━━━━━━━\n"
    "🕒 *Sońǵı 5 nátiyje:*\n"
    "{last_results}"
)

MSG_TEST_NOT_FOUND = "⚠️ *Bunday kodlı test tabılmadı!* Iltimas, kodtı durıs kiritiń."

MSG_RATING_TITLE = "🏆 *ULIWMALIQ REYTING KESTESI (TOP OQIWSHILAR)*"

MSG_INPUT_TEST_CODE = "📝 *Test tapsırıw ushın kod hám juwaplardı jiberiń.*\n\nMısalı: `math10*abcd`"