FROM continuumio/miniconda3

COPY environment.yml .
RUN conda env create -f environment.yml

CMD ["conda", "run", "--no-capture-output", "-n", "sec-embeds", "python", "bot_root/main.py"]