# temp-data-server
Python server to collect home data and write it in influxDb


## Request format

POST Request with body : 

```
{"temperature": 20" , "humidity": "75", "location": "bed_room"}
```

## InfluxDB

InfluxDB must running on localhost using port 8086.
The database name is `homedata`