FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY hf_space/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

COPY . /app

ENV Q14_OUTPUT_DIR=/tmp/q14_output
ENV Q16_WORK_ROOT=/tmp/q16_work
ENV Q19_WORK_ROOT=/tmp/q19_work
ENV Q10_CSV_PATH=/app/T22026/GA0/Q10/q-fastapi.csv
ENV CORS_ALLOW_ORIGINS=*

RUN mkdir -p /tmp/q14_output /tmp/q16_work /tmp/q19_work

EXPOSE 7860
CMD ["sh", "-c", "uvicorn hf_space.app:app --host 0.0.0.0 --port ${PORT:-7860}"]
