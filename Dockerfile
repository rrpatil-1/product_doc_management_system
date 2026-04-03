FROM python:3.12-slim

# Install UV
# COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy dependency files
# COPY pyproject.toml uv.lock ./
COPY requirements.txt ./
# Install dependencies
# RUN uv sync --frozen --no-install-project
RUN pip install --no-cache-dir -r requirements.txt
# COPY .env ./
COPY app /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]