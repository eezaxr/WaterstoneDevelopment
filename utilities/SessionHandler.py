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
        self.scheduled_sessions: Dict[int, list] = {}  # guild_id: [session_data]
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
        
        # Send session message with @everyone ping
        message = await session_channel.send(content="@everyone", embed=embed)
        session_data['message_id'] = message.id
        
        # Store session
        self.active_sessions[guild_id] = session_data
        
        return True
    
    async def schedule_session(self, interaction: discord.Interaction, host: discord.Member,
                              start_time: datetime, end_time: datetime, title: str = None) -> Optional[discord.ScheduledEvent]:
        """Schedule a session for the future and create a server event"""
        guild_id = interaction.guild.id
        
        # Initialize scheduled sessions list if not exists
        if guild_id not in self.scheduled_sessions:
            self.scheduled_sessions[guild_id] = []
        
        # Create session data
        session_data = {
            'host': host,
            'host_id': host.id,
            'start_time': start_time,
            'end_time': end_time,
            'status': 'scheduled',
            'event_id': None,
            'title': title or "Waterstone Training Session"
        }
        
        try:
            # Create Discord server event
            event = await interaction.guild.create_scheduled_event(
                name=session_data['title'],
                description=f"Hosted by {host.display_name}\n\nJoin us for an exciting training session on our school premises!",
                start_time=start_time,
                end_time=end_time,
                entity_type=discord.EntityType.external,
                location="Waterstone Academy",
                privacy_level=discord.PrivacyLevel.guild_only
            )
            
            session_data['event_id'] = event.id
            
            # Add to scheduled sessions
            self.scheduled_sessions[guild_id].append(session_data)
            
            return event
            
        except Exception as e:
            print(f"Error scheduling session: {e}")
            return None
    
    @tasks.loop(seconds=30)
    async def check_sessions(self):
        """Check for sessions that need to end or start"""
        now = datetime.utcnow()
        
        # Check active sessions for ending
        guilds_to_end = []
        for guild_id, session_data in self.active_sessions.items():
            if now >= session_data['end_time']:
                guilds_to_end.append(guild_id)
        
        # End sessions that have reached their end time
        for guild_id in guilds_to_end:
            await self._auto_end_session(guild_id)
        
        # Check scheduled sessions for starting
        for guild_id, sessions in list(self.scheduled_sessions.items()):
            sessions_to_start = []
            remaining_sessions = []
            
            for session_data in sessions:
                # Check if it's time to start (within 30 seconds)
                if session_data['start_time'] <= now:
                    sessions_to_start.append(session_data)
                else:
                    remaining_sessions.append(session_data)
            
            # Start scheduled sessions
            for session_data in sessions_to_start:
                await self._auto_start_scheduled_session(guild_id, session_data)
            
            # Update scheduled sessions list
            if remaining_sessions:
                self.scheduled_sessions[guild_id] = remaining_sessions
            else:
                self.scheduled_sessions.pop(guild_id, None)
    
    @check_sessions.before_loop
    async def before_check_sessions(self):
        """Wait until the bot is ready before starting the task"""
        await self.bot.wait_until_ready()
    
    async def _auto_start_scheduled_session(self, guild_id: int, session_data: dict):
        """Automatically start a scheduled session"""
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return
        
        # Check if there's already an active session
        if guild_id in self.active_sessions:
            print(f"Cannot start scheduled session - active session already running in guild {guild_id}")
            return
        
        host = guild.get_member(session_data['host_id'])
        if not host:
            print(f"Cannot start scheduled session - host not found in guild {guild_id}")
            return
        
        # Get session channel
        session_channel = self.bot.get_channel(int(config.SESSION_CHANNEL_ID))
        if not session_channel:
            return
        
        # Create session embed
        start_timestamp = int(session_data['start_time'].timestamp())
        end_timestamp = int(session_data['end_time'].timestamp())
        embed = discord.Embed(
            title="Waterstone Session Starting",
            description=f"Our session has now started on our school premises. We are so exited to see you on our campus! If you have any questions, please find out session host.\n\n**Host**: {host.mention}\n**Start Time**: <t:{start_timestamp}:t>\n**End Time**: <t:{end_timestamp}:t>"
        )
        embed.set_image(url="https://media.discordapp.net/attachments/1353870922712354900/1437239861802303628/WSALine.png?ex=69205d2d&is=691f0bad&hm=263131bcaa38e47255cc8111dd97c0fff3df66e81296d25031d15e45ae1daeda&=&format=webp&quality=lossless")
        
        try:
            # Send session message with @everyone ping
            message = await session_channel.send(content="@everyone", embed=embed)
            
            # Store as active session
            active_session_data = {
                'host': host,
                'host_id': host.id,
                'start_time': session_data['start_time'],
                'end_time': session_data['end_time'],
                'status': 'active',
                'message_id': message.id
            }
            
            self.active_sessions[guild_id] = active_session_data
            
        except Exception as e:
            print(f"Error starting scheduled session: {e}")
    
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
    
    async def cancel_scheduled_session(self, guild_id: int, event_id: int) -> bool:
        """Cancel a scheduled session"""
        if guild_id not in self.scheduled_sessions:
            return False
        
        # Find and remove the scheduled session
        sessions = self.scheduled_sessions[guild_id]
        for i, session in enumerate(sessions):
            if session['event_id'] == event_id:
                sessions.pop(i)
                
                # Delete the server event
                guild = self.bot.get_guild(guild_id)
                if guild:
                    try:
                        event = await guild.fetch_scheduled_event(event_id)
                        await event.delete()
                    except:
                        pass
                
                return True
        
        return False
        
    def get_active_session(self, guild_id: int) -> Optional[dict]:
        """Get the active session for a guild"""
        return self.active_sessions.get(guild_id)
    
    def get_scheduled_sessions(self, guild_id: int) -> list:
        """Get all scheduled sessions for a guild"""
        return self.scheduled_sessions.get(guild_id, [])
        
    def has_active_session(self, guild_id: int) -> bool:
        """Check if a guild has an active session"""
        return guild_id in self.active_sessions