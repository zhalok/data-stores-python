// getCommand generates a random command like Python version
package main

import (
	"bufio"
	"flag"
	"fmt"
	"math/rand"
	"net"
	"sync"
	"time"
)

type Request struct {
	id   int
	addr string
}

var totalRequestCompleted = 0

var mu sync.Mutex

var commandsPerConnection = 1000

func getCommand() string {
	commands := []string{"set", "get", "delete"}

	cmd := commands[rand.Intn(len(commands))]         // pick random command
	key := fmt.Sprintf("key-%d", rand.Intn(100000)+1) // random key 1-100000
	var commandStr string

	if cmd == "set" {
		value := fmt.Sprintf("value-%d", rand.Intn(100000)+1) // random value
		commandStr = fmt.Sprintf("%s %s %s\n", cmd, key, value)
	} else {
		commandStr = fmt.Sprintf("%s %s\n", cmd, key)
	}

	return commandStr
}

func processor(id int, requestId int, addr string) {
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		fmt.Printf("Worker %d: failed to connect: %v\n", id, err)
		return
	}
	defer conn.Close()

	fmt.Printf("connection established with address %s\n", addr)

	writer := bufio.NewWriter(conn)

	commandsWriten := 0
	for i := 0; i < commandsPerConnection; i++ {
		command := getCommand()
		writer.WriteString(command)
		commandsWriten += 1

		if (i+1)%100 == 0 {
			err = writer.Flush()
			if err != nil {
				fmt.Printf("there was an error flushing the writes to the connection %v\n", err)
				err = conn.Close()
				if err != nil {
					fmt.Printf("there was a problem closing the connection %v\n", err)
					return
				}
				fmt.Println("connection closed")
				return
			}
			fmt.Printf("sent %d commands\n",commandsWriten)
			time.Sleep(10 * time.Second)
		}

	}
	fmt.Printf("connection %d completed", requestId)
	conn.Close()
}

func worker(id int, wg *sync.WaitGroup, inputChan chan Request) {
	defer wg.Done()
	for req := range inputChan {
		processor(id, req.id, req.addr)
	}

}

func main() {
	numWorkers := flag.Int("workers", 10, "number of worker goroutines")
	numConnections := flag.Int("connections", 10, "number of connections to create")
	commands := flag.Int("commands", 10, "number of connections to create")
	queueSize := flag.Int("queue-size", 10, "size of the request queue")
	addr := flag.String("addr", "localhost:8003", "TCP server address")

	flag.Parse()

	commandsPerConnection = *commands

	fmt.Printf("Number of workers %d\n",*numWorkers)

	inputChan := make(chan Request, *queueSize)
	var wg sync.WaitGroup
	for i := 0; i < *numWorkers; i++ {
		wg.Add(1)
		go worker(i+1, &wg, inputChan)
	}

	for connection := 0; connection < *numConnections; connection++ {
		req := Request{
			id:   connection + 1,
			addr: *addr,
		}
		inputChan <- req
	}

	close(inputChan)
	wg.Wait()

}
