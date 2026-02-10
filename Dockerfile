# base image
FROM python:3.11-slim

# prevent python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# set working directory
WORKDIR /app

# install minimal system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# copy dependency definitions first (for caching)
COPY requirements.txt .

# install dependencies (use psycopg2-binary in requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# copy app code
COPY . .

# expose flask gunicorn port
EXPOSE 5000

# run app with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "main:app"]
