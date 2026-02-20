FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/src \
    FLASK_APP=trafficgen.app \
    FLASK_DEBUG=0 \
    TRAFFICGEN_TLS_CERT_FILE=/tls/tls.crt \
    TRAFFICGEN_TLS_KEY_FILE=/tls/tls.key

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY data ./data

RUN pip install --upgrade pip \
    && pip install .

EXPOSE 5000

CMD ["sh", "-c", "if [ -f \"${TRAFFICGEN_TLS_CERT_FILE}\" ] && [ -f \"${TRAFFICGEN_TLS_KEY_FILE}\" ]; then exec flask run --host=0.0.0.0 --port=5000 --cert=\"${TRAFFICGEN_TLS_CERT_FILE}\" --key=\"${TRAFFICGEN_TLS_KEY_FILE}\"; else exec flask run --host=0.0.0.0 --port=5000; fi"]
