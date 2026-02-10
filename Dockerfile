# base image
FROM python:3.11-slim

# prevent python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# set working directory
WORKDIR /app

# install system dependencies for psycopg2 and Gunicorn
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# copy dependency definitions first (for caching)
COPY requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy app code
COPY . .

# expose flask gunicorn port
EXPOSE 5000

# run app with gunicorn
# --bind 0.0.0.0:5000 make it accessible outside the container
# --workers 3
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "app:app"]
