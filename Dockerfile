FROM python:3.10-slim

WORKDIR  /dot_vision

ENV PROCESS_WITH=cpu
ENV PORT=5000
ENV PYTHONPATH=/dot_vision

RUN pip install poetry

COPY . /dot_vision

RUN poetry config virtualenvs.create false && poetry install --only main --no-interaction --no-ansi --no-root

# download the ultralytics CPU variant
RUN pip install ultralytics==8.2.100 --extra-index-url https://download.pytorch.org/whl/cpu

# downloading the libGL.so.1 library required by openCV
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

EXPOSE 5000

CMD ["python3", "app/main.py"]
