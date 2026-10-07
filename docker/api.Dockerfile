# syntax=docker/dockerfile:1

FROM scratch AS source
ARG API_REV
ADD https://github.com/Nikita-Filonov/qa-automation-engineer-api-course.git#${API_REV} /src

FROM python:3.12-slim-bookworm
ARG API_REV
LABEL org.opencontainers.image.source="https://github.com/Nikita-Filonov/qa-automation-engineer-api-course" \
      org.opencontainers.image.revision="${API_REV}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
COPY --from=source /src/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --uid 10001 --create-home api

COPY --from=source --chown=api:api /src/ ./
COPY logging.json ./logging.json
RUN mkdir -p /app/data /app/storage && chown -R api:api /app/data /app/storage

USER api
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "logging.json"]
