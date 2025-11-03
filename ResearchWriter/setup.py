from setuptools import setup, find_packages

setup(
    name="research_writer",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "crewai>=0.12.2",
        "gitpython>=3.1.40",
        "langchain>=0.1.4",
        "langchain-community>=0.0.13",
        "langchain-openai>=0.0.5",
        "python-dotenv>=1.0.0",
        "PyGithub>=2.1.1",
        "markdown>=3.5",
        "jinja2>=3.1.2",
        "requests>=2.31.0",
        "tqdm>=4.66.1",
        "openai>=1.10.0",
    ],
    extras_require={
        "dev": ["pytest>=7.4.3"],
    },
    python_requires=">=3.8",
)