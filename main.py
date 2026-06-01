import os
import arxiv
import google.generativeai as genai
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

genai.configure(api_key=os.environ.get("GEMINI_KEY"))
model = genai.GenerativeModel('gemini-pro')

async def start(update, context):
    await update.message.reply_text("🔭 أهلاً بك في 'مرصد'. أنا جاهز لاستكشاف الأبحاث العلمية لك.")

async def handle_message(update, context):
    user_text = update.message.text
    await update.message.reply_text("🔍 جاري البحث في أرشيف العلوم...")
    analysis = model.generate_content(f"استخرج موضوع بحثي دقيق من: {user_text}")
    search = arxiv.Search(query=analysis.text, max_results=2)
    for result in search.results():
        await update.message.reply_text(f"📄 *{result.title}*\n🔗 {result.pdf_url}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.environ.get("TELEGRAM_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
