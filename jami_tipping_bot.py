from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, InlineQueryHandler, CommandHandler, MessageHandler, ConversationHandler, filters
from collections import defaultdict
import re

# Store the API token for your bot
API_TOKEN = '7586332229:AAGQmjlMfUQEOeLIAnF_-sh1nuzLp3NH-FI'

# Initialize the Application with your bot's API token
application = Application.builder().token(API_TOKEN).build()

# Define conversation states
JAMIBIO, BUTTON_TEXT = range(2)

# Dictionary to store channel settings (Jami.bio link and button text)
channel_settings = {}

# Dictionary to store click count for each channel
clicks = defaultdict(int)

# Function to validate Jami.bio link format
def is_valid_jami_bio_link(link):
    jami_bio_regex = r"^https://jami\.bio/[a-zA-Z0-9_-]+$"
    return re.match(jami_bio_regex, link) is not None

# Start command: Welcome message
async def start(update, context):
    await update.message.reply_text("Welcome to the Jami Tipping Bot! Let's get started by providing your Jami.bio link.")
    return JAMIBIO

# Handle Jami.bio link input
async def jami_bio(update, context):
    user_input = update.message.text
    
    # Check if the Jami.bio link is valid
    if not is_valid_jami_bio_link(user_input):
        await update.message.reply_text(
            "The link you provided doesn't seem to be a valid Jami.bio link. Please ensure it's in the format: https://jami.bio/username.\n\nIf you don't have a Jami account, you can create one here: https://jami.bio/create"
        )
        return JAMIBIO  # Keep asking until the admin provides a valid link
    
    # Store the Jami.bio link in the channel settings
    channel_settings[update.message.chat.id] = {"jami_bio": user_input}
    await update.message.reply_text("Great! Now, please provide the button text (e.g., 'Leave Tip'). If you want to keep the default, just type 'Leave Tip'.")
    return BUTTON_TEXT

# Handle button text input
async def button_text(update, context):
    button_text = update.message.text.strip()
    
    # If the user doesn't provide custom text, default to "Leave Tip"
    if not button_text:
        button_text = "Leave Tip"
    
    # Store the button text in the channel settings
    channel_settings[update.message.chat.id]["button_text"] = button_text
    await update.message.reply_text(f"Setup complete! Your button will say '{button_text}' and will link to {channel_settings[update.message.chat.id]['jami_bio']}.")
    return ConversationHandler.END

# Track button clicks
def track_button_click(channel_id):
    clicks[channel_id] += 1

# Inline Query Handler: Display customized button with dynamic text and link
async def inlinequery(update, context):
    query = update.inline_query.query
    results = []
    
    # Retrieve the custom settings for the channel
    channel_id = update.inline_query.chat.id
    jami_bio = channel_settings.get(channel_id, {}).get("jami_bio", "https://jami.bio/yourprofile")
    button_text = channel_settings.get(channel_id, {}).get("button_text", "Leave Tip")
    
    # Create the button with dynamic text and link
    button = InlineKeyboardButton(button_text, url=jami_bio)
    keyboard = InlineKeyboardMarkup([[button]])
    
    # Track the button click
    track_button_click(channel_id)
    
    # Prepare the result to send back
    results.append(
        InlineQueryResultArticle(
            id="1", 
            title=button_text, 
            input_message_content=InputTextMessageContent("Click below to leave a tip!"), 
            reply_markup=keyboard
        )
    )
    
    await update.inline_query.answer(results)

# Command to view analytics (number of button clicks)
async def analytics(update, context):
    channel_id = update.message.chat.id
    click_count = clicks.get(channel_id, 0)
    await update.message.reply_text(f"The number of clicks for your 'Leave Tip' button is: {click_count}")

# Main function to handle the bot and start the conversation handler
def main():
    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            JAMIBIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, jami_bio)],
            BUTTON_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, button_text)],
        },
        fallbacks=[],
    )
    
    # Add handler for conversation and other commands
    application.add_handler(conv_handler)
    application.add_handler(InlineQueryHandler(inlinequery))
    application.add_handler(CommandHandler('analytics', analytics))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
