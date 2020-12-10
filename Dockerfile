FROM python:3.8
WORKDIR /opt
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
COPY ./src /opt/app
WORKDIR /opt/app
CMD ["python", "main.py"]