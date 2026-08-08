# EPIC-02 — Domain Core

## 1. Цель EPIC

Создать независимое предметное ядро PestWatch, которое описывает основные данные и состояния системы без зависимости от Flask, SQLAlchemy, SQLite, Weather API и пользовательского интерфейса.

После завершения EPIC должны существовать типизированные Python-модели, которые в следующих этапах будут использоваться:

```text
Weather Integration
        ↓
WeatherData
        ↓
Risk Engine
        ↓
RiskFactorResult
        ↓
RiskResult
```

Domain Core должен отвечать только на вопрос:

> Какие данные и состояния существуют внутри предметной области PestWatch?

На этом этапе система ещё не:

- получает реальную погоду;
- рассчитывает риск;
- сохраняет Assessment;
- работает со справочником вредителей.

---

# 2. Git

## 2.1 Базовая ветка

EPIC-02 создан от актуального:

```text
main
```

после merge:

```text
EPIC-01 — Project Bootstrap
```

## 2.2 Рабочая ветка

```text
feature/epic-02-domain-core
```

Все изменения EPIC-02 выполняются только в этой ветке.

## 2.3 Pull Request

Планируемое название:

```text
EPIC-02: Domain Core
```

Схема:

```text
main
  ↓
feature/epic-02-domain-core
  ↓
implementation
  ↓
unit tests
  ↓
regression
  ↓
architecture review
  ↓
Pull Request
  ↓
review
  ↓
merge → main
```

---

# 3. Scope

В EPIC-02 входит создание чистых domain-моделей.

## 3.1 Enum

Необходимо реализовать:

```text
UserProfile
RiskLevel
RiskStatus
RiskFactorState
```

## 3.2 Value / Data Objects

Необходимо реализовать:

```text
Location
WeatherData
RiskFactorResult
RiskResult
```

Все они располагаются внутри:

```text
app/domain/
```

---

# 4. Out of Scope

В EPIC-02 сознательно не входят:

- SQLAlchemy ORM models;
- таблицы SQLite;
- миграции;
- Threat;
- Source;
- Recommendation;
- ThreatRepository;
- ThreatService;
- WeatherClient;
- WeatherService;
- WeatherAdapter;
- реальные HTTP-запросы;
- RiskEngine;
- RiskCalculator;
- правила оценки риска;
- DegreeDaysCalculator;
- Assessment;
- REST API;
- изменение UI.

Особенно важно:

> Наличие `WeatherData` в EPIC-02 не означает интеграцию с Weather API.

`WeatherData` здесь является только внутренней моделью данных.

---

# 5. Архитектурное правило EPIC-02

Domain Core должен быть независимым.

Допустимая зависимость:

```text
Python Standard Library
        ↓
app/domain
```

Недопустимые зависимости:

```text
app/domain
    ✕ Flask
    ✕ Flask-SQLAlchemy
    ✕ SQLAlchemy
    ✕ requests/httpx
    ✕ Weather API
    ✕ repositories
    ✕ controllers
```

При этом последующие слои смогут зависеть от Domain:

```text
controllers
services
risk
integrations
repositories
        ↓
domain
```

Но не наоборот.

---

# 6. Предлагаемая структура

После EPIC-02:

```text
app/
└── domain/
    ├── __init__.py
    ├── user_profile.py
    ├── risk_level.py
    ├── risk_status.py
    ├── risk_factor_state.py
    ├── location.py
    ├── weather_data.py
    ├── risk_factor_result.py
    └── risk_result.py
```

Тесты:

```text
tests/
├── unit/
│   └── domain/
│       ├── __init__.py
│       ├── test_user_profile.py
│       ├── test_risk_level.py
│       ├── test_risk_status.py
│       ├── test_risk_factor_state.py
│       ├── test_location.py
│       ├── test_weather_data.py
│       ├── test_risk_factor_result.py
│       └── test_risk_result.py
│
└── integration/
    └── test_app.py
```

Существующие integration tests EPIC-01 сохраняются и продолжают запускаться.

---

# 7. Domain Model

## 7.1 UserProfile

Определяет, для какого пользовательского сценария выполняется оценка.

Поддерживаемые значения:

```text
HUMAN
GARDEN
VEGETABLE_GARDEN
```

Смысл:

```text
HUMAN
→ человек / прогулки / риск клещей

GARDEN
→ сад / плодовые культуры

VEGETABLE_GARDEN
→ огород / овощные культуры
```

На данном этапе `UserProfile` не определяет список угроз самостоятельно.

Соответствие:

```text
UserProfile → Threat[]
```

будет реализовано позже на Service Layer.

---

## 7.2 RiskLevel

Качественный уровень сезонного риска.

Значения:

```text
LOW
MODERATE
ELEVATED
HIGH
```

Смысл:

```text
LOW
→ низкий

MODERATE
→ умеренный

ELEVATED
→ повышенный

HIGH
→ высокий
```

Важно:

`RiskLevel` не является вероятностью.

Например:

```text
HIGH ≠ 90%
```

Enum описывает только категорию результата.

---

## 7.3 RiskStatus

Описывает состояние выполнения оценки.

Значения:

```text
CALCULATED
LIMITED
INSUFFICIENT_DATA
ERROR
```

### CALCULATED

Расчет выполнен на основании необходимых данных.

### LIMITED

Расчет возможен, но некоторые необязательные данные отсутствуют или качество результата ограничено.

### INSUFFICIENT_DATA

Отсутствуют данные, без которых корректная оценка невозможна.

### ERROR

При выполнении оценки произошла техническая или вычислительная ошибка.

Важно:

```text
RiskStatus
```

и:

```text
RiskLevel
```

— разные понятия.

Например:

```text
status = INSUFFICIENT_DATA
risk_level = None
```

является корректным состоянием.

---

## 7.4 RiskFactorState

Описывает результат проверки одного условия.

Значения:

```text
MATCHED
NOT_MATCHED
MISSING
```

### MATCHED

Фактическое значение соответствует условию.

### NOT_MATCHED

Значение известно, но условию не соответствует.

### MISSING

Значение отсутствует.

Критическое правило:

```text
MISSING != NOT_MATCHED
```

Отсутствующий показатель нельзя считать показателем, который не соответствует условию.

---

# 8. Location

## 8.1 Назначение

Внутренняя модель выбранной территории.

Минимальные поля:

```text
name
region
country
latitude
longitude
```

Предлагаемый тип:

```python
@dataclass(frozen=True)
class Location:
    name: str
    region: str | None
    country: str
    latitude: float
    longitude: float
```

`region` допускается `None`, поскольку внешний геокодирующий сервис может не вернуть регион для некоторых территорий.

---

## 8.2 Ограничения координат

Domain Model должна защищаться от явно невозможных координат:

```text
latitude
-90 ≤ value ≤ 90

longitude
-180 ≤ value ≤ 180
```

При выходе за диапазон должна возникать:

```text
ValueError
```

---

# 9. WeatherData

## 9.1 Назначение

`WeatherData` — внутренняя погодная модель PestWatch.

Она не должна повторять JSON конкретного Weather API.

Минимальные поля:

```text
observed_at
temperature
humidity
precipitation
wind_speed
soil_temperature
```

Предлагаемая структура:

```python
@dataclass(frozen=True)
class WeatherData:
    observed_at: datetime
    temperature: float | None
    humidity: float | None
    precipitation: float | None
    wind_speed: float | None
    soil_temperature: float | None
```

---

## 9.2 Почему показатели допускают None

Weather API может вернуть неполный набор данных.

Поэтому:

```text
None
```

означает:

> показатель отсутствует.

Нельзя автоматически превращать отсутствие данных в:

```text
0
```

Например:

```text
soil_temperature = None
```

не равно:

```text
soil_temperature = 0.0
```

Это принципиально важно для дальнейшего Risk Engine.

---

## 9.3 Единицы измерения

На уровне Domain Core принимаем:

```text
temperature
→ °C

soil_temperature
→ °C

humidity
→ %

precipitation
→ mm

wind_speed
→ m/s
```

Weather Adapter в будущем обязан преобразовать внешний формат API именно в эти внутренние единицы.

---

# 10. RiskFactorResult

## 10.1 Назначение

Описывает результат проверки одного фактора конкретной модели риска.

Например:

```text
TEMPERATURE
SEASON
HUMIDITY
SOIL_TEMPERATURE
DEGREE_DAYS
```

На данном EPIC создавать отдельный enum всех возможных типов факторов не требуется, если он ещё окончательно не зафиксирован архитектурой.

Минимальная структура:

```text
factor
state
actual_value
expected
explanation
```

Предлагаемая модель:

```python
@dataclass(frozen=True)
class RiskFactorResult:
    factor: str
    state: RiskFactorState
    actual_value: object | None
    expected: str | None
    explanation: str
```

---

## 10.2 Пример

```text
factor:
TEMPERATURE

state:
MATCHED

actual_value:
18.4

expected:
">= 10 °C"

explanation:
"Температура соответствует условиям активности."
```

Другой вариант:

```text
factor:
SOIL_TEMPERATURE

state:
MISSING

actual_value:
None

expected:
">= ... °C"

explanation:
"Данные о температуре почвы отсутствуют."
```

На этом этапе никакие пороговые значения внутри модели не вычисляются.

---

# 11. RiskResult

## 11.1 Назначение

`RiskResult` представляет итог оценки одной угрозы.

Минимальные поля:

```text
threat_code
status
risk_level
factors
explanation
```

Предлагаемая структура:

```python
@dataclass(frozen=True)
class RiskResult:
    threat_code: str
    status: RiskStatus
    risk_level: RiskLevel | None
    factors: tuple[RiskFactorResult, ...]
    explanation: str
```

---

## 11.2 Почему factors — tuple

Результат расчета после создания не должен случайно изменяться.

Поэтому вместо изменяемого:

```python
list
```

для внутренней immutable-модели результата предпочтительно:

```python
tuple
```

При этом Risk Calculator в будущем может первоначально собирать:

```python
list[RiskFactorResult]
```

а при создании `RiskResult` преобразовывать его в tuple.

---

## 11.3 Инвариант status / risk_level

Необходимо зафиксировать базовое правило.

Если:

```text
status = CALCULATED
```

то:

```text
risk_level != None
```

Если:

```text
status = INSUFFICIENT_DATA
```

то допустимо:

```text
risk_level = None
```

Для:

```text
ERROR
```

также:

```text
risk_level = None
```

Для `LIMITED` наличие RiskLevel допускается:

```text
status = LIMITED
risk_level = MODERATE
```

или другой рассчитанный уровень.

---

# 12. TASKS

## TASK-02.01 — Создать UserProfile

Реализовать enum:

```text
HUMAN
GARDEN
VEGETABLE_GARDEN
```

### Acceptance Criteria

Все три значения доступны и сравниваются как enum values.

---

## TASK-02.02 — Создать RiskLevel

Реализовать:

```text
LOW
MODERATE
ELEVATED
HIGH
```

---

## TASK-02.03 — Создать RiskStatus

Реализовать:

```text
CALCULATED
LIMITED
INSUFFICIENT_DATA
ERROR
```

---

## TASK-02.04 — Создать RiskFactorState

Реализовать:

```text
MATCHED
NOT_MATCHED
MISSING
```

---

## TASK-02.05 — Создать Location

Реализовать поля:

```text
name
region
country
latitude
longitude
```

и валидацию координат.

---

## TASK-02.06 — Создать WeatherData

Реализовать внутреннюю погодную модель с optional значениями погодных показателей.

---

## TASK-02.07 — Создать RiskFactorResult

Реализовать immutable-модель результата отдельного фактора.

---

## TASK-02.08 — Создать RiskResult

Реализовать итоговую immutable-модель оценки одной угрозы.

---

## TASK-02.09 — Реализовать базовые инварианты RiskResult

Проверить минимум:

```text
CALCULATED
→ RiskLevel обязателен

INSUFFICIENT_DATA
→ RiskLevel может отсутствовать

ERROR
→ RiskLevel может отсутствовать
```

---

## TASK-02.10 — Экспортировать публичные domain types

При необходимости сделать удобный экспорт через:

```text
app/domain/__init__.py
```

например:

```python
from .location import Location
from .risk_level import RiskLevel
...
```

Чтобы последующие слои могли использовать:

```python
from app.domain import WeatherData, RiskResult
```

---

## TASK-02.11 — Создать unit test structure

Создать:

```text
tests/unit/domain/
```

---

## TASK-02.12 — Покрыть enum unit-тестами

Проверить наличие всех утвержденных значений.

---

## TASK-02.13 — Покрыть Location unit-тестами

Проверить:

- создание валидной Location;
- минимальную latitude;
- максимальную latitude;
- invalid latitude;
- минимальную longitude;
- максимальную longitude;
- invalid longitude;
- `region = None`.

---

## TASK-02.14 — Покрыть WeatherData unit-тестами

Проверить:

- создание полного объекта;
- создание объекта с отсутствующими optional indicators;
- отличие `None` от `0`.

---

## TASK-02.15 — Покрыть RiskFactorResult unit-тестами

Проверить:

```text
MATCHED
NOT_MATCHED
MISSING
```

и сохранение explanation.

---

## TASK-02.16 — Покрыть RiskResult unit-тестами

Проверить:

- `CALCULATED + RiskLevel`;
- `LIMITED + RiskLevel`;
- `INSUFFICIENT_DATA + None`;
- `ERROR + None`;
- ошибку `CALCULATED + None`;
- несколько `RiskFactorResult`;
- неизменяемость factors.

---

# 13. Unit Test Scope

В отличие от EPIC-01, основная проверка EPIC-02 — именно:

```text
unit tests
```

а не integration tests.

Минимальные группы:

```text
Enum tests
Location tests
WeatherData tests
RiskFactorResult tests
RiskResult tests
```

---

# 14. Regression

Существующие тесты EPIC-01 не удаляются и не изменяются без необходимости.

Полный запуск:

```powershell
python -m pytest
```

должен включать:

```text
EPIC-01 integration tests
+
EPIC-02 unit tests
```

То есть первый настоящий regression PestWatch выглядит так:

```text
Domain tests
        +
Flask bootstrap tests
        +
SQLite bootstrap tests
        ↓
ALL GREEN
```

---

# 15. Acceptance Criteria EPIC-02

| ID | Criterion |
|---|---|
| AC-02-01 | `UserProfile` содержит три утвержденных значения |
| AC-02-02 | `RiskLevel` содержит четыре уровня |
| AC-02-03 | `RiskStatus` содержит четыре состояния |
| AC-02-04 | `RiskFactorState` различает MATCHED / NOT_MATCHED / MISSING |
| AC-02-05 | `Location` реализована |
| AC-02-06 | координаты Location валидируются |
| AC-02-07 | `WeatherData` реализована |
| AC-02-08 | отсутствующие показатели представлены как `None` |
| AC-02-09 | `RiskFactorResult` реализован |
| AC-02-10 | `RiskResult` реализован |
| AC-02-11 | `CALCULATED` без `RiskLevel` запрещен |
| AC-02-12 | `INSUFFICIENT_DATA` допускает `risk_level=None` |
| AC-02-13 | Domain classes не зависят от Flask |
| AC-02-14 | Domain classes не зависят от SQLAlchemy |
| AC-02-15 | Domain classes не зависят от Weather API |
| AC-02-16 | unit tests проходят |
| AC-02-17 | regression EPIC-01 проходит |
| AC-02-18 | функциональность будущих EPIC не добавлена |

---

# 16. Architecture Review Checklist

Перед Pull Request проверить:

- [ ] в `app/domain` нет import Flask;
- [ ] в `app/domain` нет import SQLAlchemy;
- [ ] в `app/domain` нет HTTP clients;
- [ ] domain objects не обращаются к БД;
- [ ] domain objects не знают о Weather API;
- [ ] enum не содержат расчетной логики;
- [ ] `WeatherData` не повторяет внешний API response;
- [ ] отсутствующие данные представлены как `None`;
- [ ] `MISSING` не смешивается с `NOT_MATCHED`;
- [ ] `RiskLevel` не представлен процентом;
- [ ] `RiskResult` не выполняет расчет риска;
- [ ] в EPIC не реализован `RiskEngine`;
- [ ] в EPIC не реализованы пороговые правила;
- [ ] модели можно создать в обычном unit test без Flask application context.

---

# 17. PR Checklist

## Scope

- [ ] реализован только Domain Core;
- [ ] Weather API не добавлен;
- [ ] Risk Engine не добавлен;
- [ ] ORM models не добавлены;
- [ ] Threat Catalog не добавлен.

## Domain

- [ ] `UserProfile`;
- [ ] `RiskLevel`;
- [ ] `RiskStatus`;
- [ ] `RiskFactorState`;
- [ ] `Location`;
- [ ] `WeatherData`;
- [ ] `RiskFactorResult`;
- [ ] `RiskResult`.

## Tests

- [ ] enum tests;
- [ ] Location tests;
- [ ] WeatherData tests;
- [ ] RiskFactorResult tests;
- [ ] RiskResult tests;
- [ ] existing integration tests;
- [ ] полный `python -m pytest` green.

## Architecture

- [ ] Domain независим;
- [ ] отсутствуют infrastructure dependencies;
- [ ] отсутствует business calculation;
- [ ] отсутствуют premature abstractions;
- [ ] API boundaries EPIC-01 не сломаны.

---

# 18. Definition of Done EPIC-02

EPIC-02 считается завершенным, когда:

```text
UserProfile
        +
RiskLevel
        +
RiskStatus
        +
RiskFactorState
        +
Location
        +
WeatherData
        +
RiskFactorResult
        +
RiskResult
        +
Domain unit tests
        +
EPIC-01 regression
        +
Architecture Review
        ↓
READY FOR PR
```

После merge в:

```text
main
```

мы получаем:

```text
EPIC-01
Technical Foundation

        +

EPIC-02
Domain Core
```

и можем переходить к:

```text
EPIC-03 — Threat Catalog
```

---

# 19. Условие перехода к EPIC-03

EPIC-03 не начинается до тех пор, пока:

- EPIC-02 полностью реализован;
- unit tests проходят;
- regression проходит;
- architecture review завершен;
- PR создан;
- замечания исправлены;
- повторный test run green;
- PR merged в `main`.

После merge:

```text
feature/epic-02-domain-core
        ↓
main
        ↓
feature/epic-03-threat-catalog
```
