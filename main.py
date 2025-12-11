import discord
from discord.ext import commands, tasks
import config
import os
import asyncio
from utilities.TimetableHandler import setup as timetable_setup, handle_timetable_message
from utilities.TicketHandler import setup_ticket_handler
from utilities.SessionHandler import SessionHandler

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
status_index = 0

# Initialize SessionHandler
bot.session_handler = SessionHandler(bot)

@bot.event
async def on_ready():
    # Initialize the timetable handler
    await timetable_setup(bot)
    print('Timetable handler initialized')
    
    # Initialize the ticket handler
    setup_ticket_handler(bot)
    print('Ticket handler initialized')
    
    print('Session handler initialized')
    
    # Sync slash commands globally
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s) globally")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    
    rotate_status.start()
    print(f'{bot.user} is now online!')

@bot.event
async def on_message(message):
    # Handle timetable claiming messages
    await handle_timetable_message(bot, message)
    
    # Process other commands
    await bot.process_commands(message)

@tasks.loop(seconds=10)
async def rotate_status():
    global status_index
    
    total_members = sum(guild.member_count for guild in bot.guilds)
    
    statuses = [
        discord.CustomActivity(name=f"Watching {total_members} members"),
        discord.CustomActivity(name="Watching over Waterstone"),
        discord.CustomActivity(name="Answering your tickets")
    ]
    
    await bot.change_presence(activity=statuses[status_index])
    status_index = (status_index + 1) % len(statuses)

@rotate_status.before_loop
async def before_rotate_status():
    await bot.wait_until_ready()

async def load_extensions():
    extensions = [
        'commands.public_commands.botinfo',
        'commands.public_commands.profile',
        'commands.staff_commands.activity',
        'commands.developer_commands.eval',
        'commands.developer_commands.diagnose',
        'commands.staff_commands.timetable',
        'commands.staff_commands.ticket',
        'commands.staff_commands.session',
        'commands.developer_commands.send'
    ]
    
    for extension in extensions:
        try:
            await bot.load_extension(extension)
            print(f"Loaded extension: {extension}")
        except Exception as e:
            print(f"Failed to load extension {extension}: {e}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(config.DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())