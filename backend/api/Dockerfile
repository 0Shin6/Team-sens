FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/

ENV DB_PATH=/data/teamsens.db
ENV PORT=3000

EXPOSE 3000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "3000"]

