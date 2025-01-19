This repository showcases a **fully working pipeline** that reads streaming data from a generator, validates and transforms it, routes valid messages to a new topic, and performs a simple aggregation. It uses **Zookeeper**, **Kafka**, **Redis**, **Docker Compose**, and Python services for consumer/aggregator logic.

## Table of Contents
1. [Overview](#overview)  
2. [Prerequisites](#prerequisites)  
3. [Project Structure](#project-structure)  
4. [How to Run](#how-to-run)  
5. [Additional Questions](#additional-questions)  
   - [1) How would you deploy this application in production?](#1-how-would-you-deploy-this-application-in-production)  
   - [2) What other components would you want to add to make this production ready?](#2-what-other-components-would-you-want-to-add-to-make-this-production-ready)  
   - [3) How can this application scale with a growing dataset?](#3-how-can-this-application-scale-with-a-growing-dataset)  
  

---

## Overview

The pipeline consists of the following services:

- **Zookeeper** and **Kafka**: Provide the messaging backbone.  
- **Redis**: Stores aggregator counts so restarts don’t lose data.  
- **Data Generator**: Produces random messages to the `user-login` topic.  
- **Consumer**: Reads from `user-login`, validates fields (`app_version`, `device_type`, `ip`), sends valid data to `user-login-processed` and invalid data to `user-login-errors`.  
- **Aggregator**: Reads from `user-login-processed`, increments device counters (Android/iOS) in Redis, and prints them periodically.

### Highlights:
1. **Health checks** to avoid race conditions (e.g., `NoBrokersAvailable`).  
2. Specifying `platform: "linux/amd64"` for the data generator container if your host is `arm64`.  
3. **Basic unit tests** for the consumer’s validation logic.  

---

## Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose installed.  
- (Optional) **Python 3.10+** if you’d like to run tests locally without containers.

---

## Project Structure

```plaintext
real-time-pipeline/
 ├─ docker-compose.yml
 ├─ consumer/
 │   ├─ Dockerfile
 │   ├─ requirements.txt
 │   ├─ consumer.py
 │   └─ tests/
 │       └─ test_consumer.py
 ├─ aggregator/
 │   ├─ Dockerfile
 │   ├─ requirements.txt
 │   └─ aggregator.py
 └─ README.md
 ```

docker-compose.yml: Defines Zookeeper, Kafka, Redis, the data generator, consumer, and aggregator.

consumer: Code for reading from user-login, validating IPs, writing valid data to user-login-processed.

aggregator: Simple aggregator that counts Android/iOS logins from user-login-processed and stores them in Redis.

## How to Run
Build the containers: ```docker compose build```

Start the pipeline: ```docker compose up -d```

Check the logs: ```docker compose logs my-consumer -f```
```docker compose logs my-aggregator -f```

Confirm processed data : 
```
docker exec -it <kafka_container_id> bash
kafka-console-consumer \
    --bootstrap-server kafka:9092 \
    --topic user-login-processed \
    --from-beginning
```
    

Check invalid data : 
```
kafka-console-consumer \
    --bootstrap-server kafka:9092 \
    --topic user-login-errors \
    --from-beginning
```

## Additional Questions

1) How would you deploy this application in production?
	•	Container Orchestration: Usually, Kubernetes is popular. You’d package the consumer and aggregator as separate deployments, each scaled as needed.
	•	Managed Kafka: Many teams prefer hosted services like Confluent Cloud or Amazon MSK so they don’t manually manage Kafka clusters.
	•	External Redis or Managed Cache: For aggregator state, you might use something like AWS ElastiCache for Redis.
	•	CI/CD: Integrate Docker builds in your CI/CD pipeline (e.g., Jenkins, GitHub Actions), run tests, then deploy to staging and production environments.

2) What other components would you want to add to make this production ready?
	•	Schema Registry: Keep message formats versioned and consistent as data evolves.
	•	Monitoring & Alerts: Tools like Prometheus/Grafana to watch consumer lag, aggregator performance, Redis usage, etc.
	•	Security: Encrypt data in transit (SASL_SSL for Kafka) and use ACLs to limit producer/consumer access.
	•	Error Analysis: The pipeline sends invalid data to user-login-errors. You could set up a dedicated service or workflow to analyze and handle these records further.

3) How can this application scale with a growing dataset?
   	•	Kafka Partitions: Increase partitions on the main topic (user-login), allowing multiple consumers to split the load.
	•	Horizontal Scaling: Run multiple replicas of the consumer and aggregator in Kubernetes. Each consumer handles a subset of partitions.
	•	Load Testing: Monitor consumer lag. If it grows, add more partitions or more consumer replicas to keep up.


Submission for Daniel 
