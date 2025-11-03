"""API to orchestrate Research, Writer and Deployment agents in sequence.

This lightweight Flask app exposes endpoints to run the three agents in order:
1. ResearchAgent.analyze_repository(repo_path)
2. WriterAgent.generate_documentation(analysis, output_path)
3. DeploymentAgent.generate_deployment_config(analysis)

Behavior:
- If an `api_key` is provided (in JSON payload or environment), it will be used
  to initialize the agents.
- If agent initialization fails (missing API key), the app falls back to a
  StubAgent implementation so the API remains usable for local testing.

This file intentionally keeps a small in-memory task store for background
execution. Replace it with Redis/Celery for production workloads.
"""
from __future__ import annotations

import os
import threading
import uuid
from typing import Any, Dict, Optional

from flask import Flask, Request, Response, jsonify, request

#All these imports are to ensure functionality of the program...make type notes behave nicer, talk to computer, run background helpers, and make unique IDs

# Make research_writer package importable when running from repo root
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ResearchWriter", "src"))

# Delay importing heavy agent modules until runtime. The ResearchWriter
# package depends on large ML libraries (crewai, langchain, etc.). If those
# libs are not installed we gracefully fall back to the StubAgent at runtime.
ResearchAgent = None
WriterAgent = None
DeploymentAgent = None


def _import_agent_classes():
    """Attempt to import the agent classes. Return a tuple
    (ResearchAgent, WriterAgent, DeploymentAgent) where any missing class
    is set to None.
    """
    global ResearchAgent, WriterAgent, DeploymentAgent
    if ResearchAgent is not None or WriterAgent is not None or DeploymentAgent is not None: #For the case that they are not None OR they are running
        return ResearchAgent, WriterAgent, DeploymentAgent
    try:
        from research_writer.agents.research_agent import ResearchAgent as R #Import Research Agent
        from research_writer.agents.writer_agent import WriterAgent as W #Import Writer Agent
        from research_writer.agents.deployment_agent import DeploymentAgent as D #Import Deployment Agent
        ResearchAgent, WriterAgent, DeploymentAgent = R, W, D #Assigning the agents!
    except Exception:
        # Keep them as None; caller will use StubAgent fallbacks
        ResearchAgent, WriterAgent, DeploymentAgent = None, None, None
    return ResearchAgent, WriterAgent, DeploymentAgent


app = Flask(__name__) #Initializing the Flask app


# Simple thread-safe in-memory task store (development only)
_tasks: Dict[str, Dict[str, Any]] = {}
_tasks_lock = threading.Lock()


def _set_task(task_id: str, payload: Dict[str, Any]) -> None: #This function sets a task in the task store
    with _tasks_lock:
        _tasks[task_id] = payload

def _update_task(task_id: str, **fields: Any) -> None: #This function updates a task in the task store
    with _tasks_lock:
        if task_id in _tasks:
            _tasks[task_id].update(fields)

def _get_task(task_id: str) -> Optional[Dict[str, Any]]: #This function retrieves a task from the task store
    with _tasks_lock:
        return _tasks.get(task_id)


class StubAgent:
    """A minimal stub that stands in for crewai Agent.execute_task.

    The real agents call an LLM via crewai and expect agent.execute_task(task).
    When OpenAI credentials are not available we attach this stub so the
    orchestration still runs and produces deterministic placeholder output.
    """

    def execute_task(self, task: Any) -> str: #This function executes a task and returns a string
        desc = getattr(task, "description", "") or ""
        d = desc.lower()
        if "architecture" in d or "architect" in d: #If the task is about architecture
            return "Monolithic-like architecture inferred from repository layout."
        if "design patterns" in d or "design pattern" in d: #If the task is about design patterns
            return "Singleton\nFactory\nAdapter"
        if "dockerfile" in d: #If the task is about dockerfile
            return "# Dockerfile\nFROM python:3.11-slim\n# ..."
        if "kubernetes" in d or "k8s" in d: #If the task is about kubernetes
            return "apiVersion: v1\nkind: Service\n# ..."
        if "ci/cd" in d or "ci cd" in d or "pipeline" in d: #If the task is about CI/CD pipeline
            return "# CI/CD pipeline stub"
        if "environment variables" in d or "env" in d: #If the task is about environment variables
            return "DATABASE_URL, REDIS_URL"
        return "Stubbed result"


def safe_instantiate(agent_cls, api_key: Optional[str] = None):
    """Try to instantiate the agent class with api_key; if it fails return a
    minimal instance with a StubAgent attached.
    """
    try:
        if api_key: #If there is an API key
            instance = agent_cls(api_key=api_key)
        else: #If there is no API key
            instance = agent_cls()
        return instance
    except Exception:
        # Fallback: create instance without running __init__ and attach stub agent
        inst = agent_cls.__new__(agent_cls)
        inst.agent = StubAgent()
        # WriterAgent expects a jinja environment on .env attribute; try to set it
        if hasattr(inst, "env"):
            from jinja2 import Environment, FileSystemLoader #Importing Jinja2 for templating
            template_path = os.path.join(os.path.dirname(__file__), "ResearchWriter", "src", "research_writer", "agents", "templates") #Setting the template path
            inst.env = Environment(loader=FileSystemLoader(template_path)) #Setting the environment
        return inst


def run_three_agents(task_id: str, repo_path: str, output_path: str, api_key: Optional[str]) -> None:
    """Orchestrate research -> writer -> deployment and update task store.

    Any exception is stored on the task record for inspection.
    """
    _update_task(task_id, status="running") #Update task status to running
    try:
        research_agent = safe_instantiate(ResearchAgent, api_key=api_key) #Instantiate Research Agent
        writer_agent = safe_instantiate(WriterAgent, api_key=api_key) #Instantiate Writer Agent
        deployment_agent = safe_instantiate(DeploymentAgent, api_key=api_key) #Instantiate Deployment Agent

        analysis = research_agent.analyze_repository(repo_path) #Analyze the repository
        _update_task(task_id, research=analysis) #Update task with research analysis

        # Writer will render docs; include deployment later
        writer_agent.generate_documentation(analysis, output_path) #Generate documentation
        _update_task(task_id, markdown_path=output_path) #Update task with markdown path

        # Attach deployment configs into analysis (non-destructive)
        deployment = deployment_agent.generate_deployment_config(analysis) #Generate deployment config
        analysis["deployment"] = deployment #Attach deployment to analysis
        _update_task(task_id, deployment=deployment, status="done") #Update task status to done
    except Exception as exc: #If there is an exception
        _update_task(task_id, status="error", error=str(exc)) #Update task status to error with the exception message


@app.route("/health", methods=["GET"])
def health() -> Response:
    return jsonify({"status": "ok"}) #Health check endpoint


@app.route("/agents/run", methods=["POST"]) 
def run_agents() -> Response: #Run the agents endpoint
    """Run the three agents in sequence.

    JSON payload:
      - repo_path: path to local git repo (required)
      - output_path: path to write documentation (optional, default ./docs/auto_docs.md)
      - api_key: optional OpenAI API key to initialize agents
      - background: run in background (bool)
    """
    data = request.get_json(silent=True) or {} #Data from the request
    repo_path = data.get("repo_path") or data.get("repo") #Getting the repository path
    if not repo_path: #If there is no repository path
        return jsonify({"error": "provide 'repo_path' in JSON payload"}), 400 #Return error
    output_path = data.get("output_path") or os.path.join(os.getcwd(), "docs", "auto_docs.md") #Getting the output path
    api_key = data.get("api_key") or os.environ.get("OPENAI_API_KEY") #Getting the API key
    background = bool(data.get("background", False)) #Getting the background flag

    task_id = str(uuid.uuid4()) #Generating a unique task ID
    _set_task(task_id, {"status": "queued", "repo_path": repo_path, "output_path": output_path}) #Setting the task in the task store

    if background:
        thread = threading.Thread(target=run_three_agents, args=(task_id, repo_path, output_path, api_key), daemon=True) #Creating a background thread to run the agents
        thread.start() #Starting the background thread
        return jsonify({"task_id": task_id}), 202 #Return task ID with 202 status

    run_three_agents(task_id, repo_path, output_path, api_key) #Run the three agents
    task = _get_task(task_id) #Retrieve the task from the task store
    return jsonify(task or {"task_id": task_id}) #Return task details


@app.route("/agents/task/<task_id>", methods=["GET"]) #This endpoint retrieves the task details
def get_task(task_id: str) -> Response: #Get the task details endpoint
    task = _get_task(task_id) #Retrieve the task from the task store
    if not task: #If the task is not found
        return jsonify({"error": "task not found"}), 404 #Return error
    return jsonify(task) #Return task details


@app.route("/agents/task/<task_id>/markdown", methods=["GET"]) #This endpoint retrieves the generated markdown documentation for a task
def get_task_markdown(task_id: str) -> Response: #Get the task markdown endpoint
    task = _get_task(task_id) #Retrieve the task from the task store
    if not task: #If the task is not found
        return jsonify({"error": "task not found"}), 404 #Return error
    path = task.get("markdown_path") #Getting the markdown path
    if not path or not os.path.exists(path): #If the path does not exist
        return jsonify({"error": "markdown not available", "status": task.get("status")}), 404 #Return error
    with open(path, "r") as f: #Open the markdown file
        return Response(f.read(), mimetype="text/markdown") #Return the markdown content


if __name__ == "__main__": #If this file is run directly
    port = int(os.environ.get("PORT", 8000)) #Getting the port from environment or default to 8000
    app.run(host="127.0.0.1", port=port, debug=True) #Run the Flask app
