# Contributing to N1O1 Clinical Trials

Thank you for your interest in contributing to the N1O1 Clinical Trials platform! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Respect differing viewpoints and experiences

## How to Contribute

### Reporting Issues

1. Check existing issues to avoid duplicates
2. Use issue templates when available
3. Provide detailed information:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment details

### Suggesting Features

1. Open a feature request issue
2. Describe the problem it solves
3. Propose your solution
4. Discuss alternatives considered

### Contributing Code

#### Setup Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/N1o1-Clinical-Trial-AI.git
   cd N1o1-Clinical-Trial-AI
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Copy environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

#### Development Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following our coding standards

3. Write/update tests:
   ```bash
   pytest tests/
   ```

4. Run linting (when available):
   ```bash
   flake8 .
   black .
   ```

5. Commit with descriptive messages:
   ```bash
   git commit -m "feat: add new simulation parameter for hypoxia"
   ```

6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

7. Open a Pull Request

## Coding Standards

### Python Style Guide

- Follow PEP 8
- Use meaningful variable names
- Add docstrings to all functions and classes
- Keep functions focused and small
- Use type hints where appropriate

### Example:
```python
def calculate_nitrite_clearance(
    concentration: float, 
    egfr: float = 90.0
) -> float:
    """
    Calculate nitrite clearance based on kidney function.
    
    Args:
        concentration: Plasma nitrite concentration in µM
        egfr: Estimated glomerular filtration rate in mL/min
        
    Returns:
        Clearance rate in µM/min
    """
    return concentration * (egfr / 60.0) * 0.1
```

### JavaScript Style Guide

- Use ES6+ features
- Prefer const/let over var
- Use meaningful component names
- Add JSDoc comments

### Git Commit Messages

Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Maintenance tasks

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_simulation.py
```

### Writing Tests

- Write tests for all new features
- Maintain test coverage above 80%
- Use descriptive test names
- Test edge cases

Example:
```python
def test_nitrite_simulation_with_renal_impairment():
    """Test simulation accurately models reduced clearance with low eGFR"""
    sim = NODynamicsSimulator(dose=30.0, egfr=30.0)
    results = sim.simulate()
    
    # Verify higher AUC with impaired renal function
    assert results['auc'] > normal_auc
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update API documentation for endpoint changes
- Include examples in documentation

## Pull Request Process

1. Ensure all tests pass
2. Update documentation
3. Add entry to CHANGELOG (if exists)
4. Request review from maintainers
5. Address review feedback
6. Squash commits if requested

### PR Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No sensitive data included
- [ ] Dependencies updated in requirements.txt

## Release Process

1. Version numbering follows Semantic Versioning
2. Releases are tagged in git
3. Changelog is updated
4. Documentation is versioned

## Getting Help

- Open an issue for questions
- Join our discussions
- Email: research@n1o1trials.com

## Recognition

Contributors will be recognized in:
- Contributors file
- Release notes
- Project documentation

Thank you for contributing to advancing clinical research! 🚀🧬
