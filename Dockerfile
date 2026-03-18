FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    EWA_INTERACTIVE=false

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ewa.py main.py readme.md ./

EXPOSE 502

CMD ["python", "main.py"]
