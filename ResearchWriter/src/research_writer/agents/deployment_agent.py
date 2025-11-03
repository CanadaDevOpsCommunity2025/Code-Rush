from typing import Dict, List
from crewai import Agent, Task
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

class DeploymentAgent:
    """Agent responsible for generating deployment configurations based on repository analysis."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the deployment agent.
        
        Args:
            api_key: OpenAI API key
        """
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key is None:
                raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        
        self.llm = ChatOpenAI(
            temperature=0.3,  # Lower temperature for more deterministic responses
            model_name="gpt-3.5-turbo"
        )
        
        self.agent = Agent(
            role='Deployment Engineer',
            goal='Create comprehensive deployment configurations based on repository analysis',
            backstory="""You are an expert DevOps engineer with extensive experience in 
            creating deployment configurations for various types of applications. You excel 
            at analyzing codebases and determining the optimal deployment setup.""",
            allow_delegation=False,
            llm=self.llm,
            verbose=True
        )

    def generate_deployment_config(self, repo_analysis: Dict) -> Dict:
        """
        Generate deployment configurations based on repository analysis.
        
        Args:
            repo_analysis: Dictionary containing repository analysis results
            
        Returns:
            Dictionary containing deployment configurations
        """
        configs = {
            "docker": self._generate_dockerfile(repo_analysis),
            "k8s": self._generate_kubernetes_config(repo_analysis) if self._needs_kubernetes(repo_analysis) else None,
            "ci_cd": self._generate_ci_cd_config(repo_analysis),
            "env_vars": self._identify_env_variables(repo_analysis)
        }
        return configs

    def _generate_dockerfile(self, analysis: Dict) -> str:
        """Generate a Dockerfile based on the repository analysis."""
        task = Task(
            description=f"""Create a Dockerfile for the repository with these characteristics:
            Languages: {analysis.get('code_analysis', {}).get('languages', {})}
            Dependencies: {analysis.get('dependencies', {})}
            
            Focus on:
            1. Appropriate base image selection
            2. Dependency installation
            3. Build and runtime stages if needed
            4. Security best practices
            5. Optimized layer caching""",
            expected_output="A complete Dockerfile content with comments explaining each step"
        )
        return self.agent.execute_task(task)

    def _generate_kubernetes_config(self, analysis: Dict) -> str:
        """Generate Kubernetes configuration files if needed."""
        task = Task(
            description=f"""Create Kubernetes deployment and service configurations for:
            Application: {analysis.get('basic_info', {}).get('name')}
            Architecture: {analysis.get('code_analysis', {}).get('architecture')}
            
            Include:
            1. Deployment configuration
            2. Service configuration
            3. ConfigMap/Secret templates if needed
            4. Resource requests/limits
            5. Health checks""",
            expected_output="Complete Kubernetes YAML configurations"
        )
        return self.agent.execute_task(task)

    def _needs_kubernetes(self, analysis: Dict) -> bool:
        """Determine if the application needs Kubernetes deployment."""
        # Check for indicators that suggest Kubernetes might be needed
        dependencies = analysis.get('dependencies', {})
        has_k8s_files = any('kubernetes' in str(file).lower() for file in analysis.get('structure', {}).values())
        has_microservices = 'microservices' in str(analysis.get('code_analysis', {}).get('architecture', '')).lower()
        
        return has_k8s_files or has_microservices

    def _generate_ci_cd_config(self, analysis: Dict) -> str:
        """Generate CI/CD pipeline configuration."""
        task = Task(
            description=f"""Create a CI/CD pipeline configuration for:
            Repository: {analysis.get('basic_info', {}).get('name')}
            Branches: {analysis.get('basic_info', {}).get('branches', [])}
            
            Include:
            1. Build steps
            2. Test execution
            3. Security scanning
            4. Deployment stages
            5. Environment-specific configurations""",
            expected_output="A complete CI/CD pipeline configuration file"
        )
        return self.agent.execute_task(task)

    def _identify_env_variables(self, analysis: Dict) -> List[str]:
        """Identify required environment variables from the codebase."""
        task = Task(
            description=f"""Analyze the codebase and identify required environment variables:
            Dependencies: {analysis.get('dependencies', {})}
            File Structure: {analysis.get('structure', {})}
            
            Focus on:
            1. Configuration variables
            2. API keys and credentials
            3. Database connections
            4. External service configurations""",
            expected_output="A list of required environment variables with descriptions"
        )
        return self.agent.execute_task(task)