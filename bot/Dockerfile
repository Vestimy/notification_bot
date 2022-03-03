FROM python:3.9.7

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app/

COPY . /usr/src/app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENV TZ Europe/Moscow

#RUN ["python", "bot.py"]
#ENTRYPOINT ["python", "bot.py"]