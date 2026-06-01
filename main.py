import os
import arxiv
import google.generativeai as genai
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# تفعيل الـ Logging لمتابعة عمل البوت في الـ Logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# إعدادات Gemini
genai.configure(api_key=os.environ.get("GEMINI_KEY"))
model = genai.GenerativeModel('gemini-pro')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔭 أهلاً بك في 'مرصد'! أنا جاهز لاستكشاف الأبحاث العلمية. اكتب لي موضوع البحث وسأحضر لك النتائج.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    status_msg = await update.message.reply_text("🔍 جاري البحث والتحليل...")
    
    try:
        # تحويل طلب المستخدم لإنجليزية للبحث الدقيق
        analysis = model.generate_content(f"حول هذا الموضوع العلمي إلى استعلام بحث بالإنجليزية: {user_text}")
        query = analysis.text.strip()
        
        search = arxiv.Search(query=query, max_results=2, sort_by=arxiv.SortCriterion.SubmittedDate)
        results = list(search.results())
        
        if not results:
            await context.bot.edit_message_text(chat_id=update.message.chat_id, message_id=status_msg.message_id, text="عذراً، لم أجد أبحاثاً حديثة بهذا المسمى.")
            return

        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=status_msg.message_id)
        
        for result in results:
            # تلخيص ذكي
            summary = model.generate_content(f"لخص هذا البحث في جملة واحدة: {result.summary[:300]}").text
            await update.message.reply_text(f"📄 *{result.title}*\n\n📝 *ملخص:* {summary}\n\n🔗 {result.pdf_url}")
            
    except Exception as e:
        logging.error(f"Error: {e}")
        await context.bot.edit_message_text(chat_id=update.message.chat_id, message_id=status_msg.message_id, text="حدث خطأ تقني، سأحاول مجدداً لاحقاً.")

if __name__ == '__main__':
    # البوت يبدأ الآن مع خاصية drop_pending_updates لمنع أي Conflict
    app = ApplicationBuilder().token(os.environ.get("TELEGRAM_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("🚀 مرصد يعمل الآن...")
    app.run_polling(drop_pending_updates=True)
