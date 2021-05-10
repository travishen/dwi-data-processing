FROM python:3-alpine

RUN apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

WORKDIR /src

COPY requirements.txt .

RUN python3 -m pip install six==1.16.0

RUN python3 -m pip install -r requirements.txt --no-cache-dir

COPY . .

ENTRYPOINT ["tail", "-f", "/dev/null"]
