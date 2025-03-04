.PHONY: build run

build:
	docker build -t colab-frontend ./frontend_task/colab_frontend

run:
	docker run -p 3000:3000 colab-frontend

