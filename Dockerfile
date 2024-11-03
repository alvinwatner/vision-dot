FROM python:3.10-slim

WORKDIR  /app

ENV PROCESS_WITH=cpu
ENV PORT=5000

#RUN pip install poetry
#
#COPY pyproject.toml /app
#
#RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi --sync

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python3", "main.py"]