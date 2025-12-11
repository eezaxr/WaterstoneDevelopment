import discord
from discord.ext import commands
from discord import app_commands
import config

class Send(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Add developer ID for permission checking
        self.developer_ids = [790869950076157983]
        
        # Define preset messages
        self.presets = {
            "CHRISTMAS": {
                "content": "@everyone",
                "embeds": [
                    discord.Embed().set_image(
                        url="https://media.discordapp.net/attachments/1433543011567927376/1447194109008674936/NewChristmasBrand_Informative_1.png?ex=6936bc0b&is=69356a8b&hm=323a00b274569be3822313d034720ee3860dfcaaa008bb0b8cab854540257e65&=&format=webp&quality=lossless&width=1318&height=355"
                    ),
                    discord.Embed().set_image(
                        url="https://media.discordapp.net/attachments/1433543011567927376/1447194136347283566/NewChristmasBrand_Informative_2.png?ex=6936bc11&is=69356a91&hm=96a6abd957dafe65ff308fbcd106d9687a86cc9cf1b4cb41eac012965862559b&=&format=webp&quality=lossless&width=1318&height=90"
                    )
                ]
            }
        }
    
    def is_developer(self, user_id: int) -> bool:
        """Check if user is a developer"""
        # Check against list of developer IDs
        if self.developer_ids and user_id in self.developer_ids:
            return True
        
        # Check if user is bot owner
        return user_id == self.bot.owner_id if hasattr(self.bot, 'owner_id') else False
    
    @app_commands.command(name='send', description='Send a preset message')
    @app_commands.describe(preset='The preset to send (e.g., CHRISTMAS)')
    async def send_slash(self, interaction: discord.Interaction, preset: str):
        """Send a preset message via slash command"""
        
        print(f"[SEND] Command received from user {interaction.user.id}")
        
        # Permission check
        if not self.is_developer(interaction.user.id):
            print(f"[SEND] Permission denied for user {interaction.user.id}")
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
            return
        
        print(f"[SEND] Permission check passed")
        
        preset_upper = preset.upper()
        
        if preset_upper not in self.presets:
            print(f"[SEND] Unknown preset: {preset_upper}")
            await interaction.response.send_message(
                f"❌ Unknown preset. Available presets: {', '.join(self.presets.keys())}", 
                ephemeral=True
            )
            return
        
        print(f"[SEND] Preset found: {preset_upper}")
        
        # Get the preset message data
        message_data = self.presets[preset_upper]
        
        # Get the target channel
        target_channel = self.bot.get_channel(1437234810585223258)
        
        if target_channel is None:
            print(f"[SEND] Target channel not found")
            await interaction.response.send_message("❌ Target channel not found.", ephemeral=True)
            return
        
        print(f"[SEND] Target channel found: {target_channel.name}")
        
        # Respond immediately to avoid timeout
        try:
            print(f"[SEND] Deferring response...")
            await interaction.response.defer(ephemeral=True)
            print(f"[SEND] Response deferred successfully")
        except Exception as e:
            print(f"[SEND] Failed to defer: {e}")
            return
        
        # Send the message to the target channel
        try:
            print(f"[SEND] Sending message to channel...")
            await target_channel.send(
                content=message_data["content"],
                embeds=message_data["embeds"]
            )
            print(f"[SEND] Message sent successfully")
            await interaction.followup.send(f"✅ Message sent to {target_channel.mention}", ephemeral=True)
            print(f"[SEND] Followup sent")
        except Exception as e:
            print(f"[SEND] Error sending message: {e}")
            await interaction.followup.send(f"❌ Failed to send message: {e}", ephemeral=True)
    
    @commands.command(name='send')
    async def send_prefix(self, ctx, preset: str = None):
        """Send a preset message. Usage: !send [PRESET_NAME]"""
        
        # Permission check for prefix command
        if not self.is_developer(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        if preset is None:
            await ctx.send(f"❌ Please specify a preset. Available presets: {', '.join(self.presets.keys())}")
            return
        
        preset_upper = preset.upper()
        
        if preset_upper not in self.presets:
            await ctx.send(f"❌ Unknown preset. Available presets: {', '.join(self.presets.keys())}")
            return
        
        # Get the preset message data
        message_data = self.presets[preset_upper]
        
        # Get the target channel
        target_channel = self.bot.get_channel(1433550974068330738)
        
        if target_channel is None:
            await ctx.send("❌ Target channel not found.")
            return
        
        # Send the message to the target channel
        try:
            await target_channel.send(
                content=message_data["content"],
                embeds=message_data["embeds"]
            )
            await ctx.send(f"✅ Message sent to {target_channel.mention}")
            # Delete the command message for cleanliness
            await ctx.message.delete()
        except Exception as e:
            await ctx.send(f"❌ Failed to send message: {e}")

async def setup(bot):
    await bot.add_cog(Send(bot))