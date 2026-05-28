# Multi-stage Docker build for Blender MCP (GHCR: ghcr.io/sandraschi/blender-mcp)
#
# Build:
#   docker build --target production -t ghcr.io/sandraschi/blender-mcp:local .
#
# Run HTTP MCP + metrics:
#   docker run --rm -p 10849:10849 -p 9091:9091 ghcr.io/sandraschi/blender-mcp:local

FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    bzip2 \
    libgl1 \
    libglib2.0-0 \
    libx11-6 \
    libxi6 \
    libxxf86vm1 \
    libxfixes3 \
    libxrender1 \
    libxkbcommon0 \
    libsm6 \
    libice6 \
    && rm -rf /var/lib/apt/lists/*

RUN BLENDER_VERSION=4.2.3 \
    && wget -q -O blender.tar.xz "https://download.blender.org/release/Blender4.2/blender-${BLENDER_VERSION}-linux-x64.tar.xz" \
    && tar -xf blender.tar.xz \
    && mv blender-${BLENDER_VERSION}-linux-x64 /opt/blender \
    && rm blender.tar.xz

ENV PATH="/opt/blender:${PATH}"
ENV BLENDER_EXECUTABLE="/opt/blender/blender"
ENV MCP_TRANSPORT=http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=10849
ENV PROMETHEUS_PORT=9091
ENV BLENDER_MCP_METRICS_ENABLED=true
ENV BLENDER_MCP_LOG_FORMAT=json

WORKDIR /app

FROM base AS production

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir -e ".[monitoring]"

RUN useradd --create-home --shell /bin/bash mcp \
    && mkdir -p /app/logs \
    && chown -R mcp:mcp /app

USER mcp

EXPOSE 10849 9091

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:10849/api/v1/health', timeout=5)"

CMD ["python", "-m", "blender_mcp.server"]

ARG BUILD_DATE
ARG VERSION
ARG VCS_REF

LABEL org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.title="Blender MCP" \
      org.opencontainers.image.description="AI-Powered 3D Creation MCP Server" \
      org.opencontainers.image.vendor="FlowEngineer sandraschi" \
      org.opencontainers.image.source="https://github.com/sandraschi/blender-mcp" \
      org.opencontainers.image.licenses="MIT"
