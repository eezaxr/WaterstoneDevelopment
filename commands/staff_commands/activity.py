import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from utilities.FirebaseHandler import firebase


class Activity(commands.Cog):
    """Staff activity tracking command"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="activity", description="View staff activity statistics")
    @app_commands.describe(user="The staff member to check (defaults to yourself)")
    async def activity(self, interaction: discord.Interaction, user: Optional[discord.User] = None):
        """
        Display staff activity statistics from Firebase
        
        Args:
            interaction: Discord interaction
            user: Optional user to check (defaults to command invoker)
        """
        # Default to the command invoker if no user specified
        target_user = user or interaction.user
        
        # Defer response in case Firebase takes time
        await interaction.response.defer()
        
        # Fetch all accounts from Firebase
        accounts = firebase.get("accounts")
        
        # Check if accounts data exists
        if not accounts:
            embed = discord.Embed(
                title="Staff Activity",
                description=f"No accounts data found in database",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Find the account with matching discord_id
        user_account = None
        for account_id, account_data in accounts.items():
            if account_data.get('discord_id') == str(target_user.id):
                user_account = account_data
                break
        
        # Check if user account was found
        if not user_account:
            embed = discord.Embed(
                title="Staff Activity",
                description=f"No activity data found for **{target_user.name}**\nUser may not be linked to an account.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Extract activity statistics
        total_sessions = user_account.get('total_sessions', 0)
        total_minutes = user_account.get('total_minutes', 0)
        total_messages = user_account.get('total_messages', 0)
        roleplay_name = user_account.get('roleplay_name', 'Unknown')
        
        # Create embed with styling
        embed = discord.Embed(
            title="Staff Activity",
            description=f"```{roleplay_name}```",
            color=None  # Default embed color
        )
        
        # Add fields
        embed.add_field(
            name="Total Sessions",
            value=f"`{total_sessions}`",
            inline=True
        )
        
        embed.add_field(
            name="Total Minutes",
            value=f"`{total_minutes}`",
            inline=True
        )
        
        embed.add_field(
            name="Total Messages",
            value=f"`{total_messages}`",
            inline=True
        )
        
        # Set thumbnail to user's avatar
        embed.set_thumbnail(url=target_user.display_avatar.url)
        
        # Set footer image (the line separator)
        embed.set_image(
            url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=69132e2d&is=6911dcad&hm=47098d9c927db0fa5a2b9ce7bcc63890bc2ec4042916daebd9d93ce0a6f6e280&=&format=webp&quality=lossless"
        )
        
        # Send the embed
        await interaction.followup.send(embed=embed)


async def setup(bot):
    """Add cog to bot"""
    await bot.add_cog(Activity(bot))