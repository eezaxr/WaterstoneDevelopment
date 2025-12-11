import discord
from discord.ext import commands
from discord import app_commands
from utilities.FirebaseHandler import firebase
from utilities.BloxlinkHandler import bloxlink


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="profile", description="View your student profile")
    async def profile(self, ctx):
        """Display your student profile"""
        
        target_user = ctx.author
        
        # Defer the response since we'll be making API calls
        await ctx.defer()
        
        # Get Roblox data from Bloxlink
        bloxlink_data = await bloxlink.get_user(str(target_user.id))
        
        # Default values
        roblox_username = "N/A"
        rank = "N/A"
        rank_number = 0
        account_status = "Not Linked"
        roleplay_name = "Not Set"
        roblox_id = None
        
        if bloxlink_data.get("success"):
            roblox_id = bloxlink_data.get("robloxID")
            
            # Get username from Bloxlink response
            resolved = bloxlink_data.get("resolved", {})
            roblox_username = resolved.get("roblox", {}).get("name", "N/A")
            
            # Get rank from Bloxlink and rank number
            group_data = await bloxlink.get_primary_group(str(target_user.id))
            if group_data:
                role = group_data.get("role", {})
                rank = role.get("name", "N/A")
                rank_number = role.get("rank", 0)
            
            # Get additional data from Firebase if Roblox ID exists
            if roblox_id:
                account_data = firebase.get(f'accounts/{roblox_id}')
                
                if account_data:
                    # Get account status
                    account_status = account_data.get('account_status', 'Active')
                    
                    # Check if blacklisted
                    if account_data.get('user_blacklisted', False):
                        account_status = "Blacklisted"
                    
                    # Get roleplay name
                    roleplay_name = account_data.get('roleplay_name', 'Not Set')
                else:
                    # Linked via Bloxlink but not in Firebase
                    account_status = "Linked"
        
        # Determine profile title based on rank
        profile_title = "Staff Profile" if rank_number >= 25 else "Student Profile"
        
        # Create embed with roleplay name in description
        embed = discord.Embed(
            title=profile_title,
            description=f"**Roleplay Name**\n```{roleplay_name}```",
            color=None
        )
        
        # Set thumbnail to user's avatar
        embed.set_thumbnail(url=target_user.display_avatar.url)
        
        # Add fields
        embed.add_field(
            name="Roblox Username",
            value=f"`{roblox_username}`",
            inline=True
        )
        
        embed.add_field(
            name="Discord Username",
            value=f"`{target_user.name}`",
            inline=True
        )
        
        embed.add_field(
            name="Rank",
            value=f"`{rank}`",
            inline=True
        )
        
        embed.add_field(
            name="Account Status",
            value=account_status,
            inline=True
        )
        
        embed.add_field(
            name="Negative Points",
            value="N/A",
            inline=True
        )
        
        embed.add_field(
            name="Positive Points",
            value="N/A",
            inline=True
        )
        
        # Send the embed
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Profile(bot))