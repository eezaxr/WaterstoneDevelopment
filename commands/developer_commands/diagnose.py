"""
Diagnose Command
Checks system components and displays their status
"""

import discord
from discord.ext import commands
from discord import app_commands
from utilities.FirebaseHandler import firebase
import asyncio

class Diagnose(commands.Cog):
    """System diagnostics command"""
    
    def __init__(self, bot):
        self.bot = bot
        # Add developer IDs here for permission checking
        self.developer_ids = [790869950076157983]  # Add your Discord IDs: [123456789, 987654321]
    
    def is_developer(self, user_id: int) -> bool:
        """Check if user is a developer"""
        if self.developer_ids and user_id in self.developer_ids:
            return True
        return user_id == self.bot.owner_id if hasattr(self.bot, 'owner_id') else False
    
    async def check_bot_status(self) -> bool:
        """Check if bot is responsive"""
        try:
            return self.bot.user is not None and not self.bot.is_closed()
        except Exception:
            return False
    
    async def check_discord_connection(self) -> bool:
        """Check Discord connection"""
        try:
            return self.bot.latency > 0 and self.bot.latency < 1.0
        except Exception:
            return False
    
    async def check_firebase_connection(self) -> bool:
        """Check Firebase connection"""
        try:
            return firebase.test_connection()
        except Exception:
            return False
    
    async def check_firebase_read(self) -> bool:
        """Check Firebase read capability"""
        try:
            result = firebase.get("accounts")
            return result is not None
        except Exception:
            return False
    
    async def check_firebase_write(self) -> bool:
        """Check Firebase write capability"""
        try:
            test_path = "diagnostics/test"
            test_data = {"test": "write_check"}
            success = firebase.set(test_path, test_data)
            if success:
                firebase.delete(test_path)
            return success
        except Exception:
            return False
    
    async def check_cogs_loaded(self) -> bool:
        """Check if cogs are loaded"""
        try:
            return len(self.bot.cogs) > 0
        except Exception:
            return False
    
    async def check_commands_synced(self) -> bool:
        """Check if commands are synced"""
        try:
            # Check if there are any registered app commands
            commands = await self.bot.tree.fetch_commands()
            return len(commands) > 0
        except Exception:
            return False
    
    async def check_guilds(self) -> bool:
        """Check if bot is in guilds"""
        try:
            return len(self.bot.guilds) > 0
        except Exception:
            return False
    
    @app_commands.command(name="diagnose", description="Run services diagnostics")
    async def diagnose_command(self, interaction: discord.Interaction):
        """
        Run system diagnostics and display results
        
        Args:
            interaction: Discord interaction
        """
        # Permission check
        if not self.is_developer(interaction.user.id):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
            return
        
        # Defer response as checks may take time
        await interaction.response.defer()
        
        # Run all diagnostic checks
        checks = [
            ("Bot Status", self.check_bot_status()),
            ("Discord Connection", self.check_discord_connection()),
            ("Firebase Connection", self.check_firebase_connection()),
            ("Commands Synced", self.check_commands_synced()),
            ("Guild Connectivity", self.check_guilds()),
        ]
        
        # Execute all checks
        results = []
        for check_name, check_coro in checks:
            try:
                passed = await check_coro
                results.append((check_name, passed))
            except Exception:
                results.append((check_name, False))
        
        # Build description
        description = "Waterstone Services check complete.\n\n"
        
        for check_name, passed in results:
            emoji = "<:Tick:1446847553365737554>" if passed else "<:Cross:1446847583510331392>"
            description += f"**{check_name}**\n{emoji}\n\n"
        
        # Create embed
        embed = discord.Embed(
            title="Bot Diagnoses",
            description=description,
            color=None
        )
        
        # Add footer image
        embed.set_image(
            url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=69132e2d&is=6911dcad&hm=47098d9c927db0fa5a2b9ce7bcc63890bc2ec4042916daebd9d93ce0a6f6e280&=&format=webp&quality=lossless"
        )
        
        await interaction.followup.send(embed=embed)


async def setup(bot):
    """Add cog to bot"""
    await bot.add_cog(Diagnose(bot))