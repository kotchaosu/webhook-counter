FROM python:3.9.4-alpine3.13

WORKDIR /app
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

# explicitly set user/group IDs
RUN addgroup --gid 1000 \
      whcounter && \
    adduser --ingroup whcounter \
      --uid 1000 \
      --disabled-password \
      --home /app \
      whcounter && \
    apk upgrade --update && \
    apk add build-base \
      openssl-dev \
      libffi-dev && \
    pip install --upgrade pip

COPY requirements.txt ./
RUN pip install -r /app/requirements.txt
RUN apk del build-base
COPY . .
CMD ./entrypoint.sh
