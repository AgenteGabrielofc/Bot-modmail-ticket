import discord
from discord import app_commands
from discord.ext import commands
import asyncio

class TicketModmailCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class TicketView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="Fechar Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
        async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            await interaction.channel.set_permissions(interaction.user, send_messages=False, read_messages=True)
            await interaction.followup.send("Ticket fechado. Este canal será deletado em 5 segundos.")
            await asyncio.sleep(5)
            await interaction.channel.delete()

    @app_commands.command(name="abrir_ticket", description="Abre um novo ticket")
    async def abrir_ticket(self, interaction: discord.Interaction):
        existing_ticket = discord.utils.get(interaction.guild.channels, name=f'ticket-{interaction.user.id}')
        if existing_ticket:
            await interaction.response.send_message("Você já tem um ticket aberto!", ephemeral=True)
            return

        ticket_category = discord.utils.get(interaction.guild.categories, name="Tickets")
        if ticket_category is None:
            ticket_category = await interaction.guild.create_category("Tickets")

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
        channel = await interaction.guild.create_text_channel(
            f'ticket-{interaction.user.id}',
            category=ticket_category,
            overwrites=overwrites
        )
        await interaction.response.send_message(f"Ticket criado! Por favor, vá para {channel.mention}", ephemeral=True)
        embed = discord.Embed(
            title="Novo Ticket",
            description=f"Ticket aberto por {interaction.user.mention}",
            color=discord.Color.blue()
        )
        view = self.TicketView()
        await channel.send(embed=embed, view=view)

    @app_commands.command(name="fechar_ticket", description="Fecha o ticket atual")
    async def fechar_ticket(self, interaction: discord.Interaction):
        if not interaction.channel.name.startswith('ticket-'):
            await interaction.response.send_message("Este comando só pode ser usado em canais de ticket!", ephemeral=True)
            return
        await interaction.response.defer()
        await interaction.channel.set_permissions(interaction.user, send_messages=False, read_messages=True)
        await interaction.followup.send("Ticket fechado. Este canal será deletado em 5 segundos.")
        await asyncio.sleep(5)
        await interaction.channel.delete()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if isinstance(message.channel, discord.DMChannel):
            guild = self.bot.get_guild(YOUR_GUILD_ID)  # Troque YOUR_GUILD_ID pelo o ID do seu Servidor.
            category = discord.utils.get(guild.categories, name="Modmail")
            if not category:
                category = await guild.create_category("Modmail")

            channel_name = f"modmail-{message.author.id}"
            channel = discord.utils.get(category.channels, name=channel_name)

            if not channel:
                staff_role = discord.utils.get(guild.roles, name="Staff")  # Troque "Staff" pelo o nome do cargo que o administrador poderá conversar como usuário.
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    staff_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
                channel = await category.create_text_channel(channel_name, overwrites=overwrites)
                await channel.send(f"Nova mensagem de {message.author.name}#{message.author.discriminator} (ID: {message.author.id})")

                welcome_embed = discord.Embed(
                    title="Sistema de ModMail",
                    description="**[PT]** - Agradeço por entrar em contato com a equipe de suporte da SEU_SERVIDOR Aguarde o suporte para responder você.", # troque SEU_SERVIDOR pelo nome do seu Servidor que irá usar o Bot.
                    color=discord.Color.blue()
                )
                await message.author.send(embed=welcome_embed)

            embed = discord.Embed(description=message.content, color=discord.Color.blue())
            embed.set_author(name=f"{message.author.name}#{message.author.discriminator}", icon_url=message.author.avatar.url if message.author.avatar else None)
            await channel.send(embed=embed)

            if message.attachments:
                for attachment in message.attachments:
                    await channel.send(attachment.url)

            await message.add_reaction("✅")

    @app_commands.command(name="reply", description="Responde a uma mensagem do Modmail")
    @app_commands.describe(user_id="ID do usuário para responder", message="Mensagem para enviar")
    async def reply(self, interaction: discord.Interaction, user_id: str, message: str):
        if not interaction.channel.name.startswith("modmail-"):
            await interaction.response.send_message("Este comando só pode ser usado em canais de Modmail!", ephemeral=True)
            return

        user = await self.bot.fetch_user(int(user_id))
        if not user:
            await interaction.response.send_message("Usuário não encontrado.", ephemeral=True)
            return

        try:
            await user.send(f"**Resposta da Staff:** {message}")
            await interaction.response.send_message(f"Mensagem enviada para {user.name}#{user.discriminator}.")
        except discord.errors.Forbidden:
            await interaction.response.send_message("Não foi possível enviar a mensagem para o usuário. As DMs podem estar fechadas.", ephemeral=True)

    @app_commands.command(name="close_modmail", description="Fecha um canal de Modmail")
    async def close_modmail(self, interaction: discord.Interaction):
        if not interaction.channel.name.startswith("modmail-"):
            await interaction.response.send_message("Este comando só pode ser usado em canais de Modmail!", ephemeral=True)
            return

        user_id = interaction.channel.name.split("-")[1]
        user = await self.bot.fetch_user(int(user_id))
        if user:
            try:
                await user.send("Seu ticket de Modmail foi fechado pela Staff.")
            except discord.errors.Forbidden:
                pass

        await interaction.response.send_message("Fechando o canal de Modmail em 5 segundos...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

async def setup(bot):
    await bot.add_cog(TicketModmailCog(bot))