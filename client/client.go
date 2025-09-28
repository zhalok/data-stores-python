// getCommand generates a random command like Python version
package main

import (
	"bufio"
	"fmt"
	"math/rand"
	"net"
	"sync"
)

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

func worker(id int, wg *sync.WaitGroup, addr string) {
	defer wg.Done()

	conn, err := net.Dial("tcp", addr)
	if err != nil {
		fmt.Printf("Worker %d: failed to connect: %v\n", id, err)
		return
	}
	defer conn.Close()

	writer := bufio.NewWriter(conn)

	totalCommandsSent := 0

	for batch := 0; batch < 100; batch++ {
		for i := 0; i < 100; i++ {
			command := getCommand()
			fmt.Printf("command %s", command)
			_, err := writer.WriteString(command)
			if err != nil {
				panic(err)
			}

			totalCommandsSent += 1

		}

		err = writer.Flush()
		if err != nil {
			fmt.Printf("Worker %d: flush error: %v\n", id, err)
			return
		}

		fmt.Printf("Worker %d: finished sending %d commands\n", id, totalCommandsSent)
	}

}

func main() {
	n := 10000               // number of goroutines
	addr := "127.0.0.1:8004" // TCP server address

	var wg sync.WaitGroup
	for it := 0; it < 1000; it++ {
		for i := 1; i <= n; i++ {
			wg.Add(1)
			go worker(i, &wg, addr)
		}

		wg.Wait()
		fmt.Println("All workers finished")
	}
	fmt.Println("all batch completed")

}
