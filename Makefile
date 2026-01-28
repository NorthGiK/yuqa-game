main_run = ./.venv/bin/python3 main.py
install_deps = uv sync
docker_run = docker run -d

all: main# redis rabbitmq main

main:
	$(install_deps)
	$(main_run)

redis:
	$(docker_run) redis

rabbitmq:
	$(docker_run) -p 5672:5672 -p 15672:15672 rabbitmq:management
