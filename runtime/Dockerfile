FROM python:3.13-slim-bookworm@sha256:a1165e272e578941b84abc79e4ab38a0305cd12803a5c4247979ac7655f4d641
LABEL org.opencontainers.image.title="Assignment 2 PostgreSQL setup"
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/runtime \
    TZ=UTC HOME=/tmp
WORKDIR /runtime
COPY requirements.lock /opt/a2/requirements.lock
# Build installs intentionally run as root into the immutable system environment.
# The final runtime and public Compose tools execute as a nonroot user.
RUN python -m pip install --root-user-action=ignore --no-cache-dir --only-binary=:all: --require-hashes -r /opt/a2/requirements.lock
COPY a2lab /runtime/a2lab
COPY sql /runtime/sql
USER 1000:1000
ENTRYPOINT ["python", "-m", "a2lab"]
