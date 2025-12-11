import discord
from discord.ext import commands
import random
import json
import os

class BotInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.random_facts = self.load_random_facts()
    
    def load_random_facts(self):
        """Load random facts from the JSON file"""
        try:
            # Get the path to the random_facts.json file
            # Assuming it's in the root directory or a data folder
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            facts_path = os.path.join(base_path, 'random_facts.json')
            
            # Try alternate locations if not found
            if not os.path.exists(facts_path):
                facts_path = os.path.join(base_path, 'data', 'random_facts.json')
            
            if not os.path.exists(facts_path):
                facts_path = 'random_facts.json'
            
            with open(facts_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [fact['fact'] for fact in data['fun_facts']]
        except Exception as e:
            print(f"Error loading random facts: {e}")
            # Fallback facts if JSON file can't be loaded
            return [
                "A group of flamingos is called a 'flamboyance'.",
                "Octopuses have three hearts.",
                "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are still edible."
            ]
    
    @commands.hybrid_command(name="botinfo", description="Display information about the Waterstone Bot")
    async def botinfo(self, ctx):
        """Shows detailed information about the bot"""
        
        # Get a random fact
        random_fact = random.choice(self.random_facts)
        
        # Create the embed
        embed = discord.Embed(
            title="Bot Information",
            description="All information linking to the Waterstone Bot is listed below this message. Information & data may change at any time.",
            color=None  # No color specified (default)
        )
        
        # Add fields
        embed.add_field(
            name="Waterstone Developers",
            value="<:eezaxrLight:1439334829861634256> [@eezaxr](https://x.com/eezaxr)",
            inline=True
        )
        
        embed.add_field(
            name="Waterstone Server Location",
            value="[Frankfurt, Germany](https://cloud.google.com/about/locations)",
            inline=True
        )
        
        embed.add_field(
            name="Random Fact",
            value=f"```{random_fact}```",
            inline=False
        )
        
        # Send the embed
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BotInfo(bot))