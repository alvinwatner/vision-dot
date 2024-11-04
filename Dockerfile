FROM python:3.10-slim

WORKDIR  /dot-vision

ENV PROCESS_WITH=cpu
ENV PORT=5000

RUN pip install poetry

COPY pyproject.toml /dot-vision

RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

# install cpu version of ultralytics
RUN poetry run postinstall

COPY . /dot-vision

#RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python3", "main.py"]