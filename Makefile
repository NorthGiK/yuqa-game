# Запуск приложения
main_run = ./.venv/bin/python3 main.py
# Синхронизировать зависимости
install_deps = uv sync
# запустить image в докере в фоне
docker_run = docker run -d
# закрыть image в докере
docker_stop = docker stop

all: main

main: redis rabbitmq
	$(install_deps)
	$(main_run)

# Запустить redis в докера
redis:
	$(docker_run) redis

# Запустить RabbitMQ на порту 5672 и админку в браузере на порту 15672
rabbitmq:
	$(docker_run) -p 5672:5672 -p 15672:15672 rabbitmq:management

# Закрыть все в докере
clean:
	$(docker_stop) redis
	$(docker_stop) rabbitmq:management


.PHONY: main clean
