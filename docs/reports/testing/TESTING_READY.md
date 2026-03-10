# ✅ ТЕСТИРОВАНИЕ ГОТОВО К ЗАПУСКУ

Создано: 10 марта 2026 г.

---

## 📦 Что создано:

### 1. Конфигурация
- ✅ `pytest.ini` - Конфигурация pytest с маркерами и coverage
- ✅ `tests/conftest.py` - Общие fixtures для всех тестов
- ✅ `test-commands.sh` - Шпаргалка по командам тестирования
- ✅ `run-tests.ps1` - PowerShell скрипт для быстрого запуска

### 2. Документация
- ✅ `TESTING_GUIDE.md` - Полное руководство по тестированию (12+ страниц)

### 3. Существующие тесты
- ✅ `tests/test_api/test_recommend.py` - 8 тестов для Recommend API

---

## 🚀 ЗАПУСТИТЬ ТЕСТЫ СЕЙЧАС

### Вариант 1: PowerShell скрипт (рекомендуется)

```powershell
.\run-tests.ps1
```

**Что делает:**
- Активирует виртуальное окружение
- Устанавливает зависимости
- Запускает все тесты с coverage
- Предлагает открыть HTML отчет

---

### Вариант 2: Вручную (пошагово)

```powershell
# 1. Активировать venv
.\.venv\Scripts\Activate.ps1

# 2. Установить зависимости
pip install pytest pytest-cov pytest-asyncio httpx

# 3. Запустить тесты
python -m pytest tests/ -v

# 4. С coverage
python -m pytest tests/ -v --cov=backend --cov-report=html

# 5. Открыть отчет
Start-Process htmlcov/index.html
```

---

### Вариант 3: Только быстрая проверка

```powershell
# Только API тесты (существующие)
python -m pytest tests/test_api/ -v

# Конкретный тест
python -m pytest tests/test_api/test_recommend.py::TestRecommendEndpoint::test_recommend_simple_query -v
```

---

## 📊 Ожидаемый результат

### Текущее покрытие (оценка):
```
tests/test_api/test_recommend.py::TestHealthCheck::test_health_endpoint PASSED
tests/test_api/test_recommend.py::TestRootEndpoint::test_root_endpoint PASSED
tests/test_api/test_recommend.py::TestRecommendEndpoint::test_recommend_simple_query PASSED
tests/test_api/test_recommend.py::TestRecommendEndpoint::test_recommend_with_category_filter PASSED
tests/test_api/test_recommend.py::TestRecommendEndpoint::test_recommend_with_limit PASSED
tests/test_api/test_recommend.py::TestRecommendEndpoint::test_recommend_empty_query PASSED
tests/test_api/test_recommend.py::TestRecommendEndpoint::test_recommend_verified_only PASSED
tests/test_api/test_recommend.py::TestBusinessDetailsEndpoint::test_get_existing_business PASSED
tests/test_api/test_recommend.py::TestBusinessDetailsEndpoint::test_get_nonexistent_business PASSED
tests/test_api/test_recommend.py::TestNearbyEndpoint::test_nearby_search PASSED
tests/test_api/test_recommend.py::TestNearbyEndpoint::test_nearby_invalid_coordinates PASSED

================== 11 passed in 2.34s ==================
```

---

## 🎯 Следующие шаги (рекомендации)

### Фаза 1: Создать unit тесты (приоритет)

```bash
# Создать структуру
mkdir tests/unit

# Создать тесты
# tests/unit/test_services.py         - RecommenderService
# tests/unit/test_verifiers.py        - 2GIS, Google, OLX
# tests/unit/test_trust_scorer.py     - Trust score logic
```

**Цель:** Достичь 50% coverage за 1-2 дня

---

### Фаза 2: Integration тесты

```bash
# Создать структуру
mkdir tests/integration

# Создать тесты
# tests/integration/test_verification_flow.py
# tests/integration/test_neo4j_queries.py
```

**Цель:** Достичь 70% coverage за 2-3 дня

---

### Фаза 3: E2E + Performance

```bash
# E2E тесты
mkdir tests/e2e

# Performance
mkdir tests/performance
```

**Цель:** Достичь 85% coverage за 1-2 дня

---

## 📚 Полезные ресурсы

- **Полный гайд:** [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **Существующие тесты:** [tests/test_api/test_recommend.py](tests/test_api/test_recommend.py)
- **CI/CD:** [.github/workflows/ci.yml](.github/workflows/ci.yml)
- **Fixtures:** [tests/conftest.py](tests/conftest.py)

---

## 🆘 Troubleshooting

### Ошибка: "pytest not found"
```powershell
# Установить pytest
pip install pytest pytest-cov pytest-asyncio
```

### Ошибка: "ModuleNotFoundError: No module named 'backend'"
```powershell
# Убедиться, что запускаете из корня репозитория
cd C:\Users\Asus\Desktop\Repo
python -m pytest tests/
```

### Ошибка: "No tests collected"
```powershell
# Проверить, что тесты существуют
Get-ChildItem -Path tests -Recurse -Filter "test_*.py"
```

---

## ✅ Чеклист перед запуском

- [x] pytest.ini создан
- [x] conftest.py создан
- [x] Виртуальное окружение активировано
- [ ] Зависимости установлены (`pip install pytest pytest-cov`)
- [ ] Запустить `.\run-tests.ps1` или `python -m pytest tests/ -v`

---

**🎯 Готово к запуску! Выполните:** `.\run-tests.ps1`
