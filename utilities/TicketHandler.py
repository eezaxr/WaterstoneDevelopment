import discord
from discord.ui import View, Button, Modal, TextInput
import asyncio
from datetime import datetime
import config

# Store blacklisted users in memory (kept for future use if needed)
BLACKLISTED_USERS = set()

def is_user_blacklisted(user_id):
    """Check if a user is blacklisted"""
    return user_id in BLACKLISTED_USERS

def blacklist_user(user_id):
    """Add a user to the blacklist"""
    BLACKLISTED_USERS.add(user_id)

def unblacklist_user(user_id):
    """Remove a user from the blacklist"""
    BLACKLISTED_USERS.discard(user_id)

async def create_ticket_channel(guild, user, reason):
    """Create a new ticket channel for a user"""
    try:
        # Get category
        category = guild.get_channel(int(config.TICKET_CATEGORY_ID))
        
        # Set up permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                attach_files=True,
                embed_links=True
            ),
            guild.me: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                manage_channels=True,
                manage_messages=True,
                attach_files=True,
                embed_links=True
            )
        }
        
        # Add permitted role permissions if configured
        if config.PERMITTED_ROLE_ID:
            permitted_role = guild.get_role(int(config.PERMITTED_ROLE_ID))
            if permitted_role:
                overwrites[permitted_role] = discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    manage_messages=True,
                    attach_files=True,
                    embed_links=True
                )
        
        # Create channel with user ID in topic for tracking
        channel_name = f"ticket-{user.name.lower()}"
        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"<@{user.id}>",  # Store user ID in topic for reliable tracking
            reason=f"Ticket created by {user} - {reason}"
        )
        
        return channel
        
    except Exception as e:
        print(f"Error creating ticket channel: {e}")
        return None

def is_ticket_channel(channel):
    """Check if a channel is a ticket channel by checking if it's in the ticket category"""
    try:
        return channel.category_id == int(config.TICKET_CATEGORY_ID)
    except:
        return False

def has_staff_permissions(member):
    """Check if a member has staff permissions"""
    if config.PERMITTED_ROLE_ID:
        permitted_role = member.guild.get_role(int(config.PERMITTED_ROLE_ID))
        if permitted_role and permitted_role in member.roles:
            return True
    return member.guild_permissions.manage_channels

class TicketReasonModal(Modal, title='Create Support Ticket'):
    reason = TextInput(
        label='Reason for ticket',
        placeholder='Please describe your issue or question.',
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=500
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        ticket_channel = await create_ticket_channel(interaction.guild, interaction.user, self.reason.value)
        
        if ticket_channel:
            success_embed = discord.Embed(
                title="<:Tick:1446847553365737554>   Waterstone Support",
                description=f"Your ticket has been created: {ticket_channel.mention}",
                color=None
            )
            success_embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
            
            # Ping permitted role
            if config.PERMITTED_ROLE_ID:
                permitted_role = interaction.guild.get_role(int(config.PERMITTED_ROLE_ID))
                if permitted_role:
                    ping_message = await ticket_channel.send(f"{permitted_role.mention}")
                    await ping_message.delete()
            
            # Send ticket info embeds
            embed1 = discord.Embed(
                title="Waterstone Support",
                description=(
                    "Thank you for opening a ticket, a member of our Leadership Team will speak to you momentarily. "
                    "We advise you to follow our ticket rules when waiting for a response.\n\n"
                    "**Some thinks to remember**;\n"
                    "- Abusing the system will result into being moderated.\n"
                    "- Please allow 24-48 hours for our team to process your enquiry.\n"
                    "- Failure to respond to the ticket after a certain time will result in closure."
                ),
                color=None
            )
            embed1.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
            
            embed2 = discord.Embed(
                description=f"**Reason**: {self.reason.value}\n**Opened by**: {interaction.user.mention}",
                color=None
            )
            embed2.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
            
            await ticket_channel.send(content=interaction.user.mention, embeds=[embed1, embed2])
        else:
            error_embed = discord.Embed(
                title="<:PersonWarning:1446847748677570651>   Waterstone Support",
                description="Failed to create ticket. Please contact an administrator.",
                color=None
            )
            error_embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

class TicketPanelView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(
        label='Create Ticket',
        style=discord.ButtonStyle.gray,
        custom_id='create_ticket_button'
    )
    async def create_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        existing_ticket = discord.utils.get(guild.channels, name=f"ticket-{interaction.user.name.lower()}")
        
        if existing_ticket:
            embed = discord.Embed(
                title="<:Cross:1446847583510331392>   Waterstone Support",
                description=f"You already have an open ticket: {existing_ticket.mention}",
                color=None
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        modal = TicketReasonModal()
        await interaction.response.send_modal(modal)

async def create_ticket_panel(channel):
    """Create the ticket panel in the specified channel"""
    embed = discord.Embed(
        title="Waterstone Support",
        description=(
            "At Waterstone, we want to cater to all of our members by offering a wide variety of support. "
            "If you need to speak to a member of our Leadership Team, please open a ticket below.\n\n"
            "**Before opening a ticket, be aware of these things**;\n"
            "- Abusing the system will result into being moderated.\n"
            "- Please allow 24-48 hours for our team to process your enquiry.\n"
            "- Failure to respond to the ticket after a certain time will result in closure."
        ),
        color=None
    )
    embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
    
    view = TicketPanelView()
    message = await channel.send(embed=embed, view=view)
    return message

async def check_and_create_panel(bot):
    """Check if the ticket panel exists, if not create it"""
    try:
        print("Starting panel check...")
        guild = bot.get_guild(int(config.GUILD_ID))
        if not guild:
            print(f"Guild not found! Guild ID: {config.GUILD_ID}")
            return
        
        print(f"Guild found: {guild.name}")
        ticket_channel = guild.get_channel(int(config.TICKET_CHANNEL_ID))
        if not ticket_channel:
            print(f"Ticket channel not found! Channel ID: {config.TICKET_CHANNEL_ID}")
            return
        
        print(f"Ticket channel found: {ticket_channel.name}")
        
        # Check if panel already exists by looking for messages with the button
        panel_exists = False
        async for message in ticket_channel.history(limit=100):
            if message.author == bot.user:
                # Check if message has embeds
                if message.embeds:
                    embed = message.embeds[0]
                    # Check if this is the ticket panel embed
                    if "Waterstone Support" in str(embed.title):
                        panel_exists = True
                        print("Ticket panel already exists")
                        break
        
        if not panel_exists:
            print("Creating ticket panel...")
            await create_ticket_panel(ticket_channel)
            print("Ticket panel created successfully!")
    
    except Exception as e:
        print(f"Error checking/creating ticket panel: {e}")
        import traceback
        traceback.print_exc()

def setup_ticket_handler(bot):
    """Setup ticket handler and register persistent views"""
    print("Setting up ticket handler...")
    
    # Register the persistent view so buttons work after restart
    bot.add_view(TicketPanelView())
    
    # Schedule the panel check for after the bot is ready
    async def delayed_check():
        await bot.wait_until_ready()
        print("Bot is ready, checking ticket panel...")
        await check_and_create_panel(bot)
    
    # Create the task
    bot.loop.create_task(delayed_check())