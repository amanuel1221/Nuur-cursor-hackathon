# Contributing to NuuR

Thank you for your interest in contributing to NuuR! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Your environment (OS, browser, etc.)

### Suggesting Features

1. Check if the feature has been suggested
2. Create a new issue with "Feature Request" label
3. Describe the feature and its use case
4. Explain why it would be valuable

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write/update tests
5. Ensure all tests pass
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request

### Development Setup

See README.md for local development setup instructions.

### Code Style

#### Python (Backend)
- Follow PEP 8
- Use Black for formatting
- Use type hints
- Write docstrings for functions

#### TypeScript/React (Frontend)
- Use ESLint configuration
- Follow React best practices
- Use functional components with hooks
- Write prop types

### Testing

- Write unit tests for new features
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage

### Commit Messages

Use conventional commits format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: feat, fix, docs, style, refactor, test, chore

Example:
```
feat(anti-theft): add SMS trigger validation

Added validation for trigger keyword length and format.
Improved error messages for invalid keywords.

Closes #123
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

