FROM python:3.12-slim

WORKDIR /app

# Install uv

RUN pip install uv

# Copy dependency files

COPY pyproject.toml uv.lock ./

# Install dependencies

RUN uv sync

# Copy project files

COPY backend ./backend
COPY scripts ./scripts

# Generate demo data

RUN uv run python ./scripts/generate_demo_data.py || true

# Expose FastAPI port

EXPOSE 8000

# Start FastAPI app

CMD ["uv", "run", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]