#!/bin/bash

# Main deployment script with mode selection
MODE=${1:-proxy}

case $MODE in
  "proxy")
    echo "🌐 Deploying in PROXY mode (default)"
    ./deploy-proxy.sh
    ;;
  "direct")
    echo "🔗 Deploying in DIRECT mode"
    ./deploy-local.sh
    ;;
  "stop")
    echo "🛑 Stopping all services"
    docker-compose down
    echo "✅ All services stopped"
    ;;
  "logs")
    echo "📋 Showing logs..."
    docker-compose logs -f
    ;;
  "status")
    echo "🔍 Service status:"
    docker-compose ps
    ;;
  *)
    echo "Usage: $0 [proxy|direct|stop|logs|status]"
    echo ""
    echo "Modes:"
    echo "  proxy  - Deploy for proxy access (demo.company.com/intelligent-triage/) [DEFAULT]"
    echo "  direct - Deploy for direct access (IP:PORT)"
    echo "  stop   - Stop all services"
    echo "  logs   - Show service logs"
    echo "  status - Show service status"
    echo ""
    echo "Examples:"
    echo "  $0           # Deploy in proxy mode (default)"
    echo "  $0 proxy     # Deploy in proxy mode"
    echo "  $0 direct    # Deploy in direct mode"
    echo "  $0 stop      # Stop all services"
    exit 1
    ;;
esac