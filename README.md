# **Project Setup and Usage Guide**

This repository contains two separate projects:  
1. **Collaborative Revision Status Application** 

2. **Regulatory Compliance Document Processor** 

Each project has its own dependencies, setup, and usage instructions. Below is a unified guide to running both projects using **Docker and Makefile** for ease of use.

---

## **📦 Prerequisites**
Before running the projects, ensure you have the following installed:
- [Docker](https://www.docker.com/get-started) (for containerized execution)
- [Make](https://www.gnu.org/software/make/) (to simplify build and run commands)

> **Optional:** If you prefer to run projects locally (without Docker), refer to their individual `README.md` files for manual setup and dependencies.

---

## **🛠️ Setup & Running with Docker**
The repository includes a `Makefile` to simplify building and running both projects.

### **1️⃣ Build Docker Images**
Before running the projects, build the necessary Docker images:
```bash
make build-frontend   # Builds frontend_task
make build-backend    # Builds regualtion_task
```

### **2️⃣ Run the Applications**
To start both applications:
```bash
make run-frontend    # Starts the frontend_task on port 3000
make run-backend     # Starts the regulation_task on port 5001
```

### **3️⃣ Access the Applications**
- **Frontend (Next.js UI)** → [http://localhost:3000](http://localhost:3000)  
- **Backend (Flask API)** → [http://localhost:5001](http://localhost:5001)

---

## **🔧 Stopping and Cleaning Up**
If you need to **stop** the running containers:
```bash
make stop
```

To **remove unused Docker images and free up space**:
```bash
make clean
```

---

## **📜 Additional Notes**
- Both projects have detailed documentation in their respective `README.md` files.  
- The backend project requires `uv` for Python package management, which is already handled in Docker.  
- The frontend project is a **Next.js 15** application using **Node.js 18+** and **npm/yarn**.  

