# Microservices

> Run all commands from the **project root**.

## Build

bash
docker build -t safe-rule-service -f microservices/safe_rule_service/Dockerfile .
docker build -t unsafe-rule-service -f microservices/unsafe_rule_service/Dockerfile .


## Run

powershell
docker run --rm -v "${PWD}/db.sqlite3:/app/db.sqlite3" safe-rule-service
docker run --rm -v "${PWD}/db.sqlite3:/app/db.sqlite3" unsafe-rule-service


## Or both at once

bash
docker compose -f microservices/docker-compose.yml up --build

