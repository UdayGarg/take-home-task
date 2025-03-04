.PHONY: build-frontend run-frontend build-backend run-backend stop clean

# Frontend (Next.js) Commands
build-frontend:
	docker build -t colab-frontend ./frontend_task/colab_frontend

run-frontend:
	docker run -p 3000:3000 --name colab-frontend-container colab-frontend

# Backend (Flask) Commands
build-backend:
	docker build -t flask-app -f regulation_task/Dockerfile .

run-backend:
	docker run -p 5001:5001 --name flask-app-container flask-app

# Stop Running Containers
stop:
	docker stop colab-frontend-container flask-app-container || true
	docker rm colab-frontend-container flask-app-container || true

# Remove Unused Docker Images & Containers
clean:
	docker system prune -f
