# Contributing to OpenSDR

Thank you for your interest in contributing to OpenSDR! We welcome contributions of all kinds: bug fixes, documentation improvements, new enrichment providers, and feature requests.

---

## Development Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/PatelDeepB/open-sdr.git
   cd open-sdr
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies in Editable Mode with Dev Tools**
   ```bash
   pip install -e .[dev]
   ```

4. **Run Tests to Verify Setup**
   ```bash
   pytest
   ```

---

## Contribution Workflow

1. Create a descriptive feature branch:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. Write clean, readable code with type hints.
3. Keep functions under 40 lines and add unit tests following the AAA pattern (Arrange, Act, Assert).
4. Run `pytest` and ensure all tests pass.
5. Add your changes to `CHANGELOG.md` under `[Unreleased]`.
6. Submit a Pull Request targeting `main`.

---

## Code Style Guidelines

- Python 3.10+ modern syntax with type annotations.
- Descriptive, intention-revealing names.
- Explicit error handling over silent failure.
- Zero required paid API keys for base functionality.
