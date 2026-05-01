import os
import logging
import threading
import requests  # برای دریافت اخبار فارکس
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# تنظیمات توکن و لاگ
TOKEN = '8671698456:AAFLp4i0BEgFDj9YDLNEH5qk9KRaljkbQbM'
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- بخش اول: بیدار نگه داشتن سرور ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# --- بخش دوم: دریافت اخبار فارکس فاکتوری ---
async def get_forex_news():
    try:
        url = "https://faireconomy.media"
        response = requests.get(url, timeout=10)
        events = response.json()
        
        msg = "📅 **تقویم اقتصادی (اخبار مهم قرمز):**\n\n"
        count = 0
        for ev in events:
            if ev['impact'] == 'High':
                msg += f"🔴 **{ev['title']}**\n🏳️ ارز: {ev['country']}\n⏰ زمان: {ev['date']}\n\n"
                count += 1
            if count >= 10: break
        return msg if count > 0 else "امروز خبر مهمی در تقویم نیست."
    except Exception as e:
        logging.error(f"Forex Error: {e}")
        return "❌ خطا در دریافت اطلاعات از فارکس فاکتوری."

# --- بخش سوم: مدیریت دستورات و دکمه‌ها ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 اخبار مهم فارکس", callback_data='forex')],
        [InlineKeyboardButton("🛠 لیست خدمات", callback_data='services')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! خوش آمدید. یک گزینه را انتخاب کنید:", reply_markup=reply_markup)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'forex':
        await query.edit_message_text(text="⏳ در حال دریافت اخبار...")
        news = await get_forex_news()
        await query.edit_message_text(text=news, parse_mode='Markdown')
    elif query.data == 'services':
        await query.edit_message_text(text="✅ خدمات ما شامل اطلاع‌رسانی ۲۴ ساعته فارکس است.")

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id
    if "سلام" in text:
        await context.bot.send_message(chat_id=chat_id, text="سلام! ربات شما ۲۴ ساعته فعال است. چطور می‌توانم کمکتان کنم؟")
    elif "قیمت" in text:
        await context.bot.send_message(chat_id=chat_id, text="لیست خدمات و قیمت‌ها به زودی برای شما ارسال می‌شود.")
    else:
        await context.bot.send_message(chat_id=chat_id, text="پیام شما دریافت شد: " + text)

# --- بخش چهارم: اجرای اصلی ---
if __name__ == '__main__':
    threading.Thread(target=run_health_check, daemon=True).start()
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_buttons))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_messages))
    
    print("ربات با موفقیت روشن شد...")
    application.run_polling()


