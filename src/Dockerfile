FROM python:3.13

RUN apt-get update && apt-get upgrade

# set work directory
WORKDIR /usr/app/src

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy project
COPY . .

WORKDIR /usr/app

# creating a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# change ownership of the directory and all its content to the non-root user
RUN chown -R appuser:appuser /usr/app

# switch to non-root user
USER appuser

EXPOSE 8000

CMD ["python", "-m", "src"]