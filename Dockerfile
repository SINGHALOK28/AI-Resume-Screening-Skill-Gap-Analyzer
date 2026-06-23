FROM python:3.11-slim

# Create user for Hugging Face permissions (required)
RUN useradd -m -u 1000 user
USER user

# Set environment
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Install system dependencies
USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*
USER user

# Copy requirements first
COPY --chown=user requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_md

# Copy the rest of the application
COPY --chown=user . .

# Expose Hugging Face's default Docker port
EXPOSE 7860

# Healthcheck (updated to 7860)
HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health

# Run Streamlit on port 7860
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
