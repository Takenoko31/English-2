FROM python:3.12-slim

WORKDIR /app
COPY . /app

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

EXPOSE 8080

CMD ["python", "app.py"]
