#!/bin/bash

# Color codes for styling output
GREEN="\033[1;32m"
BLUE="\033[1;34m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
CYAN="\033[1;36m"
RESET="\033[0m"

# Get terminal width dynamically
TERM_WIDTH=$(tput cols)

# Messages to center
TITLE_MESSAGE="🔥🤖 AGENT IGNITED - VERSA FORGE CLI 🤖🔥"
ART=(
"____   ____                            ___________                         "
"\   \ /   /___________  ___________    \_   _____/__________  ____   ____  "
" \   Y   // __ \_  __ \/  ___/\__  \    |    __)/  _ \_  __ \/ ___\_/ __ \ "
"  \     /\  ___/|  | \/\___ \  / __ \_  |     \(  <_> )  | \/ /_/  >  ___/ "
"   \___/  \___  >__|  /____  >(____  /  \___  / \____/|__|  \___  / \___  >"
"              \/           \/      \/       \/             /_____/      \/  "
)

# Function to print centered text
print_centered() {
  local text="$1"
  local padding=$(( (TERM_WIDTH - ${#text}) / 2 ))
  printf "%${padding}s%s\n" "" "$text"
}

# Function to print a full-width dashed line
print_dashed_line() {
  printf "%${TERM_WIDTH}s\n" | tr ' ' '-'
}

# Print dashed line (full screen width)
echo -e "${GREEN}$(print_dashed_line)${RESET}"

# Print ASCII Art (centered)
for line in "${ART[@]}"; do
  print_centered "$line"
done

# Print centered title message
echo -e "${CYAN}$(print_centered "$TITLE_MESSAGE")${RESET}"

# Print dashed line again
echo -e "${GREEN}$(print_dashed_line)${RESET}"

# Function to show usage instructions
show_usage() {
  echo -e "${YELLOW}Usage:${RESET} ./scripts/run.sh ${GREEN}[local|docker|docker-pro]${RESET}"
  echo -e "  🖥️  ${GREEN}local${RESET}       - Runs FastAPI locally with hot reload"
  echo -e "  🐳  ${GREEN}docker${RESET}      - Runs FastAPI inside Docker (Development Mode)"
  echo -e "  🚀  ${GREEN}docker-pro${RESET}  - Runs FastAPI in Production Mode (Optimized Docker)"
  echo -e "${RED}Example:${RESET} ./scripts/run.sh local"
}

# Check if an argument is provided
if [ -z "$1" ]; then
  echo -e "${RED}❌ Error:${RESET} No argument provided."
  show_usage
  exit 1
fi

# Fake loading bar effect
fake_loading() {
  echo -e -n "${CYAN}⏳ Initializing${RESET}"
  for i in {1..5}; do
    sleep 0.01
    echo -n "."
  done
  echo " ✅"
}

# Start application based on argument
case "$1" in
  local)
    export RUNNING_IN_DOCKER=false
    echo -e "⚡ ${GREEN}Starting FastAPI locally with hot reload...${RESET}"
    fake_loading
    fastapi dev app/main.py
    ;;

  docker)
    export RUNNING_IN_DOCKER=true
    echo -e "🐳 ${GREEN}Starting FastAPI in Docker mode (Development)...${RESET}"
    fake_loading
    docker-compose up app --build
    ;;

  docker-prod)
    export RUNNING_IN_DOCKER=true
    echo -e "🚀 ${GREEN}Starting FastAPI in Docker Production mode...${RESET}"
    fake_loading
    # Stop and remove existing production containers before running a new one
    docker-compose -f docker-compose.prod.yml down
    docker-compose -f docker-compose.prod.yml up --build -d
    ;;

  *)
    echo -e "${RED}❌ Error:${RESET} Invalid argument: '$1'"
    show_usage
    exit 1
    ;;
esac
