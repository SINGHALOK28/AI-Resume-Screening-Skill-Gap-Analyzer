# Dockerfile for Hugging Face Spaces
FROM python:3.11-slim

# Set up user and home directory
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set working directory
WORKDIR $HOME/app

# Install system dependencies (OCR, PDF processing, etc.)
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*
USER user

# Install Python dependencies (copied first for caching)
COPY --chown=user:user requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_md

# Copy app code
COPY --chown=user:user . .

# Hugging Face Spaces requires port 7860
EXPOSE 7860

# Set Streamlit config via environment variables
ENV STREAMLIT_SERVER_PORT=7860 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_ENABLECORS=false \
    STREAMLIT_SERVER_ENABLEXSRFPROTECTION=false \
    STREAMLIT_BROWSER_GATHERUSAGESTATS=false

# Run the app
CMD ["streamlit", "run", "app.py"]
