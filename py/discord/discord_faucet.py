import discord
from discord import app_commands
import asyncio
import json
from dotenv import load_dotenv
import os
import logging

load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#API 토큰 설정
API_TOKEN = os.getenv("DISCORD_FAUCET_API_TOKEN")

class FaucetBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        try:
            with open('claimed_users.json', 'r') as f:
                self.claimed_users = json.load(f)
        except FileNotFoundError:
            self.claimed_users = {}

    async def setup_hook(self):
        await self.tree.sync()

client = FaucetBot()

@client.tree.command(name="faucet", description="Claim 7 BERA tokens (once per user)")
async def faucet(interaction: discord.Interaction):
    # 봇의 권한 확인
    bot_permissions = interaction.channel.permissions_for(interaction.guild.me)
    if not bot_permissions.send_messages:
        await interaction.response.send_message("Bot doesn't have permission to send messages!", ephemeral=True)
        return

    user_id = str(interaction.user.id)
    if user_id in client.claimed_users:
        await interaction.response.send_message("You have already claimed your BERA tokens!", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    
    try:
        # 지연시간을 추가하여 메시지 전송
        await asyncio.sleep(1)
        tip_message = await interaction.channel.send(f"$tip {interaction.user.mention} 7 bera")
        
        # 명령어가 성공적으로 전송되었는지 확인
        await asyncio.sleep(2)
        
        # 사용자 기록 저장
        client.claimed_users[user_id] = True
        with open('claimed_users.json', 'w') as f:
            json.dump(client.claimed_users, f)
        
        await interaction.followup.send("Command has been sent. Please check if you received the BERA tokens.", ephemeral=True)
    
    except discord.Forbidden:
        await interaction.followup.send("Bot doesn't have proper permissions to execute this command.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

# 봇 토큰으로 실행
client.run(API_TOKEN)