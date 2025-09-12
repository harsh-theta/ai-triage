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

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create log directory and set permissions
RUN mkdir -p /var/log/nginx && \
    chmod -R 755 /usr/share/nginx/html && \
    chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/log/nginx

# Expose port
EXPOSE 80


# Start nginx
CMD ["nginx", "-g", "daemon off;"] 