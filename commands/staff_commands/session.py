import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import config

class SessionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session_handler = bot.session_handler
    
    # Create a command group for session commands
    session_group = app_commands.Group(name="session", description="Session management commands")
    
    @session_group.command(name="start", description="Start a new training session")
    @app_commands.describe(
        start_time="Start time in HH:MM format (24-hour, e.g., 14:30)",
        end_time="End time in HH:MM format (24-hour, e.g., 16:00)"
    )
    @app_commands.checks.has_role(int(config.PERMITTED_ROLE_ID))
    async def session_start(self, interaction: discord.Interaction, start_time: str, end_time: str):
        """Start a new training session with specified times"""
        
        # Check if there's already an active session
        if self.session_handler.has_active_session(interaction.guild.id):
            embed = discord.Embed(
                title="<:Cross:1446847583510331392>  Error",
                description="There is already an active session running!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Validate time format
        try:
            start_hour, start_min = map(int, start_time.split(':'))
            end_hour, end_min = map(int, end_time.split(':'))
            
            if not (0 <= start_hour < 24 and 0 <= start_min < 60):
                raise ValueError("Invalid start time")
            if not (0 <= end_hour < 24 and 0 <= end_min < 60):
                raise ValueError("Invalid end time")
            
            # Create datetime objects for today with specified times
            now = datetime.utcnow()
            start_datetime = now.replace(hour=start_hour, minute=start_min, second=0, microsecond=0)
            end_datetime = now.replace(hour=end_hour, minute=end_min, second=0, microsecond=0)
            
            # If end time is before start time, assume it's the next day
            if end_datetime <= start_datetime:
                end_datetime += timedelta(days=1)
            
        except ValueError:
            embed = discord.Embed(
                title="<:Cross:1446847583510331392>  Invalid Time Format",
                description="Please use HH:MM format (24-hour). Example: 14:30 for 2:30 PM",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        # Start the session
        success = await self.session_handler.start_session(
            interaction, 
            interaction.user, 
            start_datetime, 
            end_datetime
        )
        
        if success:
            start_timestamp = int(start_datetime.timestamp())
            end_timestamp = int(end_datetime.timestamp())
            
            embed = discord.Embed(
                title="Session Claimed",
                description=f"You have successfully claimed session with the following information:\n\n**Host**: {interaction.user.mention}\n**Start Time**: <t:{start_timestamp}:t>\n**End Time**: <t:{end_timestamp}:t>"
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=69205d2d&is=691f0bad&hm=263131bcaa38e47255cc8111dd97c0fff3df66e81296d25031d15e45ae1daeda&=&format=webp&quality=lossless")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="<:Cross:1446847583510331392>  Error",
                description="Failed to start the session. Please check the bot configuration.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @session_group.command(name="cancel", description="Cancel the current training session")
    @app_commands.checks.has_role(int(config.PERMITTED_ROLE_ID))
    async def session_cancel(self, interaction: discord.Interaction):
        """Cancel the current training session"""
        
        # Check if there's an active session
        if not self.session_handler.has_active_session(interaction.guild.id):
            embed = discord.Embed(
                title="<:Cross:1446847583510331392>  Error",
                description="There is no active session to cancel!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Get session data before cancelling
        session = self.session_handler.get_active_session(interaction.guild.id)
        start_timestamp = int(session['start_time'].timestamp())
        cancel_timestamp = int(datetime.utcnow().timestamp())
            
        # Cancel the session
        success = await self.session_handler.cancel_session(interaction)
        
        if success:
            embed = discord.Embed(
                title="Session Cancelled",
                description=f"You have successfully cancelled the upcoming session with the following information:\n\n**Host**: <@{session['host_id']}>\n**Start Time**: <t:{start_timestamp}:t>\n**End Time**: <t:{cancel_timestamp}:t>"
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=69205d2d&is=691f0bad&hm=263131bcaa38e47255cc8111dd97c0fff3df66e81296d25031d15e45ae1daeda&=&format=webp&quality=lossless")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="<:Cross:1446847583510331392>  Error",
                description="Failed to cancel the session.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @session_start.error
    @session_cancel.error
    async def session_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Handle errors for session commands"""
        if isinstance(error, app_commands.errors.MissingRole):
            embed = discord.Embed(
                title="<:Cross:1446847583510331392>  Permission Denied",
                description="You don't have permission to use this command!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="<:Cross:1446847583510331392>  Error",
                description=f"An error occurred: {str(error)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(SessionCommands(bot))