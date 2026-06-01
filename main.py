import os
import arxiv
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# إعدادات الذكاء الاصطناعي
genai.configure(api_key=os.environ.get("GEMINI_KEY"))
model = genai.GenerativeModel('gemini-pro')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔭 أهلاً بك في 'مرصد'!\n\n"
        "أنا مساعدك العلمي الشخصي. اسألني عن أي موضوع (مثل: 'حدثني عن الثقوب السوداء' أو 'أحدث أبحاث الجينات') "
        "وسأقوم بـ:\n"
        "1. البحث في أرشيف العلوم (arXiv).\n"
        "2. تلخيص أهم النتائج لك.\n"
        "3. تزويدك بالروابط المباشرة."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    status_msg = await update.message.reply_text("🤔 جاري التفكير والبحث في أمهات الكتب العلمية...")
    
    try:
        # استخدام Gemini لتحويل طلب المستخدم إلى "استعلام بحث" دقيق جداً
        prompt = f"حول هذا الطلب إلى كلمات مفتاحية بحثية علمية بالإنجليزية فقط: '{user_text}'"
        analysis = model.generate_content(prompt)
        query = analysis.text.strip()
        
        search = arxiv.Search(query=query, max_results=3, sort_by=arxiv.SortCriterion.SubmittedDate)
        
        results = list(search.results())
        
        if not results:
            await context.bot.edit_message_text(chat_id=update.message.chat_id, message_id=status_msg.message_id, 
                                                text="لم أجد نتائج دقيقة. هل يمكنك محاولة صياغة سؤالك بطريقة أخرى؟")
            return

        # إرسال النتائج بشكل تفاعلي
        await context.bot.edit_message_text(chat_id=update.message.chat_id, message_id=status_msg.message_id, 
                                            text=f"✅ وجدت لك أحدث 3 أبحاث حول: *{query}*")
        
        for result in results:
            summary = model.generate_content(f"لخص لي هذا البحث في جملتين بسيطتين: {result.summary[:500]}").text
            await update.message.reply_text(f"📄 *{result.title}*\n\n📝 *الملخص:* {summary}\n\n🔗 {result.pdf_url}")
            
    except Exception as e:
        await context.bot.edit_message_text(chat_id=update.message.chat_id, message_id=status_msg.message_id, 
                                            text="حدث خطأ في النظام. أنا هنا، جرب إرسال موضوع آخر!")

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.environ.get("TELEGRAM_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
