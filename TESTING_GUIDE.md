# 🧪 TESTING GUIDE — Полное руководство по тестированию Katalog-AI

> 📅 Обновлено: 10 марта 2026 г.  
> 🎯 Цель: Грамотное и комплексное тестирование всех компонентов репозитория

---

## 📊 Текущее состояние тестов

### ✅ Что уже есть:

| Компонент | Путь | Статус | Покрытие |
|-----------|------|--------|----------|
| **Recommend API** | `tests/test_api/test_recommend.py` | ✅ Готово | ~60% |
| **CI/CD Pipeline** | `.github/workflows/ci.yml` | ✅ Настроен | Lint + Tests |
| **Docker Compose** | `docker-compose.yml` | ✅ Есть | PostgreSQL + Neo4j + Redis |

### ❌ Что отсутствует:

- ❌ Тесты для `verification` API
- ❌ Тесты для `analytics` API
- ❌ Тесты для `openai_chat` API
- ❌ Unit тесты для `services/`
- ❌ Unit тесты для `verifiers/`
- ❌ Integration тесты (Neo4j + PostgreSQL)
- ❌ E2E тесты (полный флоу)
- ❌ Performance тесты
- ❌ `pytest.ini` конфигурация

---

## 🎯 СТРАТЕГИЯ ТЕСТИРОВАНИЯ

### 1️⃣ Пирамида тестов

```
        /\
       /  \      E2E Tests (5%)
      /    \     - Полный user flow
     /------\    - Реальная инфраструктура
    /        \   
   /          \  Integration Tests (25%)
  /            \ - API + Database
 /              \- Services взаимодействие
/----------------\
|  Unit Tests    | Unit Tests (70%)
|   (70%)        | - Изолированные модули
|                | - Mock dependencies
------------------
```

### 2️⃣ Типы тестов

| Тип | Цель | Инструменты | Когда запускать |
|-----|------|-------------|----------------|
| **Unit** | Изоляция логики | pytest + mocks | Каждый коммит |
| **Integration** | API + DB | pytest + TestClient | Pre-push, PR |
| **E2E** | Full flow | pytest + docker | Pre-release |
| **Performance** | Нагрузка/скорость | locust/pytest-benchmark | Weekly |
| **Security** | Уязвимости | bandit, safety | PR, Release |

---

## 🚀 БЫСТРЫЙ СТАРТ — Тестирование за 5 минут

### ✅ Шаг 1: Установка зависимостей

```bash
# Активируем виртуальное окружение (если есть)
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# или
source .venv/bin/activate     # Linux/Mac

# Устанавливаем тестовые зависимости
pip install -r backend/requirements.txt
pip install pytest pytest-cov pytest-asyncio httpx
```

### ✅ Шаг 2: Запуск существующих тестов

```bash
# Простой запуск (только готовые тесты)
pytest tests/ -v

# С покрытием кода
pytest tests/ -v --cov=backend --cov-report=html

# Только быстрые тесты (без интеграции)
pytest tests/ -v -m "not integration"

# Конкретный модуль
pytest tests/test_api/test_recommend.py -v

# Конкретный тест
pytest tests/test_api/test_recommend.py::TestRecommendEndpoint::test_recommend_simple_query -v
```

### ✅ Шаг 3: Просмотр покрытия

```bash
# Открыть HTML отчет
Start-Process htmlcov/index.html  # Windows
# или
open htmlcov/index.html           # Mac
# или
xdg-open htmlcov/index.html       # Linux
```

---

## 🏗️ ПОЛНОЕ ТЕСТИРОВАНИЕ — Комплексный подход

### Вариант А: **Локальное тестирование** (без Docker)

**Требования:**
- SQLite (для unit тестов) — ✅ встроен в Python
- Mock для внешних API

```bash
# 1. Быстрые unit тесты (БЕЗ реальной инфраструктуры)
pytest tests/ -v --cov=backend --cov-report=term-missing

# 2. Только API тесты
pytest tests/test_api/ -v

# 3. С подробным выводом
pytest tests/ -vv -s
```

**Плюсы:** Быстро, не требует Docker  
**Минусы:** Не покрывает Neo4j, PostgreSQL, Redis

---

### Вариант Б: **Docker Compose тестирование** (полная инфраструктура)

**Требования:**
- Docker Desktop запущен
- PostgreSQL + Neo4j + Redis контейнеры

```bash
# 1. Запустить инфраструктуру
docker-compose up -d postgres redis neo4j

# 2. Дождаться healthcheck
docker-compose ps

# 3. Запустить тесты с реальной БД
$env:DATABASE_URL="postgresql://alie_user:postgres123@localhost:5432/alie_db"
$env:REDIS_URL="redis://localhost:6379"
$env:NEO4J_URI="bolt://localhost:7687"
$env:NEO4J_USER="neo4j"
$env:NEO4J_PASSWORD="password123"

pytest tests/ -v --cov=backend --cov-report=html

# 4. Остановить инфраструктуру
docker-compose down
```

**Плюсы:** Полное покрытие, реальная среда  
**Минусы:** Медленнее, требует Docker

---

### Вариант В: **GitHub Actions CI/CD** (автоматизация)

**Автоматически запускается:**
- ✅ При push в `main` или `develop`
- ✅ При создании Pull Request
- ✅ Включает lint + unit tests + build

**Проверить статус:**
```bash
# Открыть GitHub Actions
start https://github.com/ilyastas/katalog-ai/actions
```

**Workflow файл:** [.github/workflows/ci.yml](.github/workflows/ci.yml)

---

## 📦 СТРУКТУРА ТЕСТОВ (целевая)

```
tests/
├── __init__.py
├── conftest.py                 # ❌ СОЗДАТЬ: Общие fixtures
│
├── unit/                       # ❌ СОЗДАТЬ: Unit тесты (70%)
│   ├── test_services.py        # RecommenderService, TrackingService
│   ├── test_verifiers.py       # 2GIS, Google, OLX verifiers
│   ├── test_trust_scorer.py    # Trust score calculation
│   ├── test_models.py          # SQLAlchemy models
│   └── test_utils.py           # Утилиты
│
├── integration/                # ❌ СОЗДАТЬ: Integration тесты (25%)
│   ├── test_verification_flow.py  # Верификация → Trust score
│   ├── test_recommendation_flow.py # Поиск → Ranking → Ответ
│   ├── test_neo4j_queries.py      # Graph DB запросы
│   └── test_celery_tasks.py       # Background jobs
│
├── e2e/                        # ❌ СОЗДАТЬ: E2E тесты (5%)
│   ├── test_full_user_journey.py  # Полный флоу пользователя
│   └── test_data_pipeline.py      # Обновление каталога → embeddings
│
└── test_api/                   # ✅ УЖЕ ЕСТЬ: API тесты
    └── test_recommend.py       # Recommend endpoints
```

---

## 🛠️ СОЗДАНИЕ ТЕСТОВ — Пошаговая инструкция

### 📝 Шаг 1: Создать `pytest.ini`

```bash
# Создаем конфигурацию pytest
cat > pytest.ini << 'EOF'
[pytest]
# Пути для поиска тестов
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Маркеры для категоризации
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (DB required)
    e2e: End-to-end tests (full stack required)
    slow: Slow tests (>3 seconds)
    api: API endpoint tests
    services: Service layer tests
    verifiers: External API verifier tests

# Coverage настройки
addopts =
    -ra
    -v
    --strict-markers
    --cov=backend
    --cov-branch
    --cov-report=term-missing:skip-covered
    --cov-report=html
    --cov-report=xml
    --maxfail=5
    --tb=short

# Async support
asyncio_mode = auto

# Предупреждения
filterwarnings =
    error
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
EOF
```

### 📝 Шаг 2: Создать `conftest.py` (общие fixtures)

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from backend.main import app
from backend.core.database import Base, get_db

# Test database
TEST_DATABASE_URL = "sqlite:///./test_katalog.db"

@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    # Cleanup
    if os.path.exists("./test_katalog.db"):
        os.remove("./test_katalog.db")

@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create test database session"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=test_engine
    )
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with overridden dependencies"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_business(db_session):
    """Create sample business for testing"""
    from backend.core.database import Business
    
    business = Business(
        business_id="test-001",
        name="Test Business",
        category="beauty",
        city="Алматы",
        phone="+7-700-000-00-00",
        email="test@test.kz",
        trust_score=0.8,
        verified_by_2gis=True
    )
    db_session.add(business)
    db_session.commit()
    db_session.refresh(business)
    return business
```

### 📝 Шаг 3: Создать unit тесты для services

```python
# tests/unit/test_recommender_service.py
import pytest
from unittest.mock import Mock, patch, AsyncMock

from backend.services.recommender import RecommenderService


@pytest.mark.unit
class TestRecommenderService:
    """Unit tests for RecommenderService"""
    
    def test_service_initialization(self):
        """Test service can be initialized"""
        service = RecommenderService()
        assert service is not None
        assert service.driver is not None
    
    @pytest.mark.asyncio
    async def test_get_recommendations_basic(self, db_session):
        """Test basic recommendation query"""
        service = RecommenderService()
        
        result = await service.get_recommendations(
            query="beauty salon",
            db=db_session,
            limit=5
        )
        
        assert "businesses" in result
        assert "citation" in result
        assert "total" in result
        assert isinstance(result["businesses"], list)
    
    @pytest.mark.asyncio
    async def test_get_recommendations_with_filters(self, db_session, sample_business):
        """Test recommendations with category filter"""
        service = RecommenderService()
        
        result = await service.get_recommendations(
            query="salon",
            db=db_session,
            category="beauty",
            geo="Алматы",
            verified_only=True
        )
        
        assert all(b["category"] == "beauty" for b in result["businesses"])
        assert all(b["verified"] for b in result["businesses"])
    
    def test_build_citation(self):
        """Test citation text generation"""
        service = RecommenderService()
        
        citation = service._build_citation(
            query="beauty salon",
            category="beauty",
            geo="Алматы",
            results_count=3
        )
        
        assert "beauty salon" in citation.lower()
        assert "Алматы" in citation
        assert "3" in citation
```

### 📝 Шаг 4: Создать integration тесты

```python
# tests/integration/test_verification_flow.py
import pytest
from backend.services.verification_coordinator import VerificationCoordinator


@pytest.mark.integration
@pytest.mark.asyncio
class TestVerificationFlow:
    """Integration tests for verification pipeline"""
    
    async def test_full_verification_flow(self, db_session, sample_business):
        """Test complete verification flow"""
        coordinator = VerificationCoordinator(
            two_gis_key="test-key",
            google_key="test-key"
        )
        
        # Mock external API calls
        with patch.object(coordinator, '_verify_2gis') as mock_2gis:
            mock_2gis.return_value = {
                "verified": True,
                "confidence": 0.95
            }
            
            result = await coordinator.verify_business(
                sample_business,
                db_session
            )
        
        assert result["status"] == "success"
        assert "trust_score" in result
        assert result["trust_score"] > 0.0
    
    async def test_trust_score_calculation(self, db_session, sample_business):
        """Test trust score changes after verification"""
        initial_score = sample_business.trust_score
        
        coordinator = VerificationCoordinator()
        # Simulate successful verification
        sample_business.verified_by_2gis = True
        sample_business.verified_by_google = True
        db_session.commit()
        
        # Recalculate trust score
        from backend.services.trust_scorer import calculate_trust_score
        new_score = calculate_trust_score(sample_business)
        
        assert new_score >= initial_score
```

---

## 📊 ПОКРЫТИЕ КОДА — Целевые метрики

### 🎯 Минимальные требования:

| Модуль | Минимум | Цель | Текущий |
|--------|---------|------|---------|
| **API Endpoints** | 70% | 85% | ~60% ✅ |
| **Services** | 80% | 90% | 0% ❌ |
| **Verifiers** | 60% | 75% | 0% ❌ |
| **Workers** | 50% | 70% | 0% ❌ |
| **Models** | 90% | 95% | 0% ❌ |
| **Utils** | 80% | 90% | 0% ❌ |
| **ИТОГО** | **70%** | **85%** | **~20%** ❌ |

### Проверка покрытия:

```bash
# Генерация отчета
pytest --cov=backend --cov-report=term-missing

# Проверка минимального порога
pytest --cov=backend --cov-fail-under=70
```

---

## 🔧 ДОПОЛНИТЕЛЬНЫЕ ИНСТРУМЕНТЫ

### 1️⃣ Performance тестирование (Locust)

```bash
# Установка
pip install locust

# Создать tests/performance/locustfile.py
# Запуск
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

### 2️⃣ Security тестирование

```bash
# Проверка зависимостей на уязвимости
pip install safety bandit

safety check -r backend/requirements.txt
bandit -r backend/ -ll
```

### 3️⃣ API Schema тестирование

```bash
# Проверка OpenAPI schema
pip install schemathesis

schemathesis run http://localhost:8000/openapi.json
```

---

## 🎭 MOCK ВНЕШНИХ API

### Пример: Mock 2GIS API

```python
# tests/unit/test_verifiers.py
import pytest
from unittest.mock import patch, AsyncMock

@pytest.mark.unit
@pytest.mark.asyncio
async def test_2gis_verifier_success():
    """Test 2GIS verifier with mocked response"""
    from backend.verifiers.two_gis import TwoGISVerifier
    
    verifier = TwoGISVerifier(api_key="test-key")
    
    # Mock httpx request
    mock_response = {
        "result": {
            "items": [{
                "id": "123456",
                "name": "Test Business",
                "rating": 4.5
            }]
        }
    }
    
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.status_code = 200
        
        result = await verifier.verify_business(
            name="Test Business",
            city="Алматы"
        )
    
    assert result["verified"] is True
    assert result["2gis_id"] == "123456"
```

---

## 🚦 CI/CD INTEGRATION

### GitHub Actions уже настроен:

✅ **Что происходит автоматически:**
1. Lint (black, isort, flake8)
2. Unit тесты (PostgreSQL + Redis в GitHub services)
3. Coverage отчет (Codecov)
4. Docker build

### Локальный запуск CI workflow:

```bash
# Установить act (GitHub Actions локально)
# https://github.com/nektos/act

act push
```

---

## 📋 ЧЕКЛИСТ — Готовность к Production

### Перед релизом проверить:

- [ ] ✅ Все тесты проходят (`pytest tests/ -v`)
- [ ] ✅ Покрытие кода ≥ 70% (`pytest --cov-fail-under=70`)
- [ ] ✅ Нет critical flake8 ошибок
- [ ] ✅ GitHub Actions pipeline зеленый
- [ ] ✅ Security audit пройден (`safety check`)
- [ ] ✅ API schema валиден (`schemathesis run`)
- [ ] ✅ E2E тесты проходят с реальной инфраструктурой
- [ ] ✅ Performance тесты показывают приемлемые результаты
- [ ] ✅ Документация обновлена

---

## 🎯 ПРИОРИТЕТНЫЙ ПЛАН ДЕЙСТВИЙ

### Фаза 1: Базовые unit тесты (1-2 дня)

1. ✅ Создать `pytest.ini`
2. ✅ Создать `tests/conftest.py`
3. ✅ Создать `tests/unit/test_services.py`
4. ✅ Создать `tests/unit/test_verifiers.py`
5. ✅ Достичь 50% покрытия

### Фаза 2: Integration тесты (2-3 дня)

6. ✅ Создать `tests/integration/test_verification_flow.py`
7. ✅ Создать `tests/integration/test_neo4j_queries.py`
8. ✅ Достичь 70% покрытия

### Фаза 3: E2E + Performance (1-2 дня)

9. ✅ Создать `tests/e2e/test_full_journey.py`
10. ✅ Создать `tests/performance/locustfile.py`
11. ✅ Достичь 85% покрытия

---

## 📚 ПОЛЕЗНЫЕ РЕСУРСЫ

- [pytest документация](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Codecov Integration](https://docs.codecov.com/docs)
- [GitHub Actions для Python](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)

---

## 🆘 TROUBLESHOOTING

### Проблема: Тесты падают с SQL ошибками

```bash
# Решение: Убедиться, что используется test database
pytest tests/ -v --log-cli-level=DEBUG
```

### Проблема: Neo4j connection refused

```bash
# Решение: Запустить Docker Compose
docker-compose up -d neo4j
docker-compose logs neo4j  # Проверить статус
```

### Проблема: Медленные тесты

```bash
# Решение: Запустить только быстрые
pytest tests/ -v -m "not slow"

# Или с параллелизацией
pip install pytest-xdist
pytest tests/ -n auto
```

---

**📝 Следующий шаг:** Выберите вариант тестирования (А, Б или В) и запустите!

**🎯 Рекомендация:** Начните с **Варианта А** (локально без Docker) для быстрой проверки, затем переходите к **Варианту Б** для полного покрытия.
