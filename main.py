# file:         main.py
# description:  contains the main implementation for the bot.
# author:       Hritik "Ricky" Gupta | hritikrg02@gmail.com

import asyncio
import discord

from typing import List, Tuple
from discord.ext import commands
from loguru import logger

from utils import get_token, create_ensemble_json

# constants

TOKEN_FILE = "token.txt"
TOKEN = get_token(TOKEN_FILE)

CALLABLE_ROLE = "Eboard"

# discord stuff

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='$', intents=intents)


@bot.event
async def on_ready():
    logger.success(f"Log on successful as {bot.user}.")

@bot.command(name="create")
async def create_embed(ctx: discord.ext.commands.Context):
    logger.info("create embed initiated")

    # if ctx.author.top_role.name != CALLABLE_ROLE:
    #     logger.warning(f"User {ctx.author} does not have role {CALLABLE_ROLE}.")
    #     return

    config = {}
    async def get_response(question: str, timeout: int = 60):
        await ctx.send(question)

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        response = await bot.wait_for('message', timeout=timeout, check=check)
        return response.content  # TODO some error handling

    config["song_title"] = await get_response("Enter song name:")
    config["game"] = await get_response("Enter game name:")

    musicians_needed = await get_response("Musicians needed (comma-separated): ")
    config["musicians_needed"] = [m.strip() for m in musicians_needed.split(",")]

    await ctx.send("Now let's add current musicians. Type 'done' when finished adding musicians.")
    current_musicians: List[Tuple[str, str]] = []
    while True:
        part = await get_response("Current musician part (or 'done' to finish): ")
        if part is None:
            return
        if part.lower() == 'done':
            break

        name = await get_response("Current musician name: ")
        if name is None:
            return

        current_musicians.append((part, name))

    config["current_musicians"] = current_musicians

    config["original_track"] = await get_response("Enter original track link: ")
    other_tracks = await get_response("Enter track track links (comma-separated, or type 'skip' to skip): ")
    if other_tracks.lower() != 'skip':
        config["other_tracks"] = [t.strip() for t in other_tracks.split(",")]

    config["user_id"] = str(ctx.author.name)

    config["thumbnail_url"] = await get_response("Enter URL for image included in embed: ")

    logger.info("info obtained successfully, creating embed JSON")
    json_str = create_ensemble_json(**config)
    await ctx.send(json_str)

bot.run(TOKEN)