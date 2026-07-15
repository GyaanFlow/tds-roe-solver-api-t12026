FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install Node.js (needed for seedrandom bridge that matches exam grader)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY hf_space/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

COPY . /app

# Install seedrandom npm package for the Node.js bridge
RUN cd /app && npm install --omit=dev seedrandom

ENV Q14_OUTPUT_DIR=/tmp/q14_output
ENV Q16_WORK_ROOT=/tmp/q16_work
ENV Q19_WORK_ROOT=/tmp/q19_work
ENV Q10_CSV_PATH=/app/T22026/GA0/Q10/q-fastapi.csv
ENV CORS_ALLOW_ORIGINS=*

RUN mkdir -p /tmp/q14_output /tmp/q16_work /tmp/q19_work

EXPOSE 7860
CMD ["sh", "-c", "uvicorn hf_space.app:app --host 0.0.0.0 --port ${PORT:-7860}"]
