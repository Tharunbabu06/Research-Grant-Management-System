FROM python:3.12-slim
WORKDIR /app
COPY requirements-lock.txt .
RUN pip install --no-cache-dir -r requirements-lock.txt
COPY . .
RUN useradd -m grant && mkdir -p /app/runtime && chown -R grant:grant /app
USER grant
EXPOSE 8000
CMD ["sh", "-c", "python scripts/setup_users.py && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"]
