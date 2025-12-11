import os
from dotenv import load_dotenv

load_dotenv()

# Bot Information
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
VERSION = os.getenv("VERSION")

# API Information
BLOXLINK_API_KEY = os.getenv("BLOXLINK_API_KEY")

# Firebase Information
FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")
FIREBASE_SECRET = os.getenv("FIREBASE_SECRET")

# Server Information
GUILD_ID = os.getenv("GUILD_ID")
PERMITTED_ROLE_ID = os.getenv("PERMITTED_ROLE_ID")
ROBLOX_GROUP_ID = os.getenv("ROBLOX_GROUP_ID")

# Channel Information
SESSION_CHANNEL_ID = os.getenv("SESSION_CHANNEL_ID")
TIMETABLE_CLAIMING_ID = os.getenv("TIMETABLE_CLAIMING_ID")
TIMETABLE_CHANNEL_ID = os.getenv("TIMETABLE_CHANNEL_ID")
TICKET_CHANNEL_ID = os.getenv("TICKET_CHANNEL_ID")
TICKET_TRANSCRIPT_ID = os.getenv("TICKET_TRANSCRIPT_ID")
TICKET_CATEGORY_ID = os.getenv("TICKET_CATEGORY_ID")