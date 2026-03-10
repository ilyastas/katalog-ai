# 🧪 Quick Test Commands

# Basic test run
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=backend --cov-report=html

# Only API tests
pytest tests/test_api/ -v

# Only unit tests (when created)
pytest tests/ -v -m unit

# Specific test
pytest tests/test_api/test_recommend.py::TestRecommendEndpoint::test_recommend_simple_query -v

# Fast tests (skip slow/integration)
pytest tests/ -v -m "not slow and not integration"

# Parallel execution (faster)
# pip install pytest-xdist
pytest tests/ -n auto

# With detailed output
pytest tests/ -vv -s

# Stop on first failure
pytest tests/ -x

# Re-run failed tests
pytest tests/ --lf -v

# Coverage with minimum threshold
pytest --cov=backend --cov-fail-under=70

# Open HTML coverage report
# Windows:
Start-Process htmlcov/index.html
# Mac/Linux:
# open htmlcov/index.html
