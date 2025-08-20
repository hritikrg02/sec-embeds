###### Author: Hritik "Ricky" Gupta | hritikrg02@gmail.com
### Purpose
This bot was created in order to streamline the creation of RIT GSO's SEC embeds.
### Info
The main file assumes:
- It is being run from the repo root (i.e. `sec-embeds`).
- There is a file called `token.txt` present under `bot_root`.

When the bot is run, the 'Eboard' role can call `$create` which prompts the bot to initialize an interactive creation wizard, which when followed, leads to the creation of an embed within a channel. The channel is determined via whatever channel id `CHANNEL_TO_SEND` is set to. 
### Usage
The bot may be either run via docker compose or locally.
#### Docker Compose
Assuming you have the latest version of docker installed, you can run `docker compose up -d --build` from the `sec-embeds` directory.
#### Local
Assuming you have some form of conda installed, use the `environment.yml` file ti create a new environment. Once this is done, run `conda activate sec-embeds` followed by `python bot_root/main.py` from the `sec-embeds` directory.