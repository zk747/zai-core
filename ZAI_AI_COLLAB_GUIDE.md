🔹 Purpose

You are assisting in the development of ZAI Core, a modular, privacy-first intelligent system that runs locally.
ZAI Core is not a chatbot—it is an operating environment where AI modules learn from local data, remember, and act autonomously.
All outputs must integrate cleanly with the existing Dockerized micro-service stack.

🔹 Overall Architecture Summary
Component	Language	Port	Description
React Dashboard	React + Tailwind CSS (+ TypeScript)	5173	User interface / control panel
Node API	Node.js (Express + PostgreSQL + Redis)	4000	Application logic + database layer
Python AI Service	Python (FastAPI + PyTorch + Transformers)	8000	Intelligence engine / RAG / Memory Engine
Data Stores	PostgreSQL, Redis, MinIO, ElasticSearch + Kibana	—	Persistence + logging + search
Docker Compose	—	—	Spins up and links all services locally
🔹 Rules for Any File They Create

Follow existing structure

Backend code → backend/node-api/ or backend/python-ai/

Frontend UI → frontend/react-dashboard/

New stand-alone experiments → /experiments/<feature-name>/

Stay self-contained
Each script or component must work independently without breaking the Compose network.

Use ports and endpoints exactly as defined

Frontend ↔ Node API (4000)

Frontend ↔ Python AI (8000)

No external cloud calls
Everything must run locally; dependencies must be open source.

Deliverables

Full source file with imports and dependencies.

Short README inside its folder explaining what it does.

Clean TypeScript / Python docstrings.

Style guide

Follow Tailwind for frontend styling.

Follow PEP8 and FastAPI standards for Python.

Use ES modules and async/await for Node.

Use consistent naming: zai_<module>.py, Zai<Component>.tsx.

Goal orientation
Everything they build should either:

Help ZAI read data, remember data, or act on data.

🔹 Examples of Good Requests You Can Give Them

“Create a FastAPI endpoint /read-folder that returns file names and word counts as JSON for the React Memory Engine page.”

“Generate a React component that uploads PDFs and sends them to http://localhost:8000/upload.”

“Write a Node script that logs every service health check into PostgreSQL.”
