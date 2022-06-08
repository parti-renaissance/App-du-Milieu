# ---- Base python ----
FROM python:3.10.5 AS base
# Create app directory
WORKDIR /app

# ---- Dependencies ----
FROM base AS dependencies
COPY requirements.txt ./
# install app dependencies
RUN pip install --upgrade pip \
    pip install -r requirements.txt

# ---- Copy Files/Build ----
FROM dependencies AS build
WORKDIR /app
COPY . /app

# --- Release with Slim ----
FROM python:3.10.5 AS release
# Create app directory
WORKDIR /app

COPY --from=dependencies /app/requirements.txt ./
COPY --from=dependencies /root/.cache /root/.cache

# Install app dependencies
RUN pip install --upgrade pip \
    pip install -r requirements.txt
COPY --from=build /app/ ./
CMD gunicorn --bind :$PORT --workers 4 --worker-class uvicorn.workers.UvicornWorker --threads 8 --timeout 0 main:app
