# Contributing to Financial Doc Chatbot

Thank you for your interest in contributing! Here's how to get started.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/JRA-CodingLab/financial-doc-chatbot.git
   cd financial-doc-chatbot
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

## Running Tests

```bash
pytest
```

Tests mock all external services (OpenAI, ChromaDB), so no API keys are needed to run them.

## Code Style

- Follow PEP 8.
- Use type hints where practical.
- Write docstrings for public functions and classes.

## Pull Request Process

1. Fork the repo and create a feature branch from `main`.
2. Add or update tests for your changes.
3. Ensure all tests pass (`pytest`).
4. Update documentation if behavior changes.
5. Open a PR with a clear description of what and why.

## Reporting Issues

Open a GitHub issue with:
- Steps to reproduce
- Expected vs. actual behavior
- Python version and OS

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
