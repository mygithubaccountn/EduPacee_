# Contributing to EduPace

Thank you for your interest in contributing to EduPace! This document provides guidelines and instructions for contributing to the project.

## Getting Started

1. **Fork the repository** (if working with GitHub)
2. **Clone your fork**:
   ```bash
   git clone <your-fork-url>
   cd EduPacee_-main
   ```

3. **Set up your development environment**:
   - Follow the installation instructions in [README.md](README.md)
   - Make sure all tests pass before making changes

## Contribution Guidelines

### Code Changes

- **Keep changes simple and focused**: Make small, incremental changes
- **Don't modify core functionality** without team discussion
- **Test your changes** before submitting
- **Follow existing code style** and conventions

### Safe Changes (Recommended for New Contributors)

These are safe areas to contribute without affecting core functionality:

- ✅ Documentation improvements (README, comments, docstrings)
- ✅ `.gitignore` enhancements
- ✅ Code formatting and style improvements
- ✅ Adding helpful comments to existing code
- ✅ Bug fixes (with team approval)
- ✅ UI/UX improvements (templates, CSS)

### Changes Requiring Team Discussion

⚠️ **Please discuss with the team before making these changes:**

- Database model modifications
- Core view functions
- Authentication/permission logic
- URL routing changes
- Settings.py modifications
- Migration files

## Workflow

1. **Create a branch** for your changes:
   ```bash
   git checkout -b your-name/feature-description
   ```

2. **Make your changes** following the guidelines above

3. **Test your changes**:
   ```bash
   python manage.py test
   python manage.py runserver  # Test manually
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Brief description of your changes"
   ```

5. **Push to your fork**:
   ```bash
   git push origin your-name/feature-description
   ```

6. **Create a Pull Request** (if using GitHub) or share your changes with the team

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and small
- Use Django best practices

## Documentation

- Update README.md if you add new features
- Add docstrings to new functions/classes
- Update this CONTRIBUTING.md if you add new guidelines

## Questions?

If you have questions about contributing:
- Check existing code for examples
- Review Django documentation
- Ask your team members
- Check the README.md for project structure

## Thank You!

Your contributions help make EduPace better for everyone! 🎓

