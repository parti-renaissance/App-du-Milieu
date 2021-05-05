# Use the official lightweight Python image.
# https://hub.docker.com/_/python

FROM python:3.9
#-alpine

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Upgrade Linux packages
RUN apt-get -y update && apt-get -y dist-upgrade && apt-get -y autoremove && apt-get -y autoclean
# Upgrade pip itself
RUN pip install --upgrade pip
# Upgrade to latests python packages
RUN pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U
# Install dependencies
RUN pip install -r requirements.txt

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers 4 --worker-class uvicorn.workers.UvicornWorker  --threads 8 --timeout 0 main:app
