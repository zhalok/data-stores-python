#!/bin/bash

# Shell script to run all client programs in detached mode
# Usage: ./run_clients.sh [workers] [connections] [commands] [queue-size] [sleep]

# Default values
WORKERS=${1:-1000}
CONNECTIONS=${2:-100000}
COMMANDS=${3:-10000}
QUEUE_SIZE=${4:-100}
SLEEP=${5:-15}

# Log directory
LOG_DIR="./logs"
mkdir -p "$LOG_DIR"

# Array to store PIDs
declare -a PIDS

# Cleanup function to kill all clients
cleanup() {
  echo ""
  echo "Received exit signal. Stopping all clients..."
  for pid in "${PIDS[@]}"; do
    if kill -0 "$pid" 2>/dev/null; then
      echo "Stopping process $pid..."
      kill "$pid"
    fi
  done
  echo "All clients stopped."
  exit 0
}

# Register signal handlers
trap cleanup SIGINT SIGTERM

echo "Starting clients with configuration:"
echo "  Workers: $WORKERS"
echo "  Connections: $CONNECTIONS"
echo "  Commands per connection: $COMMANDS"
echo "  Queue size: $QUEUE_SIZE"
echo "  Sleep duration: $SLEEP seconds"
echo ""

# Run single_threaded client (port 8000)
# echo "Starting single_threaded client..."
# cd single_threaded
# nohup go run client.go \
#   --workers="$WORKERS" \
#   --connections="$CONNECTIONS" \
#   --commands="$COMMANDS" \
#   --queue-size="$QUEUE_SIZE" \
#   --sleep="$SLEEP" \
#   --addr="localhost:8000" \
#   > "../$LOG_DIR/single_threaded_client.log" 2>&1 &
# SINGLE_THREADED_PID=$!
# PIDS+=($SINGLE_THREADED_PID)
# echo "Single threaded client started (PID: $SINGLE_THREADED_PID)"
# cd ..

# Run multi_threaded client (port 8001)
echo "Starting multi_threaded client..."
cd multi_threaded
nohup go run client.go \
  --workers="$WORKERS" \
  --connections="$CONNECTIONS" \
  --commands="$COMMANDS" \
  --queue-size="$QUEUE_SIZE" \
  --sleep="$SLEEP" \
  --addr="localhost:8001" \
  > "../$LOG_DIR/multi_threaded_client.log" 2>&1 &
MULTI_THREADED_PID=$!
PIDS+=($MULTI_THREADED_PID)
echo "Multi threaded client started (PID: $MULTI_THREADED_PID)"
cd ..

# Run single_threaded_epoll client (port 8003)
echo "Starting single_threaded_epoll client..."
cd single_threaded_epoll
nohup go run client.go \
  --workers="$WORKERS" \
  --connections="$CONNECTIONS" \
  --commands="$COMMANDS" \
  --queue-size="$QUEUE_SIZE" \
  --sleep="$SLEEP" \
  --addr="localhost:8003" \
  > "../$LOG_DIR/single_threaded_epoll_client.log" 2>&1 &
EPOLL_PID=$!
PIDS+=($EPOLL_PID)
echo "Single threaded epoll client started (PID: $EPOLL_PID)"
cd ..

echo ""
echo "All clients started successfully!"
echo ""
echo "PIDs:"
echo "  single_threaded: $SINGLE_THREADED_PID"
echo "  multi_threaded: $MULTI_THREADED_PID"
echo "  single_threaded_epoll: $EPOLL_PID"
echo ""
echo "Logs are available in:"
echo "  $LOG_DIR/single_threaded_client.log"
echo "  $LOG_DIR/multi_threaded_client.log"
echo "  $LOG_DIR/single_threaded_epoll_client.log"
echo ""
echo "Press Ctrl+C to stop all clients"
echo ""
echo "To monitor logs:"
echo "  tail -f $LOG_DIR/single_threaded_client.log"
echo "  tail -f $LOG_DIR/multi_threaded_client.log"
echo "  tail -f $LOG_DIR/single_threaded_epoll_client.log"
echo ""

# Wait indefinitely until interrupted
while true; do
  sleep 1
done
