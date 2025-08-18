# Use the official Python devcontainer as base
FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Update system packages
RUN apt-get update && apt-get install -y \
    # Essential build tools
    build-essential \
    git \
    curl \
    wget \
    unzip \
    # Database clients
    postgresql-client \
    # System monitoring tools
    htop \
    tree \
    jq \
    # Network tools
    net-tools \
    netcat \
    iputils-ping \
    # Browser dependencies for Selenium
    wget \
    gnupg \
    software-properties-common \
    # Chrome dependencies
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    # Additional utilities
    vim \
    nano \
    less \
    file \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver via webdriver-manager (will be handled by Python dependencies)
# This ensures compatibility with the installed Chrome version

# Install Node.js for additional tooling
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs

# Install Docker Compose
RUN curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose

# Create workspace directory
RUN mkdir -p /workspaces/bar-directory-recon

# Set up Python environment
COPY requirements.txt requirements-dev.txt /tmp/
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r /tmp/requirements-dev.txt \
    && rm /tmp/requirements*.txt

# Install additional Python tools
RUN pip install \
    # Code quality tools
    bandit[toml] \
    safety \
    # Documentation tools
    mkdocs \
    mkdocs-material \
    # Additional development utilities
    ipython \
    jupyter \
    notebook \
    # Performance profiling
    py-spy \
    memory-profiler \
    # Security scanning
    semgrep

# Configure Git (will be overridden by user settings)
RUN git config --global init.defaultBranch main \
    && git config --global core.autocrlf input \
    && git config --global core.filemode false

# Create logs and cache directories
RUN mkdir -p /workspaces/bar-directory-recon/logs \
    && mkdir -p /workspaces/bar-directory-recon/.pytest_cache \
    && mkdir -p /home/vscode/.cache/pre-commit \
    && chown -R vscode:vscode /home/vscode/.cache

# Set up Chrome sandbox bypass for containerized environment
RUN echo '#!/bin/bash\nexec /usr/bin/google-chrome --no-sandbox --disable-dev-shm-usage "$@"' > /usr/local/bin/chrome-no-sandbox \
    && chmod +x /usr/local/bin/chrome-no-sandbox

# Create startup script for development environment
RUN echo '#!/bin/bash\n\
echo "🚀 Bar Directory Recon Development Environment"\n\
echo "Python: $(python --version)"\n\
echo "Chrome: $(google-chrome --version)"\n\
echo "Node.js: $(node --version)"\n\
echo "Docker Compose: $(docker-compose --version)"\n\
echo ""\n\
echo "📁 Workspace: /workspaces/bar-directory-recon"\n\
echo "🔧 Available tools: pytest, black, flake8, mypy, pre-commit"\n\
echo "🌐 Browser: Chrome (with --no-sandbox for container)"\n\
echo "📊 Monitoring: Prometheus (9090), Grafana (3000)"\n\
echo ""\n\
' > /usr/local/bin/dev-welcome && chmod +x /usr/local/bin/dev-welcome

# Set working directory
WORKDIR /workspaces/bar-directory-recon

# Switch to vscode user
USER vscode

# Set up shell environment
RUN echo 'export PYTHONPATH="/workspaces/bar-directory-recon/src:/workspaces/bar-directory-recon:$PYTHONPATH"' >> ~/.bashrc \
    && echo 'export CHROME_BIN="/usr/local/bin/chrome-no-sandbox"' >> ~/.bashrc \
    && echo 'alias ll="ls -la"' >> ~/.bashrc \
    && echo 'alias pytest-cov="pytest --cov=src --cov=universal_recon --cov-report=term-missing"' >> ~/.bashrc \
    && echo 'alias pytest-html="pytest --cov=src --cov=universal_recon --cov-report=html"' >> ~/.bashrc \
    && echo 'alias pre-commit-all="pre-commit run --all-files"' >> ~/.bashrc

# Create default directories with proper permissions
RUN mkdir -p ~/.local/share/code-server/logs \
    && mkdir -p ~/.vscode-server/extensions

# Default command
CMD ["/bin/bash"]
