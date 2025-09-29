# Contributing to E-Commerce AI Agent

First off, thank you for considering contributing to this project! 🎉

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version)

### Suggesting Features

Feature suggestions are welcome! Please create an issue describing:
- The feature you'd like to see
- Why it would be useful
- How it might work

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes thoroughly
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ecom-agent.git
cd ecom-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# Create database
python create_sample_data.py

# Run tests
python test_app.py

# Start development server
python app.py
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and small
- Write meaningful variable names

### Testing

Before submitting a PR:
1. Run the diagnostic test: `python test_app.py`
2. Test all CRUD operations manually
3. Check both web and CLI interfaces
4. Verify documentation is updated

### Documentation

If you add features:
- Update relevant .md files
- Add examples to example_transcripts.md
- Update ARCHITECTURE.md if architecture changes

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

## Questions?

Feel free to open an issue for any questions about contributing!

---

**Thank you for helping make this project better!** 🚀