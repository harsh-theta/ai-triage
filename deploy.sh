#!/bin/bash

# AI Triage Deployment Script - Proxy Mode Only
# Designed for demo.company.com/intelligent-triage/

ACTION=${1:-deploy}

case $ACTION in
  "deploy"|"start")
    echo "🚀 Deploying AI Triage for proxy access"
    echo "📍 Will be accessible at: demo.company.com/intelligent-triage/"
    echo ""
    
    # Stop any running containers
    docker-compose down
    
    # Build and start services
    docker-compose up --build -d
    
    echo ""
    echo "✅ Deployment complete!"
    echo "📱 Frontend: demo.company.com/intelligent-triage/"
    echo "🔧 Backend API: demo.company.com/intelligent-triage/"
    echo "📊 API Docs: demo.company.com/intelligent-triage/docs"
    echo ""
    echo "🔍 Check status: ./deploy.sh status"
    echo "📋 View logs: ./deploy.sh logs"
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
  "restart")
    echo "🔄 Restarting services..."
    docker-compose restart
    echo "✅ Services restarted"
    ;;
  *)
    echo "AI Triage Deployment Script"
    echo "Usage: $0 [deploy|stop|logs|status|restart]"
    echo ""
    echo "Commands:"
    echo "  deploy   - Deploy the application (default)"
    echo "  stop     - Stop all services"
    echo "  logs     - Show service logs"
    echo "  status   - Show service status"
    echo "  restart  - Restart all services"
    echo ""
    echo "Examples:"
    echo "  $0           # Deploy the application"
    echo "  $0 deploy    # Deploy the application"
    echo "  $0 stop      # Stop all services"
    echo "  $0 logs      # View logs"
    exit 1
    ;;
esac