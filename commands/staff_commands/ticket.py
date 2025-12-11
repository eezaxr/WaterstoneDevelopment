import discord
from discord import app_commands
from discord.ext import commands
from utilities.TicketHandler import (
    create_ticket_channel, 
    is_ticket_channel, 
    has_staff_permissions
)
from utilities.TranscriptHandler import send_transcript, generate_transcript
import config
import asyncio

class TicketCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # Create a command group for ticket commands
    ticket_group = app_commands.Group(name="ticket", description="Ticket management commands")
    
    @ticket_group.command(name="close", description="Close the current ticket")
    @app_commands.describe(reason="Reason for closing the ticket")
    async def ticket_close(self, interaction: discord.Interaction, reason: str = None):
        """Close a ticket channel"""
        
        # Check if in a ticket channel
        if not is_ticket_channel(interaction.channel):
            embed = discord.Embed(
                title="<:Cross:1446847583510331392>  Waterstone Support",
                description="This command can only be used in ticket channels!",
                color=None
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check permissions
        if not has_staff_permissions(interaction.user):
            embed = discord.Embed(
                title="<:Cross:1446847583510331392>  Waterstone Support",
                description="You don't have permission to close tickets!",
                color=None
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Default reason if not provided
        close_reason = reason if reason else "No reason provided"
        
        # Send closing message
        embed = discord.Embed(
            title="<:People:1446847702804598886>  Waterstone Support",
            description="Generating transcript and closing ticket...",
            color=None
        )
        embed.add_field(name="Reason", value=close_reason, inline=False)
        embed.add_field(name="Closed By", value=interaction.user.mention, inline=True)
        embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
        
        await interaction.followup.send(embed=embed)
        
        # Generate and send transcript with close reason
        await send_transcript(interaction.channel, interaction.user, close_reason=close_reason)
        
        # Wait and delete channel
        await asyncio.sleep(3)
        await interaction.channel.delete(reason=f"Ticket closed by {interaction.user} - {close_reason}")
    
    @ticket_group.command(name="add", description="Add a user to the ticket")
    @app_commands.describe(user="The user to add to the ticket")
    async def ticket_add(self, interaction: discord.Interaction, user: discord.Member):
        """Add a user to the current ticket"""
        
        # Check if in a ticket channel
        if not is_ticket_channel(interaction.channel):
            embed = discord.Embed(
                title="<:Cross:1446847583510331392>  Waterstone Support",
                description="This command can only be used in ticket channels!",
                color=None
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check permissions
        if not has_staff_permissions(interaction.user):
            embed = discord.Embed(
                title="<:Cross:1446847583510331392>  Waterstone Support",
                description="You don't have permission to add users!",
                color=None
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Add user to channel
        await interaction.channel.set_permissions(
            user,
            read_messages=True,
            send_messages=True,
            attach_files=True,
            embed_links=True
        )
        
        embed = discord.Embed(
            title="<:People:1446847702804598886>  Waterstone Support",
            description=f"{user.mention} has been added to this ticket by {interaction.user.mention}",
            color=None
        )
        embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
        
        await interaction.channel.send(embed=embed)
        
        success_embed = discord.Embed(
            title="<:People:1446847702804598886>  Waterstone Support",
            description=f"Added {user.mention} to the ticket",
            color=None
        )
        success_embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
        await interaction.followup.send(embed=success_embed, ephemeral=True)
    
    @ticket_group.command(name="remove", description="Remove a user from the ticket")
    @app_commands.describe(user="The user to remove from the ticket")
    async def ticket_remove(self, interaction: discord.Interaction, user: discord.Member):
        """Remove a user from the current ticket"""
        
        # Check if in a ticket channel
        if not is_ticket_channel(interaction.channel):
            embed = discord.Embed(
                title="<:Cross:1446847583510331392>  Waterstone Support",
                description="This command can only be used in ticket channels!",
                color=None
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check permissions
        if not has_staff_permissions(interaction.user):
            embed = discord.Embed(
                title="<:Cross:1446847583510331392>  Waterstone Support",
                description="You don't have permission to remove users!",
                color=None
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Remove user from channel
        await interaction.channel.set_permissions(user, overwrite=None)
        
        embed = discord.Embed(
            title="<:People:1446847702804598886>  Waterstone Support",
            description=f"{user.mention} has been removed from this ticket by {interaction.user.mention}",
            color=None
        )
        embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
        
        await interaction.channel.send(embed=embed)
        
        success_embed = discord.Embed(
            title="<:People:1446847702804598886>  Waterstone Support",
            description=f"Removed {user.mention} from the ticket",
            color=None
        )
        success_embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
        await interaction.followup.send(embed=success_embed, ephemeral=True)
    
    @ticket_group.command(name="claim", description="Claim the current ticket")
    async def ticket_claim(self, interaction: discord.Interaction):
        """Claim a ticket"""
        
        # Check if in a ticket channel
        if not is_ticket_channel(interaction.channel):
            embed = discord.Embed(
                title="<:Cross:1446847583510331392>  Waterstone Support",
                description="This command can only be used in ticket channels!",
                color=None
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check permissions
        if not has_staff_permissions(interaction.user):
            embed = discord.Embed(
                title="<:Cross:1446847583510331392>  Waterstone Support",
                description="You don't have permission to claim tickets!",
                color=None
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        channel = interaction.channel
        
        # Check if already claimed
        if channel.topic and "Claimed by:" in channel.topic:
            embed = discord.Embed(
                title="<:Cross:1446847583510331392>  Waterstone Support",
                description="This ticket has already been claimed!",
                color=None
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Update channel topic
        await channel.edit(topic=f"Claimed by: {interaction.user.name}")
        
        embed = discord.Embed(
            title="<:People:1446847702804598886>  Waterstone Support",
            description=f"This ticket has been claimed by {interaction.user.mention}",
            color=None
        )
        embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
        
        await interaction.followup.send(embed=embed)
    
    @ticket_group.command(name="rename", description="Rename the current ticket")
    @app_commands.describe(new_name="The new name for the ticket (without 'ticket-' prefix)")
    async def ticket_rename(self, interaction: discord.Interaction, new_name: str):
        """Rename a ticket channel"""
        
        # Check if in a ticket channel
        if not is_ticket_channel(interaction.channel):
            embed = discord.Embed(
                title="<:Cross:1446847583510331392>  Waterstone Support",
                description="This command can only be used in ticket channels!",
                color=None
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check permissions
        if not has_staff_permissions(interaction.user):
            embed = discord.Embed(
                title="<:Cross:1446847583510331392>  Waterstone Support",
                description="You don't have permission to rename tickets!",
                color=None
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Sanitize name
        import re
        sanitized_name = re.sub(r'[^a-z0-9-]', '', new_name.lower().replace(' ', '-'))
        new_channel_name = f"ticket-{sanitized_name}"
        
        old_name = interaction.channel.name
        await interaction.channel.edit(name=new_channel_name)
        
        embed = discord.Embed(
            title="<:People:1446847702804598886>  Waterstone Support",
            description=f"Ticket renamed from `{old_name}` to `{new_channel_name}` by {interaction.user.mention}",
            color=None
        )
        embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
        
        await interaction.channel.send(embed=embed)
        
        success_embed = discord.Embed(
            title="<:People:1446847702804598886>  Waterstone Support",
            description=f"Ticket renamed to `{new_channel_name}`",
            color=None
        )
        success_embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=693423ad&is=6932d22d&hm=96f2ac4bdc5294f7109fc750e3225b22e73dfef514ce605c545e6dadb26ebdb4&=&format=webp&quality=lossless")
        await interaction.followup.send(embed=success_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketCommands(bot))