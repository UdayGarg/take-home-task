# **Project Setup and Usage Guide**

This repository contains two separate projects:  
1. **Collaborative Revision Status Application**  
2. **Regulatory Compliance Document Processor**  

Each project has its own dependencies, setup, and usage instructions. Below is a unified guide to running both projects using **Docker and Makefile** or **Docker Compose** for ease of use.

## **Prerequisites**
Before running the projects, ensure you have the following installed:
- [Docker](https://www.docker.com/get-started) (for containerized execution)
- [Docker Compose](https://docs.docker.com/compose/) (for managing multiple containers)
- [Make](https://www.gnu.org/software/make/) (if using the Makefile option)

### **Required Environment Variable**
The backend application requires an **OpenAI API Key** for functionality. Ensure that the `OPENAI_API_KEY` environment variable is set before running the backend.

To set it manually:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

If using Docker Compose, ensure the variable is passed correctly in your terminal.

## **Setup & Running with Docker**
You can set up and run both projects using either **Makefile** or **Docker Compose**.

### **Option 1: Using Makefile**
The repository includes a `Makefile` to simplify building and running both projects.

#### **1. Build Docker Images**
```bash
make build-frontend   # Builds frontend_task
make build-backend    # Builds regulation_task
```

#### **2. Run the Applications**
```bash
make run-frontend    # Starts the frontend_task on port 3000
make run-backend     # Starts the regulation_task on port 5001
```

#### **3. Access the Applications**
- **Frontend (Next.js UI)** → [http://localhost:3000](http://localhost:3000)  
- **Backend (Flask API)** → [http://localhost:5001](http://localhost:5001)

#### **4. Stop and Clean Up**
```bash
make stop   # Stops running containers
make clean  # Removes unused Docker images and frees up space
```

### **Option 2: Using Docker Compose**
Instead of using `Makefile`, you can use **Docker Compose** for managing both services.

#### **1. Build and Start Both Services**
```bash
docker compose up --build
```
This will:
- Build the **frontend** and **backend** images.
- Start both applications.

#### **2. Running the Applications**
```bash
docker compose up
```
- This starts both **frontend (Next.js)** and **backend (Flask API)**.

#### **3. Access the Applications**
- **Frontend (Next.js UI)** → [http://localhost:3000](http://localhost:3000)  
- **Backend (Flask API)** → [http://localhost:5001](http://localhost:5001)

#### **4. Stopping Both Services**
To **stop** both applications:
```bash
docker compose down
```

#### **5. Remove Unused Docker Resources**
```bash
docker system prune -f
```

## **Additional Notes**
- Both projects have detailed documentation in their respective `README.md` files.  
- The backend project requires `uv` for Python package management, which is already handled in Docker.  
- The frontend project is a **Next.js 15** application using **Node.js 18+** and **npm/yarn**.  

### **Which Method Should You Use?**
| Method | Best For | Command |
|--------|---------|---------|
| **Makefile** | Simple build/run commands | `make build-frontend && make run-frontend` |
| **Docker Compose** | Managing both services at once | `docker compose up --build` |

Both options are valid. Choose based on your **workflow preference**.
