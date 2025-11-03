from typing import Dict, List
from crewai import Agent, Task
from git import Repo
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

class ResearchAgent:
    """Agent responsible for analyzing GitHub repositories."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the research agent.
        
        Args:
            api_key: OpenAI API key
        """
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key is None:
                raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        
        self.llm = ChatOpenAI(
            temperature=0.1,
            model_name="gpt-3.5-turbo"
        )
        
        self.agent = Agent(
            role='Research Analyst',
            goal='Thoroughly analyze GitHub repositories and extract key information',
            backstory="""You are an expert at analyzing code repositories and 
            understanding software architecture. You have extensive experience in 
            reviewing code bases and identifying patterns.""",
            allow_delegation=False,
            llm=self.llm,
            verbose=True
        )
        
    def analyze_repository(self, repo_path: str) -> Dict:
        """
        Analyze a GitHub repository and extract relevant information.
        
        Args:
            repo_path: Path to the local git repository
            
        Returns:
            Dictionary containing analysis results
        """
        repo = Repo(repo_path)
        
        # Collect basic repository information
        analysis = {
            "basic_info": self._get_basic_info(repo),
            "structure": self._analyze_structure(repo_path),
            "code_analysis": self._analyze_code(repo_path),
            "contributors": self._analyze_contributors(repo),
            "dependencies": self._analyze_dependencies(repo_path)
        }
        
        return analysis
    
    def _get_basic_info(self, repo: Repo) -> Dict:
        """Extract basic repository information."""
        return {
            "name": os.path.basename(repo.working_dir),
            "description": repo.description,
            "default_branch": repo.active_branch.name,
            "total_commits": sum(1 for _ in repo.iter_commits()),
            "branches": [branch.name for branch in repo.branches]
        }
    
    def _analyze_structure(self, repo_path: str) -> Dict:
        """Analyze the repository structure."""
        structure = {}
        for root, dirs, files in os.walk(repo_path):
            if ".git" in dirs:
                dirs.remove(".git")
            rel_path = os.path.relpath(root, repo_path)
            if rel_path == ".":
                structure["/"] = files
            else:
                structure[rel_path] = files
        return structure
    
    def _analyze_code(self, repo_path: str) -> Dict:
        """Analyze code patterns and architecture."""
        code_analysis = {
            "languages": self._detect_languages(repo_path),
            "architecture": self._identify_architecture(repo_path),
            "patterns": self._identify_patterns(repo_path)
        }
        return code_analysis
    
    def _detect_languages(self, repo_path: str) -> Dict[str, int]:
        """Detect programming languages used in the repository."""
        extensions = {}
        for root, _, files in os.walk(repo_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext:
                    extensions[ext] = extensions.get(ext, 0) + 1
        return extensions
    
    def _identify_architecture(self, repo_path: str) -> str:
        """Identify the software architecture pattern."""
        # This would use the LLM to analyze the codebase and identify architecture patterns
        task = Task(
            description=f"Analyze the codebase at {repo_path} and identify the main architectural pattern used.",
            expected_output="A detailed description of the architectural pattern used in the codebase"
        )
        return self.agent.execute_task(task)
    
    def _identify_patterns(self, repo_path: str) -> List[str]:
        """Identify common design patterns used in the code."""
        # This would use the LLM to analyze the codebase and identify design patterns
        task = Task(
            description=f"Analyze the codebase at {repo_path} and list the main design patterns used.",
            expected_output="A list of design patterns found in the codebase"
        )
        patterns_text = self.agent.execute_task(task)
        return patterns_text.split("\n")
    
    def _analyze_contributors(self, repo: Repo) -> List[Dict]:
        """Analyze repository contributors."""
        contributors = []
        for commit in repo.iter_commits():
            contributor = {
                "name": commit.author.name,
                "email": commit.author.email,
                "commits": 1
            }
            if contributor not in contributors:
                contributors.append(contributor)
            else:
                idx = contributors.index(contributor)
                contributors[idx]["commits"] += 1
        return contributors
    
    def _analyze_dependencies(self, repo_path: str) -> Dict:
        """Analyze project dependencies."""
        dependencies = {
            "python": self._analyze_python_dependencies(repo_path),
            "javascript": self._analyze_js_dependencies(repo_path),
        }
        return dependencies
    
    def _analyze_python_dependencies(self, repo_path: str) -> Dict:
        """Analyze Python dependencies."""
        dependencies = {}
        req_file = os.path.join(repo_path, "requirements.txt")
        setup_file = os.path.join(repo_path, "setup.py")
        pyproject_file = os.path.join(repo_path, "pyproject.toml")
        
        if os.path.exists(req_file):
            with open(req_file) as f:
                dependencies["requirements.txt"] = f.read().splitlines()
        if os.path.exists(setup_file):
            dependencies["setup.py"] = "Found but not parsed"
        if os.path.exists(pyproject_file):
            dependencies["pyproject.toml"] = "Found but not parsed"
            
        return dependencies
    
    def _analyze_js_dependencies(self, repo_path: str) -> Dict:
        """Analyze JavaScript dependencies."""
        dependencies = {}
        package_json = os.path.join(repo_path, "package.json")
        
        if os.path.exists(package_json):
            dependencies["package.json"] = "Found but not parsed"
            
        return dependencies