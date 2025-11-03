# DevOps GenAI Hackathon - 3rd November, 2025 - Contributors

## Ranjana - 
Prepared the presentation for project and explored agents.Tried making the message rounter. worked on creating a files for reddis queue for dispatching tasks to right agent, but issue in deploying.

## Ram -Developement of the ResearchWriter component, implementing a sophisticated multi-agent system using CrewAI framework:
- Designed and implemented three specialized AI agents:
  - Research Agent: Analyzes git repositories using OpenAI's GPT-3.5-turbo for code pattern recognition
  - Writer Agent: Generates comprehensive documentation using templates and NLP
  - Deployment Agent: Handles project setup and configuration management
- Technical Contributions:
  - Integrated OpenAI's GPT-3.5-turbo model with LangChain for advanced code analysis
  - Implemented efficient repository scanning using GitPython
  - Created Jinja2 templates for standardized documentation generation
  - Set up comprehensive Python development environment with modern dependency management
- DevOps Implementation:
  - Containerized the application using Docker with multi-stage builds
  - Created docker-compose setup for easy deployment
  - Implemented environment management with python-dotenv
  - Set up proper project structure following Python best practices

## Surya - 
Designed, implemented, and optimized a complete CI/CD pipeline using GitHub Actions to automate the build, test, and deployment process for containerized applications. Configured self-hosted GitHub runners on a local workstation to enable custom execution environments, providing full control over build dependencies, compute resources, and pipeline performance.

Installed and configured Docker for containerization and Minikube to emulate a local Kubernetes environment for development and testing. The solution enables seamless packaging of application code into Docker images, pushing images to a container registry, and deploying workloads to the local Kubernetes cluster for validation.

A key objective of the pipeline is to integrate with an AI-driven automation engine capable of generating Kubernetes-compatible YAML manifests dynamically. The CI/CD workflow is designed to automatically retrieve and apply these YAML files to the Minikube cluster. This ensures a fully automated infrastructure-as-code deployment path, where application and infrastructure components are both programmatically generated and deployed.

This AI-based YAML integration is currently under active development, with plans to expand functionality to support parameterized deployments, error handling, and automated policy validation

## Rishi
My contributions were to try to create the API on which our program would run. This was unknown territory to me, so I heavily relied on agentic AI with GitHub Copilot, the model being used was GPT-5 mini by OpenAI.
