# 🚨 Campus Incident Report Analysis System

**Multi-Agent AI System for Educational Institutions**

A sophisticated multi-agent AI platform designed to revolutionize how educational institutions handle incident reporting, analysis, and response. Built for Agentathon 2025.

## 🎯 Project Objective

The primary objective of this project is to automate and streamline the lifecycle of campus incident management. By utilizing a swarm of specialized AI agents, the system ensures rapid, compliant, and well-documented responses to various campus incidents such as security breaches, medical emergencies, policy violations, and harassment.

### 🤖 Multi-Agent Architecture

The system achieves this through five specialized AI agents working collaboratively:

1. **📝 Prompt Agent**: Intakes raw incident reports, extracts structured data, and classifies the incident type and severity.
2. **📋 Planner Agent**: Formulates a step-by-step action plan, identifies key stakeholders, and establishes a timeline.
3. **🔒 Safety & Policy Agent**: Cross-references the plan against campus policies (like Title IX and FERPA) to ensure strict regulatory compliance and block harmful actions.
4. **⚙️ Executor Agent**: Simulates the execution of the approved plan, managing resource allocation and system notifications.
5. **📊 Evaluator Agent**: Assesses the overall quality of the response, providing scores and insights for continuous system improvement.

## 📁 Project Structure

The codebase is organized into several key domains:
- **`agents/`**: Core definitions for all AI agents.
- **`logic/`**: Backend logic, spam detection, reinforcement learning, and data generation modules.
- **`dashboard/`**: Startup scripts and server deployment configurations for the user interface.
- **`app/` / `backend/` / `frontend/`**: The core API server and React dashboard application.
- **`data/`**: Stores JSON datastores (`analytics_data.json`, `real_incidents.json`, `rl_system_data.json`).

## 🚀 Getting Started

Please refer to [VSCODE_SETUP.md](./VSCODE_SETUP.md) for instructions on how to run and manage this project directly within Visual Studio Code!