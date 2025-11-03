from crewai import Crew, Process
from research_writer.agents.research_agent import ResearchAgent
from research_writer.agents.writer_agent import WriterAgent
from research_writer.agents.deployment_agent import DeploymentAgent
import os
from dotenv import load_dotenv

class RepoDocumentationCrew:
    """Orchestrates the repository analysis and documentation generation process."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the documentation crew.
        
        Args:
            api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY in environment.
        """
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key is None:
                raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        
        self.research_agent = ResearchAgent(api_key=api_key)
        self.writer_agent = WriterAgent(api_key=api_key)
        self.deployment_agent = DeploymentAgent(api_key=api_key)
        
        self.crew = Crew(
            agents=[self.research_agent.agent, self.writer_agent.agent, self.deployment_agent.agent],
            tasks=[],
            process=Process.sequential,
            verbose=True
        )
    
    def generate_documentation(self, repo_path: str, output_path: str, include_deployment: bool = True) -> None:
        """
        Analyze repository and generate documentation.
        
        Args:
            repo_path: Path to the git repository
            output_path: Path where documentation should be saved
            include_deployment: Whether to include deployment configurations
        """
        # Ensure the repository path exists
        if not os.path.exists(repo_path):
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        # Analyze the repository
        analysis_results = self.research_agent.analyze_repository(repo_path)
        
        # Generate deployment configurations if requested
        if include_deployment:
            deployment_configs = self.deployment_agent.generate_deployment_config(analysis_results)
            analysis_results['deployment'] = deployment_configs
        
        # Generate documentation
        self.writer_agent.generate_documentation(analysis_results, output_path)

def main():
    # Example usage
    crew = RepoDocumentationCrew()
    
    # Replace these paths with actual paths
    repo_path = "path/to/repository"
    output_path = "path/to/output/documentation.md"
    
    crew.generate_documentation(repo_path, output_path)

if __name__ == "__main__":
    main()