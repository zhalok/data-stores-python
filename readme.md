run the command

```
docker compose down && docker compose up -d --build
```

go to localhost:8080 --> you can see cadvisor metrics for all the containers

go to localhost:8089, localhost:8090 and localhost:8091 and start load testing with 100 concurrent users

observe the metrics in cadvisor
