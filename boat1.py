from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
from flask import Flask
from threading import Thread

# Coordinator Schedule
coordinator_schedule = {
    "Monday": {"4-5": "Mansi", "5-6": "Anany", "6-7": "Amish"},
    "Tuesday": {"4-5": "Rohit", "5-6": "Mansi", "6-7": "Mansi"},
    "Wednesday": {"4-5": "Mansi", "5-6": "Amish", "6-7": "Anany"},
    "Thursday": {"4-5": "Amish", "5-6": "Rohit", "6-7": "Mansi"},
    "Friday": {"4-5": "Anany", "5-6": "Amish", "6-7": "Rohit"},
    "Saturday": {"4-5": "Amish", "5-6": "Anany", "6-7": "Rohit"},
}

# Secretary Schedule
secretary_schedule = {
    "Monday": {"4-5": "Nil", "5-6": "Nil", "6-7": "Shilpa"},
    "Tuesday": {"4-5": "Nil", "5-6": "Abhay", "6-7": "Abhay"},
    "Wednesday": {"4-5": "Nil", "5-6": "Nil", "6-7": "Nil"},
    "Thursday": {"4-5": "Shital", "5-6": "Nil", "6-7": "Ankit"},
    "Friday": {"4-5": "Shital", "5-6": "Shilpa", "6-7": "Shilpa"},
    "Saturday": {"4-5": "Shital", "5-6": "Ankit", "6-7": "Abhay"},
}

# Start Command
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [[InlineKeyboardButton(day, callback_data=day)] for day in coordinator_schedule.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Choose a day:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("Choose a day:", reply_markup=reply_markup)

# Handle Day Selection
async def day_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    context.user_data['selected_day'] = query.data

    keyboard = [[InlineKeyboardButton(slot, callback_data=slot)] for slot in coordinator_schedule[query.data].keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=f"📅 Selected Day: {query.data}\nChoose a slot:", reply_markup=reply_markup)

# Handle Slot Selection
async def slot_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    selected_day = context.user_data.get('selected_day')
    selected_slot = query.data
    await query.answer()

    coordinator_name = coordinator_schedule[selected_day][selected_slot]
    secretary_name = secretary_schedule[selected_day][selected_slot]

    await query.edit_message_text(
        text=f"📅 Selected Day: {selected_day}\n🕒 Selected Slot: {selected_slot}\n"
             f"👨‍💼 **Coordinator:** {coordinator_name}\n🧑‍💼 **Secretary:** {secretary_name}"
    )

    # Restart Process: Send a new message to start over
    keyboard = [[InlineKeyboardButton(day, callback_data=day)] for day in coordinator_schedule.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text("Choose a day:", reply_markup=reply_markup)

# Flask Server for Keep Alive
def run_flask():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return "Bot is running!"

    app.run(host="0.0.0.0", port=8080)

# Main Bot Function
def main():
    TOKEN = "8083465248:AAH0-s1KjpJXvsJ8T3t8AXxCcYR02HdaX24"  # Replace with your actual Telegram bot token
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(day_selection, pattern="^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)$"))
    app.add_handler(CallbackQueryHandler(slot_selection, pattern="^(4-5|5-6|6-7)$"))

    app.run_polling()

if __name__ == '__main__':
    # Run Flask server in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Run the Telegram bot
    main()
