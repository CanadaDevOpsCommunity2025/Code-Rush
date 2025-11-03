# Research Writer

A Python-based research and write agent that analyzes git repositories and generates comprehensive documentation using OpenAI's GPT models.

## Features

- Git repository analysis and code inspection using OpenAI
- Documentation generation in Markdown format
- Project structure analysis
- Code patterns and architecture documentation
- Dependency analysis
- Custom template support for documentation

## Prerequisites

1. Get an OpenAI API key from the [OpenAI Platform](https://platform.openai.com/account/api-keys)
2. Set up your API key in one of these ways:
   - Create a `.env` file based on `.env.example` and add your API key
   - Set the `OPENAI_API_KEY` environment variable
   - Pass the API key directly using the `--api-key` argument

Note: The project uses OpenAI's GPT models for analysis and documentation generation. Make sure you have a valid OpenAI API key and sufficient credits.

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## Usage

### Command Line

```bash
# Using environment variable or .env file
python -m research_writer --repo /path/to/repo --output documentation.md

# Using direct API key
python -m research_writer --repo /path/to/repo --output documentation.md --api-key your_api_key
```

### Docker

Build and run using Docker:

```bash
# Build the image
docker build -t research-writer .

# Run with environment file
docker run -v /path/to/repository:/repository --env-file .env research-writer --repo /repository --output /repository/documentation.md

# Run with direct API key
docker run -v /path/to/repository:/repository -e OPENAI_API_KEY=your_api_key research-writer --repo /repository --output documentation.md
```

### Python API

```python
from research_writer import RepoDocumentationCrew

# Initialize the crew (will use GOOGLE_API_KEY from environment)
crew = RepoDocumentationCrew()

# Or provide API key directly
crew = RepoDocumentationCrew(api_key="your_api_key")

# Generate documentation
crew.generate_documentation("path/to/repo", "documentation.md")
```

## Development

1. Clone the repository
2. Set up your OpenAI API key in `.env`:
   ```
   OPENAI_API_KEY=your_api_key
   ```
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
4. Run tests:
   ```bash
   pytest
   ```

## Notes

- The application uses OpenAI's GPT-3.5-turbo model by default
- Make sure you have sufficient API quota before running large repository analysis
- API costs are based on token usage during repository analysis and documentation generation

## License

MIT License