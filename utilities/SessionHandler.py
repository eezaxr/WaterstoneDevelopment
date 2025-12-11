import discord
from discord.ext import tasks
from datetime import datetime, timedelta
from typing import Optional, Dict
import config
import asyncio

class SessionHandler:
    def __init__(self, bot):
        self.bot = bot
        self.active_sessions: Dict[int, dict] = {}  # guild_id: session_data
        self._task_started = False
        
    def start_task(self):
        """Start the background task - call this after bot is ready"""
        if not self._task_started:
            self.check_sessions.start()
            self._task_started = True
        
    def cog_unload(self):
        if self._task_started:
            self.check_sessions.cancel()
        
    async def start_session(self, interaction: discord.Interaction, host: discord.Member, 
                          start_time: datetime, end_time: datetime) -> bool:
        """Start a new session with specified start and end times"""
        guild_id = interaction.guild.id
        
        # Check if there's already an active session
        if guild_id in self.active_sessions:
            return False
            
        # Get session channel
        session_channel = self.bot.get_channel(int(config.SESSION_CHANNEL_ID))
        if not session_channel:
            return False
            
        # Create session data
        session_data = {
            'host': host,
            'host_id': host.id,
            'start_time': start_time,
            'end_time': end_time,
            'status': 'active',
            'message_id': None
        }
        
        # Create session embed
        start_timestamp = int(start_time.timestamp())
        end_timestamp = int(end_time.timestamp())
        embed = discord.Embed(
            title="Waterstone Session Starting",
            description=f"Our session has now started on our school premises. We are so exited to see you on our campus! If you have any questions, please find out session host.\n\n**Host**: {host.mention}\n**Start Time**: <t:{start_timestamp}:t>\n**End Time**: <t:{end_timestamp}:t>"
        )
        embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=69205d2d&is=691f0bad&hm=263131bcaa38e47255cc8111dd97c0fff3df66e81296d25031d15e45ae1daeda&=&format=webp&quality=lossless")
        
        # Send session message
        message = await session_channel.send(embed=embed)
        session_data['message_id'] = message.id
        
        # Store session
        self.active_sessions[guild_id] = session_data
        
        return True
    
    @tasks.loop(seconds=30)
    async def check_sessions(self):
        """Check for sessions that need to end"""
        now = datetime.utcnow()
        guilds_to_end = []
        
        for guild_id, session_data in self.active_sessions.items():
            if now >= session_data['end_time']:
                guilds_to_end.append(guild_id)
        
        # End sessions that have reached their end time
        for guild_id in guilds_to_end:
            await self._auto_end_session(guild_id)
    
    @check_sessions.before_loop
    async def before_check_sessions(self):
        """Wait until the bot is ready before starting the task"""
        await self.bot.wait_until_ready()
    
    async def _auto_end_session(self, guild_id: int):
        """Automatically end a session"""
        if guild_id not in self.active_sessions:
            return
            
        session_data = self.active_sessions[guild_id]
        
        start_timestamp = int(session_data['start_time'].timestamp())
        end_timestamp = int(session_data['end_time'].timestamp())
        
        # Get session channel
        session_channel = self.bot.get_channel(int(config.SESSION_CHANNEL_ID))
        if session_channel and session_data['message_id']:
            try:
                message = await session_channel.fetch_message(session_data['message_id'])
                
                # Update embed
                embed = discord.Embed(
                    title="Waterstone Session Ending",
                    description=f"Our session has now ended, thank you to everyone who attended. See you next time!\n\n**Host**: <@{session_data['host_id']}>\n**Start Time**: <t:{start_timestamp}:t>\n**End Time**: <t:{end_timestamp}:t>"
                )
                embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=69205d2d&is=691f0bad&hm=263131bcaa38e47255cc8111dd97c0fff3df66e81296d25031d15e45ae1daeda&=&format=webp&quality=lossless")
                
                await message.edit(embed=embed)
            except Exception as e:
                print(f"Error ending session: {e}")
        
        # Remove session
        self.active_sessions.pop(guild_id, None)
        
    async def cancel_session(self, interaction: discord.Interaction) -> bool:
        """Cancel the active session"""
        guild_id = interaction.guild.id
        
        # Check if there's an active session
        if guild_id not in self.active_sessions:
            return False
            
        session_data = self.active_sessions[guild_id]
        
        start_timestamp = int(session_data['start_time'].timestamp())
        cancel_timestamp = int(datetime.utcnow().timestamp())
        
        # Get session channel
        session_channel = self.bot.get_channel(int(config.SESSION_CHANNEL_ID))
        if session_channel and session_data['message_id']:
            try:
                message = await session_channel.fetch_message(session_data['message_id'])
                
                # Update embed
                embed = discord.Embed(
                    title="Waterstone Session Cancelled",
                    description=f"Our session was cancelled, we're sorry for any inconveniences\ncaused. Our next session will be hopefully active and engaging.\n\n**Host**: <@{session_data['host_id']}>\n**Start Time**: <t:{start_timestamp}:t>\n**End Time**: <t:{cancel_timestamp}:t>"
                )
                embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=69205d2d&is=691f0bad&hm=263131bcaa38e47255cc8111dd97c0fff3df66e81296d25031d15e45ae1daeda&=&format=webp&quality=lossless")
                
                await message.edit(embed=embed)
            except:
                pass
        
        # Remove session
        self.active_sessions.pop(guild_id)
        
        return True
        
    def get_active_session(self, guild_id: int) -> Optional[dict]:
        """Get the active session for a guild"""
        return self.active_sessions.get(guild_id)
        
    def has_active_session(self, guild_id: int) -> bool:
        """Check if a guild has an active session"""
        return guild_id in self.active_sessions