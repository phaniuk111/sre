FROM python:3.12-slim
RUN pip install --no-cache-dir prometheus_client==0.21.1
WORKDIR /app
COPY shop.py loadgen.py ./
ENV PYTHONUNBUFFERED=1
