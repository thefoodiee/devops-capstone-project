#!/usr/bin/env bash
# ==============================================================================
# Cloud-Native Notes Application - Master Start Script
# DevOps & Automation Lab (ENSP461) Capstone Project
# "one script to start everything"
# ==============================================================================

set -e

# Color definitions
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

print_banner() {
    echo -e "${CYAN}${BOLD}"
    echo "======================================================================"
    echo "       CLOUD-NATIVE NOTES APPLICATION - DEVOPS CAPSTONE PIPELINE      "
    echo "          DevOps & Automation Lab (ENSP461) | B.Tech CSE Sem VII     "
    echo "======================================================================"
    echo -e "${NC}"
}

print_help() {
    echo "Usage: ./start.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --docker       Start the complete cloud-native stack with Docker Compose (Default)"
    echo "  --local        Start lightweight local instance using Python virtualenv & SQLite"
    echo "  --build        Rebuild Docker images before starting"
    echo "  --help         Show this help message"
}

MODE="docker"
REBUILD=""

for arg in "$@"; do
    case "$arg" in
        --local)
            MODE="local"
            ;;
        --docker)
            MODE="docker"
            ;;
        --build)
            REBUILD="--build"
            ;;
        --help|-h)
            print_help
            exit 0
            ;;
    esac
done

print_banner

# Helper to detect docker compose command
get_compose_cmd() {
    if docker compose version >/dev/null 2>&1; then
        echo "docker compose"
    elif docker-compose version >/dev/null 2>&1; then
        echo "docker-compose"
    else
        echo ""
    fi
}

start_docker() {
    COMPOSE_CMD=$(get_compose_cmd)
    if [ -z "$COMPOSE_CMD" ]; then
        echo -e "${YELLOW}[WARNING] Docker Compose not found. Falling back to local mode...${NC}"
        start_local
        return
    fi

    echo -e "${BLUE}[1/4] Checking Docker daemon status...${NC}"
    if ! docker info >/dev/null 2>&1; then
        echo -e "${YELLOW}[WARNING] Docker daemon is not accessible. Falling back to local mode...${NC}"
        start_local
        return
    fi

    echo -e "${BLUE}[2/4] Starting Cloud-Native Stack (App, PostgreSQL, Prometheus, Grafana)...${NC}"
    $COMPOSE_CMD up -d $REBUILD

    echo -e "${BLUE}[3/4] Waiting for Notes Application health check (http://localhost:5000/api/health)...${NC}"
    max_retries=30
    count=0
    until curl -s -f http://localhost:5000/api/health >/dev/null 2>&1; do
        count=$((count+1))
        if [ $count -gt $max_retries ]; then
            echo -e "${RED}[ERROR] Notes App did not become healthy within 60 seconds.${NC}"
            echo "Checking container logs:"
            $COMPOSE_CMD logs --tail 20 notes_app
            exit 1
        fi
        printf "."
        sleep 2
    done
    echo ""
    echo -e "${GREEN}[SUCCESS] Notes Application is healthy and responsive!${NC}"

    echo -e "${BLUE}[4/4] Verifying all running services...${NC}"
    $COMPOSE_CMD ps
}

start_local() {
    echo -e "${CYAN}[LOCAL MODE] Setting up local Python environment...${NC}"
    cd "$(dirname "$0")"

    if [ ! -d "venv" ]; then
        echo "Creating virtual environment in ./venv..."
        python3 -m venv venv
    fi

    echo "Activating virtualenv and installing dependencies..."
    . venv/bin/activate
    pip install -q -r requirements.txt

    export USE_SQLITE="true"
    export SECRET_KEY="dev-local-secret-key"
    export FLASK_ENV="development"
    export PORT=5000

    echo "Initializing database tables and seed data..."
    python3 scripts/init_db.py

    echo -e "${GREEN}[SUCCESS] Starting local Gunicorn server on http://localhost:5000...${NC}"
    exec gunicorn --bind 0.0.0.0:5000 --workers 2 "app:create_app()"
}

# Execute selected mode
if [ "$MODE" = "docker" ]; then
    start_docker
else
    start_local
fi

# Print Final Summary and Links
echo ""
echo -e "${GREEN}${BOLD}======================================================================${NC}"
echo -e "${GREEN}${BOLD}           ALL SERVICES SUCCESSFULLY DEPLOYED & OPERATIONAL           ${NC}"
echo -e "${GREEN}${BOLD}======================================================================${NC}"
echo ""
echo -e "  ${BOLD}Web Application:${NC}     ${CYAN}http://localhost:5000${NC}"
echo -e "  ${BOLD}API Health Check:${NC}    ${CYAN}http://localhost:5000/api/health${NC}"
echo -e "  ${BOLD}Prometheus Metrics:${NC}  ${CYAN}http://localhost:5000/metrics${NC}"
echo -e "  ${BOLD}Prometheus Server:${NC}   ${CYAN}http://localhost:9090${NC}"
echo -e "  ${BOLD}Grafana Dashboards:${NC}  ${CYAN}http://localhost:3000${NC} (admin / admin)"
echo ""
echo -e "  ${BOLD}Default Credentials:${NC}"
echo -e "    * Admin User:  Username: ${YELLOW}admin${NC}  | Password: ${YELLOW}admin123${NC}"
echo -e "    * Demo User:   Username: ${YELLOW}demo${NC}   | Password: ${YELLOW}demo123${NC}"
echo ""
echo -e "  ${BOLD}Helpful Commands:${NC}"
echo -e "    * View logs:    ${CYAN}docker compose logs -f notes_app${NC}"
echo -e "    * Run tests:    ${CYAN}./test.sh${NC}"
echo -e "    * Stop stack:   ${CYAN}./stop.sh${NC}"
echo -e "${GREEN}======================================================================${NC}"
echo ""
