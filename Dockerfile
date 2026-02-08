FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic
COPY src ./src
COPY main.py ./main.py

# Legacy workflow assets used by graph service adapter.
COPY graph_chat ./graph_chat
COPY tools ./tools
COPY order_faq.md ./order_faq.md
COPY travel_new.sqlite ./travel_new.sqlite
COPY travel2.sqlite ./travel2.sqlite

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

EXPOSE 8000

CMD ["python", "main.py"]
