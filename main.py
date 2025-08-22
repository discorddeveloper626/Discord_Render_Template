import os
import threading
import time
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from dotenv import load_dotenv
import asyncio

from web import run_web

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("/"), intents=intents)

start_time = time.time()
command_usage = 0


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.loop.create_task(status_task())
    try:
        await bot.tree.sync()
        print("Commands synced globally.")
    except Exception as e:
        print(f"Sync error: {e}")


async def status_task():
    await bot.wait_until_ready()
    while not bot.is_closed():
        servers = len(bot.guilds)
        users = command_usage
        await bot.change_presence(
            activity=discord.Game(name=f"{servers} Servers | {users} Uses"),
            status=discord.Status.dnd,
        )
        await asyncio.sleep(5)

        ping = round(bot.latency * 1000)
        uptime_seconds = int(time.time() - start_time)
        m, s = divmod(uptime_seconds, 60)
        await bot.change_presence(
            activity=discord.Game(name=f"{ping} Ping | {m}m,{s}s"),
            status=discord.Status.dnd,
        )
        await asyncio.sleep(5)


@bot.tree.command(name="ping", description="ping")
async def ping(interaction: discord.Interaction):
    global command_usage
    command_usage += 1
    await interaction.response.send_message("pong")


@bot.tree.command(name="ban", description="ban a user")
@app_commands.describe(user="target user", reason="reason")
async def ban(interaction: discord.Interaction, user: discord.User, reason: str = "なし"):
    global command_usage
    command_usage += 1
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("権限がありません。", ephemeral=True)
        return
    member = interaction.guild.get_member(user.id)
    if member:
        await member.ban(reason=reason)
        await interaction.response.send_message(f"{user} をBANしました。理由: {reason}")
    else:
        await interaction.response.send_message("対象ユーザーが見つかりません。", ephemeral=True)


@bot.tree.command(name="kick", description="kick a user")
@app_commands.describe(user="target user", reason="reason")
async def kick(interaction: discord.Interaction, user: discord.User, reason: str = "なし"):
    global command_usage
    command_usage += 1
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("権限がありません。", ephemeral=True)
        return
    member = interaction.guild.get_member(user.id)
    if member:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"{user} をKickしました。理由: {reason}")
    else:
        await interaction.response.send_message("対象ユーザーが見つかりません。", ephemeral=True)


@bot.tree.command(name="serverinfo", description="show server info")
async def serverinfo(interaction: discord.Interaction):
    global command_usage
    command_usage += 1
    g = interaction.guild
    embed = discord.Embed(title=f"{g.name} の情報", color=discord.Color.blue())
    embed.add_field(name="サーバーID", value=g.id, inline=False)
    embed.add_field(name="メンバー数", value=g.member_count, inline=False)
    embed.add_field(name="オーナー", value=g.owner, inline=False)
    embed.add_field(
        name="作成日", value=g.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="userinfo", description="show user info")
@app_commands.describe(user="target user")
async def userinfo(interaction: discord.Interaction, user: discord.User):
    global command_usage
    command_usage += 1
    embed = discord.Embed(title=f"{user.name} の情報", color=discord.Color.green())
    embed.add_field(name="ユーザーID", value=user.id, inline=False)
    embed.add_field(name="タグ", value=user.discriminator, inline=False)
    embed.add_field(name="Bot?", value=user.bot, inline=False)
    embed.set_thumbnail(url=user.display_avatar.url)
    await interaction.response.send_message(embed=embed)


if __name__ == "__main__":
    t = threading.Thread(target=run_web, daemon=True)
    t.start()
    bot.run(TOKEN)