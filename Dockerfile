FROM python:3.11 as builder

WORKDIR /usr/src

VOLUME /usr/src/db.sqlite3

COPY requirements.txt ./

RUN pip3 install --upgrade pip \
    && pip install --no-cache-dir --no-deps --wheel-dir /usr/src/wheels -r requirements.txt \
    && pip install gunicorn psycopg2>=2.7,<2.8 --no-binary psycopg2 \
    && chmod +x entrypoint.sh

COPY . .


FROM python:3.11-alpine

COPY --from=builder /usr/src /usr/src

ENTRYPOINT ["./entrypoint.sh"]
