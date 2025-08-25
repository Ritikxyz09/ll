import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from database import init_db, generate_otp, verify_otp, add_user, search_phone

# Apna API Token yahan dalen - @BotFather se milega
API_TOKEN = "8105791394:AAG4PPggphTHzoI8HpWZvoy2sl_Qw_DYtVU"

# Database initialize karen
init_db()

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# User states track karne ke liye
user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    keyboard = [[KeyboardButton("📞 Share My Number", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        "🔍 **Verified Phone Directory Bot**\n\n"
        "📞 Apna number share karein → OTP verification → Database mein add hoga\n"
        "🔎 Fir kisi verified number ko search kar sakte hain\n\n"
        "Note: Sirf OTP verified numbers hi searchable honge",
        reply_markup=reply_markup
    )

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Contact share hone par handle kare"""
    if update.message.contact:
        contact = update.message.contact
        user_id = contact.user_id
        phone = contact.phone_number
        name = contact.first_name or "User"
        
        # Database mein add karo (unverified)
        add_user(user_id, phone, name)
        
        # OTP generate karo
        otp_code = generate_otp(phone)
        
        # User state set karo
        user_states[user_id] = {"phone": phone, "step": "verify_otp", "otp": otp_code}
        
        # OTP user ko bhejo (SMS ki jagah bot hi bhejega)
        await update.message.reply_text(
            f"✅ Number received: {phone}\n\n"
            f"🔐 Your OTP for verification is: \n\n"
            f"📩 **{otp_code}**\n\n"
            f"Please enter this 6-digit OTP to verify your number:"
        )
    else:
        await update.message.reply_text("❌ Please share contact using the button")

async def handle_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """OTP enter karne par handle kare"""
    user_id = update.effective_user.id
    otp_code = update.message.text.strip()
    
    if user_id not in user_states or user_states[user_id]["step"] != "verify_otp":
        await update.message.reply_text("❌ Please share your number first using /start")
        return
    
    if len(otp_code) != 6 or not otp_code.isdigit():
        await update.message.reply_text("❌ Invalid OTP. Please enter 6 digits.")
        return
    
    phone = user_states[user_id]["phone"]
    correct_otp = user_states[user_id]["otp"]
    
    if otp_code == correct_otp:
        # OTP verified
        verify_otp(phone, otp_code)  # Database update
        user_states[user_id]["step"] = "verified"
        
        await update.message.reply_text(
            f"🎉 Verification Successful!\n\n"
            f"✅ Your number {phone} has been verified.\n"
            f"🔍 Now you can search numbers: /search\n\n"
            f"📖 Help: /help"
        )
    else:
        await update.message.reply_text(
            "❌ Invalid OTP. Please try again or request new OTP: /start"
        )

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search command handler"""
    await update.message.reply_text(
        "🔍 Enter phone number to search (with country code):\n"
        "Example: +919876543210\n\n"
        "Note: Sirf verified numbers hi dikhenge"
    )

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search query handle kare"""
    phone = update.message.text.strip()
    
    if not phone.startswith('+'):
        await update.message.reply_text("❌ Please enter valid phone number with country code (+91...)")
        return
    
    result = search_phone(phone)
    
    if result:
        await update.message.reply_text(f"✅ Number: {phone}\n📛 Name: {result}")
    else:
        await update.message.reply_text(
            f"❌ {phone} not found in verified database.\n"
            f"Possible reasons:\n"
            f"• Number doesn't exist\n"
            f"• Number not verified yet\n"
            f"• User didn't consent to share"
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler"""
    await update.message.reply_text(
        "🤖 **Bot Help Guide**\n\n"
        "📞 /start - Share your number and get verified\n"
        "🔍 /search - Search a verified number\n"
        "❓ /help - Show this help message\n\n"
        "📝 **How it works:**\n"
        "1. Share your number → Get OTP\n"
        "2. Enter OTP → Get verified\n"
        "3. Search numbers → Only verified numbers shown"
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Status check command"""
    user_id = update.effective_user.id
    if user_id in user_states:
        status = user_states[user_id]
        await update.message.reply_text(
            f"📊 Your Status:\n"
            f"Phone: {status['phone']}\n"
            f"Verified: {'✅ Yes' if status.get('step') == 'verified' else '❌ No'}"
        )
    else:
        await update.message.reply_text("❌ Please start with /start first")

def main():
    """Main function"""
    application = Application.builder().token(API_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_otp))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search))
    
    print("🤖 OTP Verification Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
