FROM python:3.12-bullseye

# Set the working directory in the container
WORKDIR /

# Copy the dependencies file to the working directory
#COPY ./requirements.txt ./requirements.txt
COPY . .

#ENV PATH="/py/bin:$PATH"
# allows for more space in the container
ENV PYTHONDONTWRITEBYTECODE 1
# have Python output directly to terminal
ENV PYTHONUNBUFFERED 1


RUN python3 -m pip install --upgrade pip setuptools
RUN pip install -r requirements.txt
RUN python manage.py collectstatic --noinput

#COPY . .

CMD exec gunicorn --bind 0.0.0.0:$PORT kp.wsgi:application

