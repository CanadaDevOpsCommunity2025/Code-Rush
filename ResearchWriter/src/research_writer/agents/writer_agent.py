from typing import Dict, List
from crewai import Agent, Task
import os
import markdown
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

class WriterAgent:
    """Agent responsible for writing documentation based on repository analysis."""
    
    def __init__(self, api_key: str = None,
                 template_path: str = None):
        """
        Initialize the writer agent.
        
        Args:
            api_key: OpenAI API key
            template_path: Optional path to custom templates directory
        """
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key is None:
                raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-3.5-turbo"
        )
        
        self.agent = Agent(
            role='Technical Writer',
            goal='Create clear, comprehensive documentation from repository analysis',
            backstory="""You are an expert technical writer with years of experience 
            in creating software documentation. You excel at explaining complex 
            technical concepts in a clear and organized manner.""",
            allow_delegation=False,
            llm=self.llm,
            verbose=True
        )
        
        self.template_path = template_path or os.path.join(
            os.path.dirname(__file__), "templates"
        )
        self.env = Environment(loader=FileSystemLoader(self.template_path))
    
    def generate_documentation(self, analysis_results: Dict, output_path: str) -> None:
        """
        Generate documentation from repository analysis results.
        
        Args:
            analysis_results: Dictionary containing repository analysis
            output_path: Path where documentation should be saved
        """
        # Generate each section of the documentation
        sections = {
            "overview": self._generate_overview(analysis_results),
            "architecture": self._generate_architecture(analysis_results),
            "code_analysis": self._generate_code_analysis(analysis_results),
            "structure": self._generate_structure(analysis_results),
            "contributors": self._generate_contributors(analysis_results),
            "dependencies": self._generate_dependencies(analysis_results),
        }
        
        # Add deployment section if available
        if 'deployment' in analysis_results:
            sections["deployment"] = self._generate_deployment_section(analysis_results['deployment'])
        
        # Combine all sections
        doc = self._combine_sections(sections)
        
        # Save the documentation
        self._save_documentation(doc, output_path)
    
    def _generate_overview(self, analysis: Dict) -> str:
        """Generate the overview section using the agent."""
        task = Task(
            description=f"""Create a clear overview section for the repository documentation
            using this information: {analysis['basic_info']}
            
            Focus on:
            1. Repository name and purpose
            2. Key statistics (branches, commits)
            3. High-level description""",
            expected_output="A comprehensive overview section for the documentation"
        )
        return self.agent.execute_task(task)
    
    def _generate_architecture(self, analysis: Dict) -> str:
        """Generate the architecture section using the agent."""
        task = Task(
            description=f"""Create a detailed architecture section based on this analysis:
            {analysis['code_analysis']['architecture']}
            
            Explain:
            1. The overall architectural pattern
            2. Key components and their interactions
            3. Design decisions and their rationale""",
            expected_output="A detailed description of the repository's architecture"
        )
        return self.agent.execute_task(task)
    
    def _generate_code_analysis(self, analysis: Dict) -> str:
        """Generate the code analysis section using the agent."""
        task = Task(
            description=f"""Create a comprehensive code analysis section using this information:
            {analysis['code_analysis']}
            
            Include:
            1. Programming languages used and their distribution
            2. Design patterns identified
            3. Code organization and structure""",
            expected_output="A detailed analysis of the codebase"
        )
        return self.agent.execute_task(task)
    
    def _generate_structure(self, analysis: Dict) -> str:
        """Generate the structure section."""
        template = self.env.get_template("structure.md.j2")
        return template.render(structure=analysis["structure"])
    
    def _generate_contributors(self, analysis: Dict) -> str:
        """Generate the contributors section."""
        template = self.env.get_template("contributors.md.j2")
        return template.render(contributors=analysis["contributors"])
    
    def _generate_dependencies(self, analysis: Dict) -> str:
        """Generate the dependencies section."""
        template = self.env.get_template("dependencies.md.j2")
        return template.render(dependencies=analysis["dependencies"])
    
    def _combine_sections(self, sections: Dict[str, str]) -> str:
        """Combine all documentation sections."""
        template = self.env.get_template("main.md.j2")
        return template.render(sections=sections)
    
    def _generate_deployment_section(self, deployment_configs: Dict) -> str:
        """Generate the deployment configuration section."""
        task = Task(
            description=f"""Create a comprehensive deployment section using these configurations:
            Docker: {deployment_configs.get('docker')}
            Kubernetes: {deployment_configs.get('k8s')}
            CI/CD: {deployment_configs.get('ci_cd')}
            Environment Variables: {deployment_configs.get('env_vars')}
            
            Include:
            1. Detailed explanation of deployment approach
            2. Instructions for building and deploying
            3. Configuration details
            4. Environment setup requirements""",
            expected_output="A detailed deployment configuration section"
        )
        return self.agent.execute_task(task)

    def _save_documentation(self, content: str, output_path: str) -> None:
        """Save the documentation to file."""
        # Convert markdown to HTML if output is HTML
        if output_path.endswith('.html'):
            content = markdown.markdown(content)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write the file
        with open(output_path, 'w') as f:
            f.write(content)