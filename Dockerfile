# Use the official Python image as the base image
FROM python:3.12

COPY ./requirements.txt /src/requirements.txt

# switch working directory
WORKDIR /src

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY . /src

EXPOSE 8080

WORKDIR .

CMD [ "python", "src/main.py" ]
