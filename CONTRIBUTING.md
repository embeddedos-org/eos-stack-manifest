# Contributing to eFab

Thank you for contributing to the EmbeddedOS project! We welcome contributions from the community.

## Development Standards

This project is benchmarked against world-class embedded systems projects:
- **Zephyr RTOS** — Apache-2.0, 1000+ contributors, 500+ boards
- **FreeRTOS** — MIT, 35+ years of embedded RTOS expertise
- **Linux Kernel** — The gold standard for OS development
- **LLVM/Clang** — World-class compiler infrastructure

## Code Quality Requirements

1. **Test Coverage**: All new code must maintain ≥80% test coverage
2. **Test Types**: Unit, functional, performance, and simulation tests required
3. **Static Analysis**: Code must pass `clang-tidy` and `cppcheck` with zero warnings
4. **Documentation**: All public APIs must be documented with Doxygen
5. **Performance**: No regression in benchmark tests (see `tests/performance/`)
6. **Security**: No new CWE/SANS Top 25 vulnerabilities

## Pull Request Process

1. Fork the repository and create a feature branch
2. Implement changes with tests
3. Run the full test suite: `python3 run_all_tests.py`
4. Ensure CI/CD passes all checks
5. Submit PR with description of changes and test results

## Coding Style

- **C**: Follow Linux kernel coding style (tabs, 80-char lines)
- **Python**: PEP 8 with type hints
- **Go**: `gofmt` formatted
- **TypeScript**: ESLint with strict mode

## Testing

```bash
# Run all tests
python3 run_all_tests.py

# Run specific test category
python3 -m pytest tests/unit/ -v
python3 -m pytest tests/functional/ -v
python3 -m pytest tests/performance/ -v
python3 -m pytest tests/simulation/ -v
```

## Simulation & Emulation

Hardware simulation tests can be run without physical hardware:
```bash
python3 -m pytest tests/simulation/ -v --sim-mode=host
```
