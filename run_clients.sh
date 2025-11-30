#!/bin/bash

# Shell script to run all client programs in detached mode
# Usage: ./run_clients.sh [workers] [connections] [commands] [queue-size] [sleep]

# Default values
WORKERS=${1:-10}
CONNECTIONS=${2:-10}
COMMANDS=${3:-100000}
QUEUE_SIZE=${4:-10}
SLEEP=${5:-5}

# Log directory
LOG_DIR="./logs"
mkdir -p "$LOG_DIR"

echo "Starting clients with configuration:"
echo "  Workers: $WORKERS"
echo "  Connections: $CONNECTIONS"
echo "  Commands per connection: $COMMANDS"
echo "  Queue size: $QUEUE_SIZE"
echo "  Sleep duration: $SLEEP seconds"
echo ""

# Run single_threaded client (port 8000)
echo "Starting single_threaded client..."
cd single_threaded
nohup go run client.go \
  --workers="$WORKERS" \
  --connections="$CONNECTIONS" \
  --commands="$COMMANDS" \
  --queue-size="$QUEUE_SIZE" \
  --sleep="$SLEEP" \
  --addr="localhost:8000" \
  > "../$LOG_DIR/single_threaded_client.log" 2>&1 &
SINGLE_THREADED_PID=$!
echo "Single threaded client started (PID: $SINGLE_THREADED_PID)"
cd ..

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
echo "To stop all clients, run:"
echo "  kill $SINGLE_THREADED_PID $MULTI_THREADED_PID $EPOLL_PID"
echo ""
echo "To monitor logs:"
echo "  tail -f $LOG_DIR/single_threaded_client.log"
echo "  tail -f $LOG_DIR/multi_threaded_client.log"
echo "  tail -f $LOG_DIR/single_threaded_epoll_client.log"
