# Dockerfile for nitsuah/avatar - Jupyter Notebook application

# ================================
# Stage 1: Python Dependencies (for Jupyter Notebook)
# ================================
FROM python:3.11-slim AS python-deps
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ================================
# Stage 2: Node.js Dependencies (for any Node.js parts of the app)
# ================================
FROM node:20-alpine AS node-deps
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# ================================
# Stage 3: Builder (Node.js build if applicable)
# ================================
FROM node:20-alpine AS builder
WORKDIR /app

# Copy package files and install all dependencies (including devDependencies)
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build the application (if applicable)
RUN npm run build

# ================================
# Stage 4: Final Image
# ================================
FROM python:3.11-slim AS final

# Create non-root user
RUN groupadd --system appgroup && useradd --system --gid appgroup appuser

WORKDIR /app

# Copy Python dependencies
COPY --from=python-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-deps /usr/local/bin /usr/local/bin

# Copy Node.js dependencies (if applicable)
COPY --from=node-deps /app/node_modules ./node_modules

# Copy built Node.js assets (if applicable)
COPY --from=builder --chown=appuser:appgroup /app/.next ./.next
COPY --from=builder --chown=appuser:appgroup /app/public ./public
COPY --from=builder --chown=appuser:appgroup /app/package*.json ./


# Copy the rest of the application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose Jupyter Notebook port
EXPOSE 8888

# Set environment variables (example, adjust as needed)
ENV JUPYTER_ALLOW_ROOT=yes
ENV JUPYTER_PORT=8888
ENV JUPYTER_IP=0.0.0.0

# Health check (example, adjust based on your application)
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8888/ || exit 1

# Start Jupyter Notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--allow-root"]