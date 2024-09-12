import discord
from discord.ext import commands

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        await self.load_extension('ticket_modmail_cog')
        await self.tree.sync()
        print("Comandos sincronizados com sucesso!")

    async def on_ready(self):
        print(f'Bot logado como: {self.user.name} - ID: {self.user.id}')
        await bot.change_presence(activity=discord.CustomActivity(emoji="📩", name="Ajudando usuários!")) # Caso o emoji não funcione, coloque no nome, assim, mostrará o emoji.

bot = Bot()
bot.run('YOUR_TOKEN') # Substitua YOUR_TOKEN pelo token do seu Bot.