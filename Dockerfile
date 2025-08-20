FROM continuumio/miniconda3

COPY environment.yml .
RUN conda env create -f environment.yml

SHELL ["conda", "run", "-n", "sec-embeds", "/bin/bash", "-c"]

# sanity check
RUN echo "making sure discord is installed"
RUN python -c "import discord"

CMD ["conda", "run", "--no-capture-output", "-n", "sec-embeds", "python", "bot_root/main.py"]