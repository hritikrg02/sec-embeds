# file:         main.py
# description:  contains the main implementation for the bot.
# author:       Hritik "Ricky" Gupta | hritikrg02@gmail.com

import discord

from typing import List, Tuple
from discord.ext import commands
from loguru import logger

from utils import get_token

# constants

TOKEN_FILE = "bot_root/token.txt"
TOKEN = get_token(TOKEN_FILE)

CALLABLE_ROLE = "Eboard"
CHANNEL_TO_SEND = 1343293435901251624

# discord stuff

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="$", intents=intents)


@bot.event
async def on_ready():
    logger.success(f"Log on successful as {bot.user}.")


@bot.command(name="create")
async def create_embed(ctx: discord.ext.commands.Context):
    logger.info("create embed initiated")

    # comment out for testing so you don't have to deal with role nonsense
    if ctx.author.top_role.name != CALLABLE_ROLE:
        logger.warning(f"User {ctx.author} does not have role {CALLABLE_ROLE}.")
        return

    config = {}

    async def get_response(question: str, timeout: int = 60):
        await ctx.send(question)

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        response = await bot.wait_for("message", timeout=timeout, check=check)
        return response.content  # TODO some error handling

    try:
        config["song_title"] = await get_response("Enter song name:")
        config["game"] = await get_response("Enter game name:")

        config["musicians_needed"] = []
        musicians_needed = await get_response(
            "Musicians needed, i.e that musicians you don't have yet (comma-separated, or type skip): "
        )
        if musicians_needed.lower() != "skip":
            config["musicians_needed"] = [
                m.strip() for m in musicians_needed.split(",")
            ]

        await ctx.send(
            "Now let's add current musicians. Type 'done' when finished adding musicians."
        )
        current_musicians: List[Tuple[str, str]] = []
        while True:
            part = await get_response("Current musician part (or 'done' to finish): ")
            if part is None:
                return
            if part.lower() == "done":
                break

            name = await get_response("Current musician name: ")
            if name is None:
                return

            current_musicians.append((part, name))

        config["current_musicians"] = current_musicians

        config["original_track"] = await get_response(
            "Enter OST link(s) (comma-separated if there are multiple): "
        )
        config["other_tracks"] = []
        other_tracks = await get_response(
            "Enter extra track links (comma-separated, or type 'skip' to skip): "
        )
        if other_tracks.lower() != "skip":
            config["other_tracks"] = [t.strip() for t in other_tracks.split(",")]

        config["user_id"] = await get_response(
            "Enter the username of the person running the ensemble, or type 'use mine' to use the username of the person filling out the details currently: "
        )
        if config["user_id"] == "use mine":
            config["user_id"] = str(ctx.author.name)

        config["thumbnail_url"] = await get_response(
            "Enter URL for image included in embed: "
        )

        logger.info("info obtained successfully, creating embed")

        # format embed info
        current_musicians_text = "\n".join(
            f"- {part}: {name}" for part, name in config["current_musicians"]
        )
        musicians_needed_text = "\n".join(
            f"- {part}: **_NEEDED_**" for part in config["musicians_needed"]
        )
        # only add newline between sections if both exist
        musicians_text = current_musicians_text
        if current_musicians_text and musicians_needed_text:
            musicians_text += "\n"
        musicians_text += musicians_needed_text

        tracks_text = f'\n- Original(s): {config["original_track"]}'
        if config["other_tracks"]:
            tracks_text += "\n- " + "\n- ".join(other_tracks)

        # generate embed

        embed = discord.Embed(
            title=f'{config["song_title"]} ~ {config["game"]}',
            color=discord.Color(16733952),
        )
        embed.add_field(name="Musicians", value=musicians_text, inline=False)
        embed.add_field(name="Tracks", value=tracks_text, inline=False)
        embed.set_thumbnail(url=config["thumbnail_url"])
        embed.set_author(name="Small Ensemble")
        embed.description = f'Run by @{config["user_id"]}'
        logger.info("embed created successfully")

        logger.info("sending embed")
        channel = bot.get_channel(CHANNEL_TO_SEND)
        await channel.send(embed=embed)
        logger.info("embed sent successfully")

    except Exception:  # TODO wayyy too broad
        logger.error("error encountered while making embed")
        logger.exception("")


bot.run(TOKEN)
