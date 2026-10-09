# CF Practice Coach: Streamlit app in a container.
#   docker build -t cf-coach .
#   docker run --rm -p 8501:8501 cf-coach                       # rule-based coach notes
#   docker run --rm -p 8501:8501 -e GROQ_API_KEY=... cf-coach   # with a hosted model
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    FASTEMBED_CACHE_PATH=/opt/fastembed

# Run as an unprivileged user, never as root.
RUN useradd --create-home --uid 1000 app
WORKDIR /app
RUN chown app:app /app

# Dependencies first, in their own layer: rebuilt only when requirements.txt changes,
# not on every code edit.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Bake the embedding model into the image so the first request needs no download.
RUN python -c "from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5')" \
    && chmod -R a+rX /opt/fastembed

COPY --chown=app:app . .
USER app

EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"

# 0.0.0.0: listen on all interfaces, or the app is unreachable from outside the container.
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", \
     "--server.headless=true", "--browser.gatherUsageStats=false"]
