#!/bin/bash

# Color codes for styling output
GREEN="\033[1;32m"
BLUE="\033[1;34m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
CYAN="\033[1;36m"
RESET="\033[0m"

# Get terminal width dynamically (fallback for non-TTY)
TERM_WIDTH=$( (tput cols 2>/dev/null || echo 80) )

# Messages to center
TITLE_MESSAGE="🔥🤖 AGENT IGNITED - VERSA FORGE CLI 🤖🔥"
ART=(
"____   ____                            ___________                         "
"\\   \\ /   /___________  ___________    \\_   _____/__________  ____   ____  "
" \\   Y   // __ \\_  __ \\/  ___/\\__  \\    |    __)/  _ \\_  __ \\/ ___\\_/ __ \\ "
"  \\     /\\  ___/|  | \\/\\___ \\  / __ \\_  |     \\(  <_> )  | \\/ /_/  >  ___/ "
"   \\___/  \\___  >__|  /____  >(____  /  \\___  / \\____/|__|  \\___  / \\___  >"
"              \\/           \\/      \\/       \\/             /_____/      \\/  "
)

print_centered() {
  local text="$1"
  local padding=$(( (TERM_WIDTH - ${#text}) / 2 ))
  [ "$padding" -lt 0 ] && padding=0
  printf "%${padding}s%s\n" "" "$text"
}

print_dashed_line() {
  printf "%${TERM_WIDTH}s\n" | tr ' ' '-'
}

echo -e "${GREEN}$(print_dashed_line)${RESET}"
for line in "${ART[@]}"; do print_centered "$line"; done
echo -e "${CYAN}$(print_centered "$TITLE_MESSAGE")${RESET}"
echo -e "${GREEN}$(print_dashed_line)${RESET}"

show_usage() {
  echo -e "${YELLOW}Usage:${RESET} ./scripts/run.sh ${GREEN}[local|docker|docker-prod]${RESET}"
  echo -e "  🖥️  ${GREEN}local${RESET}        - Run FastAPI locally with hot reload"
  echo -e "  🐳  ${GREEN}docker${RESET}       - Run FastAPI in Docker (development mode)"
  echo -e "  🚀  ${GREEN}docker-prod${RESET}  - Run FastAPI in Docker (production mode)"
  echo -e "${RED}Example:${RESET} ./scripts/run.sh local"
}

if [ -z "$1" ]; then
  echo -e "${RED}❌ Error:${RESET} No argument provided."
  show_usage
  exit 1
fi

fake_loading() {
  echo -e -n "${CYAN}⏳ Initializing${RESET}"
  for _ in {1..5}; do sleep 0.02; echo -n "."; done
  echo " ✅"
}

case "$1" in
  local)
    export RUNNING_IN_DOCKER=false
    echo -e "⚡ ${GREEN}Starting FastAPI locally with hot reload...${RESET}"
    fake_loading
    # fastapi dev app/main.py
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

    ;;

  docker)
    export RUNNING_IN_DOCKER=true
    echo -e "🐳 ${GREEN}Starting FastAPI in Docker (development mode)...${RESET}"
    fake_loading
    # Ensure the main and override compose files are used
    docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build app
    ;;

  docker-prod)
    export RUNNING_IN_DOCKER=true
    echo -e "🚀 ${GREEN}Starting FastAPI in Docker (production mode)...${RESET}"
    fake_loading
    # Use base and prod overlay, and stop/remove previous containers safely
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d app
    ;;

  *)
    echo -e "${RED}❌ Error:${RESET} Invalid argument: '$1'"
    show_usage
    exit 1
    ;;
esac
