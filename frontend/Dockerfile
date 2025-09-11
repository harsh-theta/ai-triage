# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps

# Copy source code
COPY . ./

# Build the application
RUN npm run build

# Production nginx stage
FROM nginx:alpine

# Install wget for health checks
RUN apk add --no-cache wget

# Set working directory
WORKDIR /usr/share/nginx/html

# Copy built application from builder stage
COPY --from=builder /app/out .

# Copy optimized nginx configuration
COPY nginx-optimized.conf /etc/nginx/nginx.conf

# Create log directory and set permissions
RUN mkdir -p /var/log/nginx && \
    chmod -R 755 /usr/share/nginx/html && \
    chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/log/nginx

# Create nginx cache directory
RUN mkdir -p /var/cache/nginx && \
    chown -R nginx:nginx /var/cache/nginx

# Expose port
EXPOSE 80

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 