FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /srv

COPY backend/pyproject.toml backend/pyproject.toml
COPY backend/app backend/app
COPY frontend frontend
RUN pip install --upgrade pip && pip install -e "backend[postgres]"

WORKDIR /srv/backend
RUN mkdir -p data && useradd -r -u 10001 bureau && chown -R bureau /srv
USER bureau
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/sante').status==200 else 1)"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
