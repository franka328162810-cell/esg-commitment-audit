FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_RETRIES=10

WORKDIR /app

COPY container-requirements.lock /tmp/
RUN pip install --no-cache-dir --prefer-binary --timeout 120 --retries 10 \
    -r /tmp/container-requirements.lock

COPY container-dist/esg_commitment_audit-*.whl /tmp/
RUN pip install --no-cache-dir --no-deps /tmp/esg_commitment_audit-*.whl

COPY container_api.py /app/container_api.py

RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

CMD ["uvicorn", "container_api:app", "--host", "0.0.0.0", "--port", "8080"]
