DC = docker-compose

.PHONY: up down restart logs build

up:
	$(DC) up -d

down:
	$(DC) down

restart:
	$(DC) down
	$(DC) up -d --build

build:
	$(DC) build