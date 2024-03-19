FROM python:3.12-bullseye

# Set the working directory in the container
WORKDIR /

# Copy the dependencies file to the working directory
# the chown is needed for Docker Watch
COPY --chown=root:root . .

# allows for more space in the container
ENV PYTHONDONTWRITEBYTECODE 1
# have Python output directly to terminal
ENV PYTHONUNBUFFERED 1


RUN python3 -m pip install --upgrade pip setuptools
RUN pip install -r requirements.txt

# Gunicorn as app server
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 kp.wsgi:application

