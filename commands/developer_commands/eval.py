import discord
from discord.ext import commands
from discord import app_commands
import traceback
import io
import contextlib
import textwrap
from typing import Optional


class Eval(commands.Cog):
    """Developer eval command for executing Python code"""
    
    def __init__(self, bot):
        self.bot = bot
        # Add any developer IDs here for permission checking
        self.developer_ids = [790869950076157983]  # Add your Discord IDs: [123456789, 987654321]
    
    def is_developer(self, user_id: int) -> bool:
        """Check if user is a developer"""
        # Option 1: Check against list of developer IDs
        if self.developer_ids and user_id in self.developer_ids:
            return True
        
        # Option 2: Check if user is bot owner
        return user_id == self.bot.owner_id if hasattr(self.bot, 'owner_id') else False
    
    @app_commands.command(name="eval", description="Execute Python code")
    @app_commands.describe(code="The Python code to execute")
    async def eval_command(self, interaction: discord.Interaction, code: str):
        """
        Execute Python code dynamically
        
        Args:
            interaction: Discord interaction
            code: Python code to execute
        """
        # Permission check
        if not self.is_developer(interaction.user.id):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        # Clean code formatting (remove code blocks if present)
        code = code.strip()
        if code.startswith('```') and code.endswith('```'):
            code = code[3:-3]
            if code.startswith('python') or code.startswith('py'):
                code = '\n'.join(code.split('\n')[1:])
        
        # Setup environment for eval
        env = {
            'bot': self.bot,
            'discord': discord,
            'commands': commands,
            'interaction': interaction,
            'guild': interaction.guild,
            'channel': interaction.channel,
            'user': interaction.user,
            'message': interaction.message if hasattr(interaction, 'message') else None,
        }
        
        # Add all imported modules to environment
        env.update(globals())
        
        # Capture stdout
        stdout = io.StringIO()
        
        try:
            # Wrap code in async function for await support
            to_compile = f'async def func():\n{textwrap.indent(code, "  ")}'
            
            # Compile the code
            exec(to_compile, env)
            
            # Execute and capture output
            func = env['func']
            with contextlib.redirect_stdout(stdout):
                result = await func()
            
            # Get output
            output = stdout.getvalue()
            
            # Build response
            response = ""
            
            if output:
                response += f"**Output:**\n```\n{output}\n```\n"
            
            if result is not None:
                response += f"**Return Value:**\n```py\n{repr(result)}\n```"
            
            if not response:
                response = "✅ Code executed successfully with no output."
            
            # Split response if too long
            if len(response) > 2000:
                # Send first part
                await interaction.followup.send(response[:2000])
                # Send remaining parts
                for i in range(2000, len(response), 2000):
                    await interaction.followup.send(response[i:i+2000])
            else:
                await interaction.followup.send(response)
                
        except Exception as e:
            # Get full traceback
            error_trace = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            
            # Format error message
            error_msg = f"**Error:**\n```py\n{error_trace}\n```"
            
            # Truncate if too long
            if len(error_msg) > 2000:
                error_msg = error_msg[:1997] + "...```"
            
            await interaction.followup.send(error_msg)


async def setup(bot):
    """Add cog to bot"""
    await bot.add_cog(Eval(bot))