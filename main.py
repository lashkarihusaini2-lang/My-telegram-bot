import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# توکن خود را دقیقاً بین دو کوتیشن بگذارید
TOKEN = '8671698456:AAFH9YYpxR6eBuvJPjIvCGVXKFSbinZjcjI'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# بخش بیدار نگه داشتن سرور (Port 8080)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# بخش پاسخ به کلمات خاص
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id

    if "سلام" in text:
        await context.bot.send_message(chat_id=chat_id, text="سلام! ربات شما ۲۴ ساعته فعال است. چطور می‌توانم کمکتان کنم؟")
    elif "قیمت" in text:
        await context.bot.send_message(chat_id=chat_id, text="لیست خدمات و قیمت‌ها به زودی برای شما ارسال می‌شود.")
    else:
        await context.bot.send_message(chat_id=chat_id, text="پیام شما دریافت شد: " + text)

if __name__ == '__main__':
    # اجرای سیستم ضد-خاموشی در پس‌زمینه
    threading.Thread(target=run_health_check, daemon=True).start()
    
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_messages))
    
    application.run_polling()

