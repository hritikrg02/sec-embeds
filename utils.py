# file:         utils.py
# description:  contains utility functions used by the bot.
# author:       Hritik "Ricky" Gupta | hritikrg02@gmail.com

import json
from typing import List, Optional

from loguru import logger


def get_token(token_file):
    logger.info("Initiating token get.")
    try:
        with open(token_file, "r") as f:
            token = f.read().rstrip()

    except Exception:  # yes ik this is too broad, no I don't care enough to fix it
        logger.error("Issue when reading token file.")
        return

    logger.success("Token successfully parsed.")
    return token

# this func can be deleted, it was mostly a POC iirc
def create_ensemble_json(
    song_title: str,
    game: str,
    musicians_needed: List[str],
    current_musicians: List[tuple[str, str]],
    original_track: str,
    other_tracks: Optional[List[str]] = None,
    thumbnail_url: str = "https://png.pngtree.com/png-clipart/20210129/ourmid/pngtree-default-male-avatar-png-image_2811083.jpg",
    user_id: str = "userID",
) -> str:

    current_musicians_text = "\n".join(
        f"- {part}: {name}" for part, name in current_musicians
    )
    musicians_needed_text = "\n".join(
        f"- {part}: **_NEEDED_**" for part in musicians_needed
    )

    # only add newline between sections if both exist
    musicians_text = current_musicians_text
    if current_musicians_text and musicians_needed_text:
        musicians_text += "\n"
    musicians_text += musicians_needed_text

    tracks_text = f"\n- Original: {original_track}"
    if other_tracks:
        tracks_text += "\n- " + "\n- ".join(other_tracks)

    embed_dict = {
        "fields": [
            {"name": "Musicians", "value": musicians_text, "inline": False},
            {"name": "Tracks", "value": tracks_text, "inline": False},
        ],
        "title": f"{song_title} ~ {game}",
        "thumbnail": {"url": thumbnail_url},
        "author": {"name": "Small Ensemble"},
        "description": f"Run by @{user_id}",
        "color": 16733952,
    }

    return json.dumps(embed_dict, indent=4)
