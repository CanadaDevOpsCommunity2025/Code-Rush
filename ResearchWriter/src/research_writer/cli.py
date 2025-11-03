#!/usr/bin/env python3
import argparse
import os
from research_writer.main import RepoDocumentationCrew
from dotenv import load_dotenv

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate documentation for a Git repository using AI agents"
    )
    
    parser.add_argument(
        "--repo",
        required=True,
        help="Path to the Git repository"
    )
    
    parser.add_argument(
        "--output",
        default="documentation.md",
        help="Path to save the generated documentation (default: documentation.md)"
    )
    
    parser.add_argument(
        "--api-key",
        help="OpenAI API key. If not provided, will look for OPENAI_API_KEY in environment."
    )
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Validate repository path
    if not os.path.exists(args.repo):
        print(f"Error: Repository path does not exist: {args.repo}")
        return 1
    
        # Load API key from environment if not provided
    api_key = args.api_key
    if api_key is None:
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            print("Error: OpenAI API key not found. Please either:")
            print("1. Set the OPENAI_API_KEY environment variable")
            print("2. Create a .env file with OPENAI_API_KEY=your_key")
            print("3. Provide the API key using --api-key argument")
            return 1
    
    try:
        # Initialize the documentation crew
        crew = RepoDocumentationCrew(api_key=api_key)
        
        # Generate documentation
        print(f"Analyzing repository: {args.repo}")
        crew.generate_documentation(args.repo, args.output)
        
        print(f"Documentation generated successfully: {args.output}")
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())