import discord
from discord import app_commands
from discord.ext import commands

class TimetableCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    timetable_group = app_commands.Group(name="timetable", description="Timetable management commands")
    
    @timetable_group.command(name="reset", description="Reset the entire timetable")
    @app_commands.default_permissions(administrator=True)
    async def reset(self, interaction: discord.Interaction):
        """Reset the entire timetable (Admin only)"""
        await interaction.response.defer(ephemeral=True)
        
        if not hasattr(self.bot, 'timetable_handler'):
            await interaction.followup.send("Timetable handler not initialized.", ephemeral=True)
            return
        
        handler = self.bot.timetable_handler
        handler.reset_timetable()
        
        from config import TIMETABLE_CHANNEL_ID
        timetable_channel = self.bot.get_channel(int(TIMETABLE_CHANNEL_ID))
        
        if timetable_channel:
            try:
                await timetable_channel.purge(limit=100)
            except discord.Forbidden:
                pass
            except Exception as e:
                pass
            
            handler.timetable_message_id = None
            await handler.update_timetable_message(timetable_channel)
        
        embed = discord.Embed(
            title="Timetable Reset",
            description="The timetable has been successfully reset. All slots are now unclaimed."
        )
        embed.set_image(url=handler.divider_image)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @timetable_group.command(name="edit", description="Edit a timetable slot")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(
        user="The staff member to assign to this slot",
        period="The period (e.g., Period 1, P1, Break, Lunch)",
        subject="The subject being taught (or Reflection/Pastoral)",
        year="The year group (e.g., Year 7, Y7, Reflection, Pastoral)",
        room="The room number (auto-filled for Reflection/Pastoral)"
    )
    async def edit(
        self, 
        interaction: discord.Interaction, 
        user: discord.Member,
        period: str,
        subject: str,
        year: str,
        room: str = None
    ):
        """Edit a timetable slot by assigning or updating it"""
        await interaction.response.defer(ephemeral=True)
        
        if not hasattr(self.bot, 'timetable_handler'):
            await interaction.followup.send("Timetable handler not initialized.", ephemeral=True)
            return
        
        handler = self.bot.timetable_handler
        
        # Normalize the inputs
        period_normalized = handler._is_period(period)
        year_group_normalized = handler._is_year_group(year)
        
        if not period_normalized or not year_group_normalized:
            error_embed = discord.Embed(
                title="Invalid Input",
                description="Please provide a valid period and year group.\n\n"
                           "**Valid Periods:** Period 1, Period 2, Break, Period 3, Lunch, Period 4\n"
                           "**Valid Year Groups:** Year 7, Year 8, Reflection, Pastoral"
            )
            error_embed.set_image(url=handler.divider_image)
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return
        
        # Auto-fill room for Reflection/Pastoral if not provided
        if year_group_normalized in ["Reflection", "Pastoral"]:
            room_number = handler.auto_rooms.get(year_group_normalized, "N/A")
        else:
            if not room:
                error_embed = discord.Embed(
                    title="Room Required",
                    description="Please provide a room number for regular lessons (Year 7/8)."
                )
                error_embed.set_image(url=handler.divider_image)
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return
            room_number = room
        
        # Check if slot exists (if editing) or if it's available (if creating new)
        slot_key = f"{period_normalized}_{year_group_normalized}"
        was_editing = slot_key in handler.timetable_data
        
        # Claim/update the slot
        handler.claim_slot(
            period_normalized,
            year_group_normalized,
            user.mention,
            room_number,
            subject
        )
        
        # Update the timetable message
        from config import TIMETABLE_CHANNEL_ID
        timetable_channel = self.bot.get_channel(int(TIMETABLE_CHANNEL_ID))
        
        if timetable_channel:
            await handler.update_timetable_message(timetable_channel)
        
        # Send success message
        action = "updated" if was_editing else "assigned"
        success_embed = discord.Embed(
            title=f"Slot {action.capitalize()}",
            description=f"Successfully {action} **{year_group_normalized}** during **{period_normalized}** to {user.mention}.\n\n"
                       f"**Subject:** {subject}\n"
                       f"**Room:** {room_number}"
        )
        success_embed.set_image(url=handler.divider_image)
        await interaction.followup.send(embed=success_embed, ephemeral=True)

async def setup(bot):
    """Setup function for loading the cog"""
    await bot.add_cog(TimetableCommands(bot))