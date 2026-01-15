# Multi-stage Docker build for Blender MCP
# Supports both development and production deployments

# =============================================================================
# Base stage with Python and Blender
# =============================================================================
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    bzip2 \
    libgl1-mesa-glx \
    libxi6 \
    libgconf-2-4 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Blender
RUN BLENDER_VERSION=3.6.5 \
    && wget -O blender.tar.xz "https://download.blender.org/release/Blender${BLENDER_VERSION:0:3}/blender-${BLENDER_VERSION}-linux-x64.tar.xz" \
    && tar -xf blender.tar.xz \
    && mv blender-${BLENDER_VERSION}-linux-x64 /opt/blender \
    && rm blender.tar.xz

# Add Blender to PATH
ENV PATH="/opt/blender:$PATH"
ENV BLENDER_PATH="/opt/blender/blender"

# Set working directory
WORKDIR /app

# =============================================================================
# Development stage
# =============================================================================
FROM base as development

# Copy Python project files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .[dev]

# Copy source code
COPY src/ ./src/

# Create non-root user
RUN useradd --create-home --shell /bin/bash mcp
USER mcp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import blender_mcp; print('OK')" || exit 1

# Default command
CMD ["python", "-m", "blender_mcp.cli", "--stdio"]

# =============================================================================
# Production stage
# =============================================================================
FROM base as production

# Copy Python project files
COPY pyproject.toml uv.lock ./

# Install only production dependencies
RUN pip install --no-cache-dir -e .

# Copy source code
COPY src/ ./src/

# Create non-root user
RUN useradd --create-home --shell /bin/bash mcp
USER mcp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import blender_mcp; print('OK')" || exit 1

# Default command for production
CMD ["python", "-m", "blender_mcp.cli", "--stdio"]

# =============================================================================
# Minimal runtime stage (for registry distribution)
# =============================================================================
FROM python:3.11-slim as runtime

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libxi6 \
    && rm -rf /var/lib/apt/lists/*

# Install Blender MCP from PyPI (when published)
# RUN pip install blender-mcp

# For now, copy from production stage
COPY --from=production /app /app
WORKDIR /app

# Create non-root user
RUN useradd --create-home --shell /bin/bash mcp
USER mcp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import blender_mcp; print('OK')" || exit 1

# Default command
CMD ["python", "-m", "blender_mcp.cli", "--stdio"]

# =============================================================================
# Build arguments and labels
# =============================================================================
ARG BUILD_DATE
ARG VERSION
ARG VCS_REF

LABEL org.opencontainers.image.created="$BUILD_DATE" \
      org.opencontainers.image.version="$VERSION" \
      org.opencontainers.image.revision="$VCS_REF" \
      org.opencontainers.image.title="Blender MCP" \
      org.opencontainers.image.description="AI-Powered 3D Creation MCP Server" \
      org.opencontainers.image.vendor="FlowEngineer sandraschi" \
      org.opencontainers.image.source="https://github.com/sandraschi/blender-mcp" \
      org.opencontainers.image.licenses="MIT"





