// getCommand generates a random command like Python version
package main

import (
	"bufio"
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
	for i := 0; i < 10000; i++ {
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
	numWorker := 4000 // number of goroutines
	numConnections := 100000
	queueSize := 1

	addr := "localhost:8003" // TCP server address
	inputChan := make(chan Request, queueSize)
	var wg sync.WaitGroup
	for i := 0; i < numWorker; i++ {
		wg.Add(1)
		go worker(i+1, &wg, inputChan)
	}

	for connection := 0; connection < numConnections; connection++ {
		req := Request{
			id:   connection + 1,
			addr: addr,
		}
		inputChan <- req
	}

	close(inputChan)
	wg.Wait()

}
