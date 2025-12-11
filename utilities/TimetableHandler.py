import discord
from discord.ext import commands
import re
from datetime import datetime
from typing import Optional, Dict

class TimetableHandler:
    def __init__(self, bot):
        self.bot = bot
        self.divider_image = "https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=6921aead&is=69205d2d&hm=72ec192652bcd007b12ecaf19cc15333e92e8fbb237271e767966df4fa015afb&=&format=webp&quality=lossless"
        self.timetable_structure = {
            "Period 1": ["Year 7", "Year 8", "Reflection", "Pastoral", "Reception"],
            "Period 2": ["Year 7", "Year 8", "Reflection", "Pastoral", "Reception"],
            "Break": ["Reflection", "Pastoral", "Reception"],
            "Period 3": ["Year 7", "Year 8", "Reflection", "Pastoral", "Reception"],
            "Lunch": ["Reflection", "Pastoral", "Reception"],
            "Period 4": ["Year 7", "Year 8", "Reflection", "Pastoral", "Reception"]
        }
        self.timetable_data = {}
        self.timetable_message_id = None
        
        self.success_emoji = "<:Tick:1446847553365737554>"
        self.error_emoji = "<:Cross:1446847583510331392>"
        self.warning_emoji = "<:Warning:1446849251853471764>"
        
        self.auto_rooms = {
            "Reflection": "F13",
            "Pastoral": "G13",
            "Reception": "G01"
        }
        
    def parse_claim(self, message_content: str) -> Optional[Dict[str, str]]:
        """
        Parse the claim message and extract information.
        Returns a dict with the claim info if valid, None otherwise.
        Supports shorthand format only.
        """
        lines = [line.strip() for line in message_content.strip().split('\n') if line.strip()]
        return self._parse_shorthand_format(lines)
    
    def _is_period(self, text: str) -> Optional[str]:
        """Check if text is a period and return normalized format"""
        text_clean = text.strip()
        text_lower = text_clean.lower()
        
        if text_lower in ['break', 'lunch']:
            return text_clean.capitalize()
        
        if text_lower.startswith('p') and len(text_clean) > 1:
            period_num = text_clean[1:].strip()
            if period_num.isdigit():
                return f"Period {period_num}"
        
        if text_lower.startswith('period'):
            match = re.search(r'period\s*(\d+)', text_clean, re.IGNORECASE)
            if match:
                return f"Period {match.group(1)}"
        
        if text_clean.isdigit() and text_clean in ['1', '2', '3', '4']:
            return f"Period {text_clean}"
        
        return None
    
    def _is_year_group(self, text: str) -> Optional[str]:
        """Check if text is a year group and return normalized format"""
        text_clean = text.strip()
        text_lower = text_clean.lower()
        
        # Check for Reflection, Pastoral, and Reception
        if text_lower in ['reflection', 'pastoral', 'reception']:
            return text_clean.capitalize()
        
        if text_lower.startswith('y') and len(text_clean) > 1:
            year_num = text_clean[1:].strip()
            if year_num.isdigit():
                return f"Year {year_num}"
        
        if text_lower.startswith('year'):
            match = re.search(r'year\s*(\d+)', text_clean, re.IGNORECASE)
            if match:
                return f"Year {match.group(1)}"
        
        if text_clean.isdigit() and text_clean in ['7', '8']:
            return f"Year {text_clean}"
        
        return None
    
    def _parse_with_alternatives(self, line: str, validator_func) -> Optional[str]:
        """Parse a line that might have comma-separated alternatives"""
        options = [opt.strip() for opt in line.split(',')]
        for opt in options:
            result = validator_func(opt)
            if result:
                return result
        return None
    
    def _parse_shorthand_format(self, lines: list) -> Optional[Dict[str, str]]:
        """Parse the shorthand format - flexible to handle multiple variations"""
        if len(lines) < 2:
            return None
        
        claim_data = {}
        idx = 0
        
        # Parse period
        period = self._parse_with_alternatives(lines[idx], self._is_period)
        if not period:
            return None
        claim_data["period"] = period
        idx += 1
        
        # Check if next line is a year group (Reflection/Pastoral/Reception only format)
        year_group_check = self._parse_with_alternatives(lines[idx], self._is_year_group)
        
        # If it's Reflection, Pastoral, or Reception as the FIRST thing after period
        if year_group_check and year_group_check in ["Reflection", "Pastoral", "Reception"]:
            claim_data["subject"] = year_group_check
            claim_data["year_group"] = year_group_check
            claim_data["room_number"] = self.auto_rooms.get(year_group_check, "N/A")
            return claim_data
        
        # Otherwise, it's a regular lesson format: Subject -> Year -> Room
        # Line at idx should be the subject
        claim_data["subject"] = lines[idx]
        idx += 1
        
        if idx >= len(lines):
            return None
        
        # Next line should be year group
        year_group = self._parse_with_alternatives(lines[idx], self._is_year_group)
        if not year_group:
            return None
        claim_data["year_group"] = year_group
        idx += 1
        
        # Next line should be room number (required for Year 7/8)
        if idx >= len(lines):
            return None
        claim_data["room_number"] = lines[idx]
        
        return claim_data
    
    def is_slot_available(self, period: str, year_group: str) -> bool:
        """Check if a timetable slot is available"""
        slot_key = f"{period}_{year_group}"
        return slot_key not in self.timetable_data
    
    def claim_slot(self, period: str, year_group: str, staff_mention: str, room: str, subject: str):
        """Claim a timetable slot"""
        slot_key = f"{period}_{year_group}"
        self.timetable_data[slot_key] = {
            "staff": staff_mention,
            "room": str(room),
            "subject": str(subject)
        }
        print(f"DEBUG: Claimed slot {slot_key} - Staff: {staff_mention}, Room: {room}, Subject: {subject}")
    
    def unclaim_slot(self, period: str, year_group: str) -> bool:
        """Unclaim a timetable slot. Returns True if successful."""
        slot_key = f"{period}_{year_group}"
        if slot_key in self.timetable_data:
            del self.timetable_data[slot_key]
            return True
        return False
    
    def reset_timetable(self):
        """Reset all timetable claims"""
        self.timetable_data = {}
    
    def generate_timetable_description(self) -> str:
        """Generate the timetable description with all current claims"""
        description_parts = []
        
        for period, year_groups in self.timetable_structure.items():
            description_parts.append(f"**{period}**")
            
            for year_group in year_groups:
                slot_key = f"{period}_{year_group}"
                
                if slot_key in self.timetable_data:
                    slot_data = self.timetable_data[slot_key]
                    staff = slot_data.get('staff', 'Unknown')
                    room = slot_data.get('room', 'N/A')
                    description_parts.append(
                        f"{year_group}: {staff} - **{room}**"
                    )
                else:
                    description_parts.append(f"{year_group}: **Unclaimed**")
            
            description_parts.append("")
        
        return "\n".join(description_parts)
    
    async def update_timetable_message(self, channel: discord.TextChannel):
        """Update or create the timetable message"""
        description = self.generate_timetable_description()
        
        embed = discord.Embed(
            title="Staff Timetable",
            description=description
        )
        embed.set_image(url=self.divider_image)
        
        if self.timetable_message_id:
            try:
                message = await channel.fetch_message(self.timetable_message_id)
                await message.edit(embed=embed)
            except discord.NotFound:
                new_message = await channel.send(embed=embed)
                self.timetable_message_id = new_message.id
        else:
            new_message = await channel.send(embed=embed)
            self.timetable_message_id = new_message.id
    
    async def process_claim(self, message: discord.Message) -> bool:
        """
        Process a timetable claim message.
        Returns True if successful, False otherwise.
        """
        claim_data = self.parse_claim(message.content)
        
        if not claim_data:
            await message.add_reaction(self.error_emoji)
            error_embed = discord.Embed(
                title="Error while claiming slot",
                description="You aren't using the correct format when trying to claim a slot, please look at the following examples for guidance.\n\n"
                           "**Lessons:**\n"
                           "```Period 1\n"
                           "Maths\n"
                           "Year 7\n"
                           "FO7```\n"
                           "**Reflection/Pastoral/Reception:**\n"
                           "```Period 1\n"
                           "Reflection```"
            )
            error_embed.set_image(url=self.divider_image)
            try:
                await message.author.send(embed=error_embed)
            except discord.Forbidden:
                await message.reply(embed=error_embed, delete_after=30)
            return False
        
        if not self.is_slot_available(claim_data['period'], claim_data['year_group']):
            await message.add_reaction(self.error_emoji)
            error_embed = discord.Embed(
                title="Error while claiming slot",
                description="We were unable to allocate you this slot, this slot has already been taken by another member of staff. Please claim another free slot."
            )
            error_embed.set_image(url=self.divider_image)
            try:
                await message.author.send(embed=error_embed)
            except discord.Forbidden:
                await message.reply(embed=error_embed, delete_after=30)
            return False
        
        self.claim_slot(
            claim_data['period'],
            claim_data['year_group'],
            message.author.mention,
            claim_data['room_number'],
            claim_data['subject']
        )
        
        from config import TIMETABLE_CHANNEL_ID
        timetable_channel = self.bot.get_channel(int(TIMETABLE_CHANNEL_ID))
        
        if not timetable_channel:
            await message.add_reaction(self.warning_emoji)
            return False
        
        await self.update_timetable_message(timetable_channel)
        await message.add_reaction(self.success_emoji)
        
        success_embed = discord.Embed(
            title="Successfully Claimed",
            description=f"You have successfully claimed **{claim_data['year_group']}**, **{claim_data['period']}** in **{claim_data['room_number']}**. Please make sure you attend session and arrive to your designated area."
        )
        success_embed.set_image(url=self.divider_image)
        try:
            await message.author.send(embed=success_embed)
        except discord.Forbidden:
            await message.reply(embed=success_embed, delete_after=15)
        
        return True

async def setup(bot):
    """Setup function for the timetable handler"""
    handler = TimetableHandler(bot)
    bot.timetable_handler = handler
    return handler

async def handle_timetable_message(bot, message):
    """Call this function from your main bot's on_message event"""
    if message.author.bot:
        return
    
    from config import TIMETABLE_CLAIMING_ID
    
    if str(message.channel.id) == TIMETABLE_CLAIMING_ID:
        if hasattr(bot, 'timetable_handler'):
            await bot.timetable_handler.process_claim(message)