# EPIC-09 — Risk Context Refactoring

## 1. Статус

```text
CONTRACT
READY FOR REVIEW
```

EPIC-09 является архитектурным refactoring EPIC.

Он не добавляет новую пользовательскую capability и не меняет предметные правила оценки угроз.

Основание для EPIC — Architecture Decision:

```text
WeatherData vs RiskContext
```

Принятое решение:

```text
B — отдельный RiskContext
```

---

## 2. Цель EPIC

Устранить архитектурную перегрузку `WeatherData` до начала реализации `Assessment`.

Сейчас `WeatherData` одновременно содержит:

```text
current/provider weather observations
+
derived soil-temperature estimate
+
historical Degree Days result
```

После EPIC-09 ответственность разделяется:

```text
WeatherData
→ normalized current/provider weather observations

SoilTemperatureEstimate
→ derived soil-temperature indicator

DegreeDaysResult
→ derived historical indicator

RiskContext
→ aggregate prepared inputs for Risk Calculators
```

Целевая граница:

```text
WeatherData
+
SoilTemperatureEstimate
+
DegreeDaysResult
        ↓
RiskContext
        ↓
RiskCalculator
        ↓
RiskFactorResult[]
        ↓
RiskEngine
        ↓
RiskResult
```

---

## 3. Почему EPIC-09 выполняется до Assessment

Исходная архитектура определяет `WeatherData` как внутреннюю модель погодных данных.

После EPIC-07 и EPIC-08 объект начал также хранить derived indicators.

Если оставить эту границу неизменной, будущий `AssessmentService` будет вынужден использовать `WeatherData` как универсальный контейнер всего, что необходимо Risk Engine.

EPIC-09 исправляет границу до появления:

```text
AssessmentService
Assessment persistence
Assessment REST API
```

Тем самым refactoring выполняется в точке минимальной стоимости изменения.

---

## 4. Тип изменения

EPIC-09:

```text
architecture refactoring
```

а не:

```text
new business capability
```

Поэтому обязательный invariant:

```text
одинаковые предметные входные данные
до и после EPIC-09
должны давать одинаковые RiskResult
```

---

# 5. Frozen Decisions EPIC-01–08

EPIC-09 не пересматривает уже утверждённые предметные решения.

Не меняются:

```text
Threat catalog

TICK rules

CABBAGE_APHID rules

COLORADO_BEETLE rules

CODLING_MOTH rules
```

Не меняются:

```text
RiskLevel semantics
RiskStatus semantics
RiskFactorState semantics
RiskFactorResult semantics
RiskEvaluation semantics
RiskPolicy semantics
```

Не меняются:

```text
Tick temperature threshold

Cabbage Aphid temperature thresholds

Cabbage Aphid humidity thresholds

Colorado Beetle soil-temperature threshold = 13 °C

Codling Moth base temperature = 10 °C

Codling Moth seasonal threshold = 130 °C СЭТ
```

Не меняются:

```text
SoilTemperatureEstimator formula

T6/T18 source depths

T10 linear interpolation

SoilTemperatureEstimate provenance

DegreeDaysCalculator formula

DegreeDaysResult provenance

historical period semantics

missing historical data semantics
```

Не меняются:

```text
Open-Meteo current weather contract

Open-Meteo historical weather contract

WeatherAdapter mapping

HistoricalWeatherAdapter mapping

WeatherClient error semantics

HistoricalWeatherClient error semantics
```

---

# 6. Fundamental Invariant

EPIC-09 не должен изменить ответы Risk Engine.

Например:

```text
TICK before refactoring
temperature = X
→ result A

TICK after refactoring
temperature = X
→ result A
```

То же правило применяется ко всем четырём угрозам.

Если refactoring меняет:

```text
RiskFactorState
RiskStatus
RiskLevel
actual_value
expected
explanation
required
```

для эквивалентного input — это regression defect.

---

# 7. Scope

В EPIC-09 входят:

```text
RiskContext domain model

RiskContext unit tests

canonical WeatherData cleanup

remove derived indicators from WeatherData

RiskCalculator contract migration

TickRiskCalculator migration

CabbageAphidRiskCalculator migration

ColoradoBeetleRiskCalculator migration

CodlingMothRiskCalculator migration

WeatherService responsibility cleanup

existing unit-test migration

existing integration-test migration

new architecture-focused tests where necessary

Architecture Review

Scope Review

full regression
```

---

# 8. Out of Scope

В EPIC-09 не входят:

```text
Assessment

AssessmentService

Assessment domain model changes

RiskContextBuilder

RiskContextFactory

RiskContextService

production RiskContext assembly

assessment date orchestration

historical period orchestration for Assessment

Assessment persistence

WeatherSnapshot persistence

DegreeDaysResult persistence

SoilTemperatureEstimate persistence

database migrations

new repositories

new controllers

new REST endpoints

UI

History UI

new Weather Provider

new historical provider

new weather fields

new derived indicators

new threats

new biological rules

new thresholds

new RiskLevel

new RiskStatus

new scoring model

ML

notifications
```

---

# 9. Explicit Non-Goal

EPIC-09 не должен отвечать на вопрос:

```text
как production Assessment собирает RiskContext?
```

Это ответственность следующего функционального этапа.

В EPIC-09 достаточно определить и проверить canonical input contract Risk Calculators.

---

# 10. Git

Базовая ветка:

```text
main
```

Рабочая ветка после утверждения контракта:

```text
feature/epic-09-risk-context-refactoring
```

Предлагаемое название PR:

```text
EPIC-09: Introduce Risk Context
```

---

# 11. Canonical Domain Model после EPIC-09

```text
Location
    │
    └── используется upstream
        для получения погодных данных


CURRENT WEATHER

WeatherData
├── observed_at
├── temperature
├── humidity
├── precipitation
├── wind_speed
├── soil_temperature
├── soil_temperature_6cm
└── soil_temperature_18cm


DERIVED SOIL DATA

WeatherData
    ↓
SoilTemperatureEstimator
    ↓
SoilTemperatureEstimate


HISTORICAL WEATHER

Historical Weather
    ↓
DailyTemperature[]
    ↓
DegreeDaysCalculator
    ↓
DegreeDaysResult


RISK INPUT

WeatherData
+
SoilTemperatureEstimate | None
+
DegreeDaysResult | None
        ↓
RiskContext


RISK DOMAIN

RiskContext
    ↓
RiskCalculator
    ↓
RiskFactorResult[]
    ↓
RiskEngine
    ↓
RiskResult
```

---

# 12. Domain Responsibility Matrix

| Domain object | Responsibility |
|---|---|
| `Location` | территория и координаты |
| `WeatherData` | нормализованный current/provider weather snapshot |
| `DailyTemperature` | одна historical daily observation |
| `SoilTemperatureEstimate` | derived T10 estimate + provenance |
| `DegreeDaysResult` | derived historical SET + provenance |
| `RiskContext` | prepared inputs для Risk Calculators |
| `RiskFactorResult` | результат проверки одного фактора |
| `RiskResult` | итог оценки одной угрозы |

---

# 13. RiskContext

Создаётся:

```text
app/domain/risk_context.py
```

Canonical contract:

```python
from dataclasses import dataclass

from app.domain.degree_days_result import DegreeDaysResult
from app.domain.soil_temperature_estimate import (
    SoilTemperatureEstimate,
)
from app.domain.weather_data import WeatherData


@dataclass(frozen=True)
class RiskContext:
    weather: WeatherData
    soil_temperature_10cm_estimate: (
        SoilTemperatureEstimate | None
    ) = None
    degree_days_10c: DegreeDaysResult | None = None
```

---

# 14. RiskContext Semantics

`RiskContext` означает:

```text
полный набор подготовленных domain inputs,
доступных Risk Calculators
в рамках одного расчёта
```

Он не означает:

```text
погода

Assessment

историческая запись

пользовательский запрос

database entity
```

---

# 15. RiskContext Immutability

Используется:

```python
@dataclass(frozen=True)
```

После создания context не должен изменяться.

Derived indicators рассчитываются до создания context.

Не допускается:

```python
context.degree_days_10c = result
```

или:

```python
context.soil_temperature_10cm_estimate = estimate
```

---

# 16. RiskContext Fields

Минимальный контракт содержит только:

```text
weather

soil_temperature_10cm_estimate

degree_days_10c
```

---

# 17. Почему `weather` required

Current `WeatherData` является базовым входом для:

```text
TICK
CABBAGE_APHID
```

и остаётся основным current-weather snapshot системы.

Поэтому:

```python
weather: WeatherData
```

не optional.

---

# 18. Почему SoilTemperatureEstimate optional

Не каждая оценка обязана иметь возможность получить:

```text
T6
T18
```

или построить:

```text
T10 estimate
```

Поэтому:

```python
soil_temperature_10cm_estimate: (
    SoilTemperatureEstimate | None
) = None
```

`None` означает:

```text
derived soil-temperature input unavailable
```

а не:

```text
temperature = 0
```

---

# 19. Почему DegreeDaysResult optional

Historical data могут быть:

```text
unavailable
incomplete
missing
```

Поэтому:

```python
degree_days_10c: DegreeDaysResult | None = None
```

`None` сохраняет существующую missing semantics Codling Moth Calculator.

---

# 20. Что НЕ входит в RiskContext

Не добавляем:

```text
Location
UserProfile
Threat
assessment_date
RiskLevel
RiskStatus
RiskFactorResult
RiskResult
Recommendation
Source
```

Не добавляем:

```text
WeatherClient
WeatherService
HistoricalWeatherClient
HistoricalWeatherService
Repository
database session
Flask request
```

Не добавляем:

```text
raw JSON
dict[str, Any]
provider-specific response
```

---

# 21. Почему Location не входит

`Location` используется upstream:

```text
Location
    ↓
WeatherService
HistoricalWeatherService
```

После получения нормализованных данных текущие Risk Calculators координаты непосредственно не используют.

Поэтому:

```text
Location
```

не является calculation input текущих threat models.

---

# 22. Почему UserProfile не входит

`UserProfile` отвечает за:

```text
какие Threat необходимо оценить
```

`RiskContext` отвечает за:

```text
какие факты доступны Calculator
```

Это разные ответственности.

Canonical separation:

```text
UserProfile
→ orchestration / threat selection

RiskContext
→ risk calculation input
```

---

# 23. Почему Threat не входит

Threat используется для выбора соответствующего Calculator.

После выбора:

```text
TickRiskCalculator
```

не должен дополнительно проверять:

```text
context.threat == TICK
```

Threat selection остаётся orchestration responsibility.

---

# 24. Почему assessment_date не входит

Дата оценки нужна upstream для построения historical period.

После формирования:

```text
DegreeDaysResult
```

период уже зафиксирован:

```text
period_start
period_end
```

Ни один текущий Calculator непосредственно `assessment_date` не использует.

---

# 25. RiskContext не является Service Locator

Категорически не допускается:

```python
RiskContext(
    weather_service=...,
    historical_weather_service=...,
    repository=...,
)
```

Calculator не должен самостоятельно получать данные.

Все inputs должны быть подготовлены до вызова Calculator.

---

# 26. RiskContext не является generic bag

Не допускается:

```python
@dataclass
class RiskContext:
    values: dict[str, Any]
```

или:

```python
context.get("degree_days")
```

Используются только typed fields.

---

# 27. Canonical WeatherData

После EPIC-09 `WeatherData` снова означает:

```text
normalized current/provider weather observations
```

Он содержит только значения, непосредственно полученные от current Weather Provider и нормализованные Adapter-ом.

---

# 28. Canonical WeatherData Contract

После cleanup:

```python
@dataclass(frozen=True)
class WeatherData:
    observed_at: datetime
    temperature: float | None
    humidity: float | None
    precipitation: float | None
    wind_speed: float | None
    soil_temperature: float | None
    soil_temperature_6cm: float | None = None
    soil_temperature_18cm: float | None = None
```

---

# 29. Что удаляется из WeatherData

Удаляются:

```python
soil_temperature_10cm_estimate: (
    SoilTemperatureEstimate | None
)

degree_days_10c: DegreeDaysResult | None
```

Эти значения являются derived indicators PestWatch, а не current/provider observations.

---

# 30. Что остаётся в WeatherData

Остаются:

```text
observed_at
temperature
humidity
precipitation
wind_speed
soil_temperature
soil_temperature_6cm
soil_temperature_18cm
```

---

# 31. Почему soil_temperature_6cm остаётся

Это значение непосредственно предоставляет Weather Provider.

PestWatch его не вычисляет.

Следовательно:

```text
soil_temperature_6cm
```

является normalized weather observation.

---

# 32. Почему soil_temperature_18cm остаётся

По той же причине:

```text
soil_temperature_18cm
```

является provider observation.

Он не является derived indicator PestWatch.

---

# 33. Почему soil_temperature остаётся

Существующее:

```text
soil_temperature
```

соответствует provider observation:

```text
soil_temperature_0cm
```

и остаётся частью current WeatherData.

EPIC-09 не меняет его semantics и не переименовывает поле.

---

# 34. WeatherData Backward Contract

После EPIC-09 canonical constructor:

```python
WeatherData(
    observed_at=...,
    temperature=...,
    humidity=...,
    precipitation=...,
    wind_speed=...,
    soil_temperature=...,
    soil_temperature_6cm=...,
    soil_temperature_18cm=...,
)
```

Больше не поддерживаются:

```python
WeatherData(
    soil_temperature_10cm_estimate=...
)
```

и:

```python
WeatherData(
    degree_days_10c=...
)
```

Это intentional internal breaking change.

Compatibility shim не создаётся.

---

# 35. Derived Indicators остаются самостоятельными Domain Objects

Не меняются:

```text
SoilTemperatureEstimate
SoilTemperatureEstimateMethod

DailyTemperature
DegreeDaysResult
DegreeDaysCalculationMethod
```

Они не становятся nested implementation details `RiskContext`.

`RiskContext` только содержит ссылки на эти immutable domain values.

---

# 36. Data Provenance

Data provenance остаётся внутри соответствующих derived objects.

Для soil estimate:

```text
SoilTemperatureEstimate
├── depth_cm
├── temperature
├── source_depths_cm
├── source_temperatures
└── method
```

Для Degree Days:

```text
DegreeDaysResult
├── base_temperature
├── total
├── period_start
├── period_end
├── observations
└── method
```

`RiskContext` не дублирует эти поля.

---

# 37. Canonical Principle

После EPIC-09:

```text
WeatherData
→ observations

Derived Domain Objects
→ derived facts + provenance

RiskContext
→ composition of calculation inputs

RiskFactorResult
→ result of applying a rule
```

Каждый объект имеет одну явно различимую ответственность.

# EPIC-09 — Risk Context Refactoring

## Часть 2/3 — Service и Risk Calculator Migration Contract

# 38. WeatherService — текущая проблема

После EPIC-07 `WeatherService` выполняет две разные ответственности:

```text
1. current weather orchestration

Location
    ↓
WeatherClient
    ↓
WeatherAdapter
    ↓
WeatherData
```

и:

```text
2. derived calculation

WeatherData.soil_temperature_6cm
+
WeatherData.soil_temperature_18cm
        ↓
SoilTemperatureEstimator
        ↓
WeatherData.soil_temperature_10cm_estimate
```

После введения `RiskContext` вторая ответственность больше не должна принадлежать `WeatherService`.

---

# 39. Canonical WeatherService Responsibility

После EPIC-09:

```text
WeatherService
→ только получение и нормализация current weather
```

Canonical flow:

```text
Location
    ↓
WeatherClient
    ↓
raw provider payload
    ↓
WeatherAdapter
    ↓
WeatherData
```

---

# 40. Canonical WeatherService Contract

После refactoring:

```python
class WeatherService:
    def __init__(
        self,
        client: WeatherClient,
        adapter: WeatherAdapter,
    ):
        self._client = client
        self._adapter = adapter

    def get_current_weather(
        self,
        location: Location,
    ) -> WeatherData:
        payload = self._client.get_current_weather(
            latitude=location.latitude,
            longitude=location.longitude,
        )

        return self._adapter.to_weather_data(payload)
```

---

# 41. Что удаляется из WeatherService

Удаляется dependency:

```text
SoilTemperatureEstimator
```

Удаляется:

```python
soil_temperature_estimator=...
```

из constructor.

Удаляется orchestration:

```text
T6
+
T18
↓
estimate T10
↓
replace WeatherData
```

---

# 42. Что WeatherService НЕ делает после EPIC-09

```text
не интерполирует T10

не рассчитывает Degree Days

не вызывает HistoricalWeatherService

не создаёт RiskContext

не знает RiskCalculator

не знает Threat

не знает Assessment
```

---

# 43. SoilTemperatureEstimator не удаляется

Сам:

```text
SoilTemperatureEstimator
```

остаётся без изменения.

Он по-прежнему выполняет:

```text
T6
+
T18
        ↓
linear interpolation
        ↓
SoilTemperatureEstimate(T10)
```

Меняется только место orchestration.

---

# 44. Где вызывается SoilTemperatureEstimator

EPIC-09 не создаёт production orchestrator.

Поэтому после cleanup:

```text
WeatherService
```

больше не вызывает estimator.

Сам estimator остаётся доступным как отдельный application/domain calculation component.

В unit/integration tests `RiskContext` может собираться непосредственно:

```python
estimate = SoilTemperatureEstimator().estimate(
    temperature_6cm=...,
    temperature_18cm=...,
)

context = RiskContext(
    weather=weather,
    soil_temperature_10cm_estimate=estimate,
)
```

Production assembly будет определён в Assessment contract.

---

# 45. HistoricalWeatherService

`HistoricalWeatherService` в EPIC-09 не меняется.

Его ответственность уже корректна:

```text
Location
+
date range
        ↓
HistoricalWeatherClient
        ↓
HistoricalWeatherAdapter
        ↓
DailyTemperature[]
```

Он не знает:

```text
Degree Days
Codling Moth
RiskContext
RiskLevel
```

---

# 46. DegreeDaysCalculator

`DegreeDaysCalculator` в EPIC-09 не меняется.

Он продолжает принимать:

```text
DailyTemperature[]
```

и возвращать:

```text
DegreeDaysResult | None
```

Он не создаёт `RiskContext`.

---

# 47. Production RiskContext Assembly

Production assembly специально отсутствует в EPIC-09.

Целевая будущая цепочка известна концептуально:

```text
WeatherService
        ↓
WeatherData
        │
        ├───────────────┐
        │               │
        ▼               │
SoilTemperatureEstimator│
        ↓               │
SoilTemperatureEstimate │
                        │
HistoricalWeatherService│
        ↓               │
DailyTemperature[]      │
        ↓               │
DegreeDaysCalculator    │
        ↓               │
DegreeDaysResult        │
        │               │
        └───────┬───────┘
                ↓
           RiskContext
```

Но компонент, выполняющий эту orchestration, в EPIC-09 не создаётся.

---

# 48. Почему production assembly отложен

Чтобы построить production `RiskContext`, необходимо определить:

```text
assessment_date

historical period

какие данные получать для выбранного UserProfile

нужно ли получать historical weather,
если CODLING_MOTH не оценивается

как обрабатывать partial integration failure

когда выполнять derived calculations

какой lifecycle имеет одна Assessment operation
```

Это вопросы следующего Assessment contract.

EPIC-09 не должен принимать их преждевременно.

---

# 49. RiskCalculator — текущий contract

До EPIC-09:

```python
class RiskCalculator:
    def evaluate(
        self,
        weather: WeatherData,
    ) -> tuple[RiskFactorResult, ...]:
        ...
```

Проблема:

```text
WeatherData
```

больше не является полным и семантически корректным input всех calculators.

---

# 50. Canonical RiskCalculator Contract

После EPIC-09:

```python
class RiskCalculator:
    def evaluate(
        self,
        context: RiskContext,
    ) -> tuple[RiskFactorResult, ...]:
        ...
```

Все implementations обязаны использовать одинаковый public internal contract.

---

# 51. Не поддерживаем два Calculator Contract

Не создаём:

```python
evaluate(weather: WeatherData)
```

параллельно с:

```python
evaluate(context: RiskContext)
```

Не создаём:

```python
evaluate_weather(...)
```

и:

```python
evaluate_context(...)
```

После миграции единственный canonical contract:

```text
RiskContext → RiskCalculator
```

---

# 52. RiskCalculator остаётся generic

Base contract не знает:

```text
TICK

CABBAGE_APHID

COLORADO_BEETLE

CODLING_MOTH
```

и не знает конкретных полей:

```text
temperature
humidity
soil_temperature_10cm_estimate
degree_days_10c
```

Он знает только:

```text
RiskContext
→ RiskFactorResult[]
```

---

# 53. TickRiskCalculator Migration

До EPIC-09:

```text
WeatherData.temperature
        ↓
TickRiskCalculator
```

После:

```text
RiskContext
    ↓
context.weather.temperature
    ↓
TickRiskCalculator
```

---

# 54. TickRiskCalculator — Business Invariant

Не меняются:

```text
factor name

threshold

MATCHED semantics

NOT_MATCHED semantics

MISSING semantics

actual_value

expected

explanation

required
```

Меняется только путь получения input:

```text
weather.temperature
```

→

```text
context.weather.temperature
```

---

# 55. Tick Missing Semantics

Если:

```python
context.weather.temperature is None
```

Calculator формирует тот же:

```text
RiskFactorState.MISSING
```

что и до refactoring.

`RiskContext` не интерпретирует missing data.

---

# 56. CabbageAphidRiskCalculator Migration

До:

```text
WeatherData.temperature
WeatherData.humidity
```

После:

```text
context.weather.temperature
context.weather.humidity
```

---

# 57. Cabbage Aphid Business Invariant

Не меняются:

```text
temperature thresholds
humidity thresholds
factor names
required semantics
explanations
boundary semantics
```

EPIC-09 не пересматривает биологическую модель капустной тли.

---

# 58. Cabbage Aphid Partial Missing

Если:

```text
temperature available
humidity missing
```

или наоборот, существующая semantics каждого `RiskFactorResult` сохраняется.

`RiskContext` не вводит global:

```text
context is incomplete
```

или:

```text
context is invalid
```

из-за одного missing weather field.

---

# 59. ColoradoBeetleRiskCalculator Migration

До EPIC-09 Calculator получает derived estimate через:

```text
WeatherData.soil_temperature_10cm_estimate
```

После:

```text
RiskContext.soil_temperature_10cm_estimate
```

---

# 60. Colorado Beetle Canonical Flow

После EPIC-09:

```text
WeatherData.soil_temperature_6cm
+
WeatherData.soil_temperature_18cm
        ↓
SoilTemperatureEstimator
        ↓
SoilTemperatureEstimate
        ↓
RiskContext.soil_temperature_10cm_estimate
        ↓
ColoradoBeetleRiskCalculator
```

---

# 61. Colorado Beetle Architecture Invariant

`ColoradoBeetleRiskCalculator` по-прежнему не должен знать:

```text
soil_temperature_6cm
soil_temperature_18cm
linear interpolation
Open-Meteo
WeatherClient
SoilTemperatureEstimator
```

Он использует только готовый:

```text
SoilTemperatureEstimate | None
```

---

# 62. Colorado Beetle Business Invariant

Не меняется threshold:

```text
13.0 °C
```

Не меняются:

```text
factor
state
actual_value
expected
explanation
required
```

---

# 63. Colorado Beetle Missing Semantics

Если:

```python
context.soil_temperature_10cm_estimate is None
```

Calculator должен вернуть тот же:

```text
MISSING
```

что и до refactoring.

---

# 64. CodlingMothRiskCalculator Migration

До:

```text
WeatherData.degree_days_10c
```

После:

```text
RiskContext.degree_days_10c
```

---

# 65. Codling Moth Canonical Flow

```text
HistoricalWeatherService
        ↓
DailyTemperature[]
        ↓
DegreeDaysCalculator
        ↓
DegreeDaysResult
        ↓
RiskContext.degree_days_10c
        ↓
CodlingMothRiskCalculator
```

---

# 66. Codling Moth Architecture Invariant

Calculator по-прежнему не знает:

```text
HistoricalWeatherClient
HistoricalWeatherService
Open-Meteo
temperature_2m_mean
DailyTemperature accumulation
Degree Days formula
historical period construction
```

Он использует готовый:

```text
DegreeDaysResult | None
```

---

# 67. Codling Moth Business Invariant

Не меняются:

```text
BASE temperature semantics = 10 °C

seasonal threshold = 130 °C СЭТ

< 130
→ NOT_MATCHED

>= 130
→ MATCHED

None
→ MISSING
```

Не меняются explanation semantics.

---

# 68. RiskContext Missing Semantics

`RiskContext` может быть:

```python
RiskContext(
    weather=weather,
    soil_temperature_10cm_estimate=None,
    degree_days_10c=None,
)
```

Это валидный context.

Он не означает:

```text
Assessment failure
```

---

# 69. Independent Threat Evaluation

Например:

```text
weather.temperature = 18 °C

soil_temperature_10cm_estimate = None

degree_days_10c = None
```

может позволить:

```text
TICK
→ CALCULATED
```

одновременно с:

```text
COLORADO_BEETLE
→ INSUFFICIENT_DATA
```

и:

```text
CODLING_MOTH
→ INSUFFICIENT_DATA
```

Это соответствует принципу независимой оценки угроз.

---

# 70. RiskContext не валидирует completeness для Threat

Не создаём:

```python
context.validate_for("CODLING_MOTH")
```

Не создаём:

```python
context.is_complete
```

Не создаём:

```python
context.missing_fields
```

Каждый Calculator уже владеет semantics required/optional факторов.

---

# 71. RiskEngine Responsibility

`RiskEngine` остаётся generic aggregation layer.

Он отвечает за:

```text
RiskFactorResult[]
        ↓
RiskEvaluation
        ↓
RiskPolicy
        ↓
RiskResult
```

---

# 72. RiskEngine не должен читать RiskContext

Если текущая реализация `RiskEngine` получает уже рассчитанные:

```text
RiskFactorResult[]
```

то EPIC-09 вообще не меняет его runtime contract.

Не следует добавлять:

```python
RiskEngine.evaluate(
    context=...
)
```

если Engine сам не вызывает Calculator.

---

# 73. Calculator Selection

EPIC-09 не меняет механизм выбора Calculator.

Не добавляем selection logic в:

```text
RiskContext
```

и не переносим её в:

```text
WeatherService
```

---

# 74. RiskEvaluation

`RiskEvaluation` не меняется.

Он по-прежнему анализирует:

```text
RiskFactorResult[]
```

а не:

```text
WeatherData
RiskContext
```

---

# 75. RiskPolicy

`RiskPolicy` не меняется.

EPIC-09 не меняет mapping:

```text
factor states
→ RiskLevel / RiskStatus
```

---

# 76. WeatherAdapter

`WeatherAdapter` не должен создавать:

```text
RiskContext
```

Он продолжает только mapping:

```text
provider current JSON
→ WeatherData
```

После удаления derived fields из `WeatherData` Adapter становится ещё более явно provider-normalization boundary.

---

# 77. HistoricalWeatherAdapter

Не меняется.

Продолжает:

```text
provider historical JSON
→ DailyTemperature[]
```

Он не знает `RiskContext`.

---

# 78. SoilTemperatureEstimator

Не знает:

```text
RiskContext
```

Предпочтительный contract остаётся:

```text
T6 + T18
→ SoilTemperatureEstimate | None
```

Composition выполняется снаружи.

---

# 79. DegreeDaysCalculator

Также не знает:

```text
RiskContext
```

Contract:

```text
DailyTemperature[]
→ DegreeDaysResult | None
```

остаётся неизменным.

---

# 80. Почему Calculators получают весь RiskContext

Хотя каждый Calculator использует только часть context, единый typed contract сохраняет простое polymorphic API:

```python
calculator.evaluate(context)
```

Это осознанный trade-off.

Не используем calculator-specific signatures:

```python
evaluate(temperature)
evaluate(temperature, humidity)
evaluate(estimate)
evaluate(degree_days)
```

поскольку это усложнило бы orchestration и registry.

---

# 81. Правило использования Context

Calculator должен читать только необходимые ему inputs.

Ожидаем:

```text
Tick
→ context.weather.temperature
```

```text
Cabbage Aphid
→ context.weather.temperature
→ context.weather.humidity
```

```text
Colorado Beetle
→ context.soil_temperature_10cm_estimate
```

```text
Codling Moth
→ context.degree_days_10c
```

---

# 82. Запрещённые зависимости Tick

`TickRiskCalculator` не должен использовать:

```text
soil_temperature_10cm_estimate
degree_days_10c
```

---

# 83. Запрещённые зависимости Cabbage Aphid

`CabbageAphidRiskCalculator` не должен использовать:

```text
soil_temperature_10cm_estimate
degree_days_10c
```

---

# 84. Запрещённые зависимости Colorado Beetle

`ColoradoBeetleRiskCalculator` не должен использовать:

```text
context.weather.temperature
context.weather.humidity
degree_days_10c
```

если эти значения не входят в утверждённую модель Colorado Beetle.

---

# 85. Запрещённые зависимости Codling Moth

`CodlingMothRiskCalculator` не должен использовать:

```text
context.weather.temperature
context.weather.humidity
soil_temperature_10cm_estimate
```

Текущая модель использует только:

```text
degree_days_10c
```

---

# 86. Test Fixtures

Для уменьшения дублирования тесты могут иметь helper:

```python
def create_context(
    *,
    weather: WeatherData | None = None,
    soil_temperature_10cm_estimate=None,
    degree_days_10c=None,
) -> RiskContext:
    ...
```

Но helper не должен содержать business logic.

Он только строит test fixture.

---

# 87. Integration Tests

Существующие integration scenarios должны перейти с:

```text
WeatherData
→ Calculator
```

на:

```text
RiskContext
→ Calculator
```

без изменения expected outcomes.

---

# 88. Colorado Integration Migration

Было:

```text
WeatherData
с embedded T10 estimate
        ↓
ColoradoBeetleRiskCalculator
```

Станет:

```text
WeatherData
        ↓
SoilTemperatureEstimator
        ↓
SoilTemperatureEstimate
        ↓
RiskContext
        ↓
ColoradoBeetleRiskCalculator
```

---

# 89. Codling Integration Migration

Было:

```text
DegreeDaysCalculator
        ↓
DegreeDaysResult
        ↓
WeatherData.degree_days_10c
        ↓
CodlingMothRiskCalculator
```

Станет:

```text
DegreeDaysCalculator
        ↓
DegreeDaysResult
        ↓
RiskContext.degree_days_10c
        ↓
CodlingMothRiskCalculator
```

---

# 90. No Business Re-baselining

При миграции тестов запрещено изменять expected results только для того, чтобы тесты стали зелёными.

Если существующий scenario до refactoring ожидал:

```text
HIGH
```

после refactoring он также должен ожидать:

```text
HIGH
```

Если результат изменился, сначала ищется regression.

---

# 91. WeatherService Test Migration

Существующие tests, проверяющие estimator внутри `WeatherService`, должны быть удалены или преобразованы, поскольку эта ответственность сознательно удаляется.

После EPIC-09 WeatherService tests должны проверять только:

```text
Location coordinates → WeatherClient

Client payload → WeatherAdapter

Adapter WeatherData → caller
```

---

# 92. Не переносим удалённый WeatherService Test буквально

Если старый test проверяет:

```text
WeatherService
→ SoilTemperatureEstimator
```

его не нужно механически переносить в новый компонент только ради сохранения количества тестов.

После EPIC-09 такой collaboration больше не является ответственностью `WeatherService`.

Сам:

```text
SoilTemperatureEstimator
```

уже имеет собственные unit tests.

Поэтому тест удалённой ответственности должен быть удалён либо заменён тестом нового canonical contract `WeatherService`.

---

# 93. WeatherService после refactoring

Unit-test matrix `WeatherService` должна подтверждать только:

```text
Location.latitude
→ WeatherClient

Location.longitude
→ WeatherClient

WeatherClient payload
→ WeatherAdapter

WeatherAdapter result
→ caller
```

Не должно остаться тестов:

```text
WeatherService
→ SoilTemperatureEstimator
```

---

# 94. Weather Integration Regression

Существующая реальная цепочка:

```text
Open-Meteo
→ WeatherClient
→ WeatherAdapter
→ WeatherService
→ WeatherData
```

должна продолжить работать.

После EPIC-09 real/current Weather integration не должна автоматически рассчитывать:

```text
T10 estimate
```

Это intentional responsibility change.

---

# 95. Derived Calculation Regression

Отдельно сохраняется возможность:

```text
WeatherData
    ↓
soil_temperature_6cm
soil_temperature_18cm
    ↓
SoilTemperatureEstimator
    ↓
SoilTemperatureEstimate
```

То есть EPIC-09 меняет composition, но не математическую capability.

---

# 96. Historical Weather Regression

Не меняется цепочка:

```text
HistoricalWeatherClient
        ↓
HistoricalWeatherAdapter
        ↓
HistoricalWeatherService
        ↓
DailyTemperature[]
        ↓
DegreeDaysCalculator
        ↓
DegreeDaysResult
```

---

# 97. No New External Calls

EPIC-09 не должен добавлять ни одного нового HTTP request.

Не меняется количество provider calls существующих services.

---

# 98. End of Migration Contract

После завершения migration:

```text
WeatherData
```

больше нигде не должен использоваться как container для:

```text
SoilTemperatureEstimate
DegreeDaysResult
```

Canonical owner этих references:

```text
RiskContext
```

---

# Часть 3/3 — Test Matrix, Architecture Gates, Implementation Plan и DoD

# 99. Test Strategy

EPIC-09 является refactoring EPIC.

Поэтому тестирование должно доказывать два свойства одновременно:

```text
STRUCTURAL CORRECTNESS
+
BEHAVIORAL EQUIVALENCE
```

Structural correctness:

```text
ответственности действительно разделены
```

Behavioral equivalence:

```text
risk outcomes не изменились
```

---

# 100. Baseline

До начала EPIC-09 зафиксирован baseline:

```text
277 passed
```

Это regression baseline EPIC-01–08.

---

# 101. RiskContext Unit Tests

Создать:

```text
tests/unit/domain/test_risk_context.py
```

Минимальная matrix:

```text
RiskContext создаётся с одним WeatherData

weather сохраняется

soil_temperature_10cm_estimate
по умолчанию None

degree_days_10c
по умолчанию None

SoilTemperatureEstimate сохраняется

DegreeDaysResult сохраняется

оба derived indicators
могут существовать одновременно

RiskContext immutable
```

---

# 102. Minimal RiskContext Test

Проверить:

```python
context = RiskContext(
    weather=weather,
)
```

Expected:

```text
context.weather is weather

context.soil_temperature_10cm_estimate is None

context.degree_days_10c is None
```

---

# 103. Soil Estimate Context Test

Создать:

```text
WeatherData
+
SoilTemperatureEstimate
```

Expected:

```text
context.weather
→ WeatherData

context.soil_temperature_10cm_estimate
→ exact supplied estimate

context.degree_days_10c
→ None
```

---

# 104. Degree Days Context Test

Создать:

```text
WeatherData
+
DegreeDaysResult
```

Expected:

```text
context.degree_days_10c
→ exact supplied result
```

---

# 105. Complete Context Test

Создать:

```text
WeatherData
+
SoilTemperatureEstimate
+
DegreeDaysResult
```

Expected:

```text
все три references сохранены
```

Никакой дополнительный расчёт при создании `RiskContext` не выполняется.

---

# 106. RiskContext Immutability Test

Попытка:

```python
context.degree_days_10c = ...
```

должна приводить к:

```text
FrozenInstanceError
```

Аналогично для:

```text
weather
soil_temperature_10cm_estimate
```

---

# 107. WeatherData Cleanup Tests

Существующий:

```text
tests/unit/domain/test_weather_data.py
```

обновляется.

Удаляются tests, проверяющие:

```text
weather.soil_temperature_10cm_estimate

weather.degree_days_10c
```

---

# 108. WeatherData Canonical Fields Test

После cleanup проверяется:

```text
observed_at

temperature

humidity

precipitation

wind_speed

soil_temperature

soil_temperature_6cm

soil_temperature_18cm
```

---

# 109. WeatherData Optional Provider Fields

Проверить:

```text
soil_temperature_6cm=None
soil_temperature_18cm=None
```

по умолчанию.

Это валидный `WeatherData`.

---

# 110. WeatherData Immutability

Существующая immutable semantics сохраняется.

Если она уже покрыта тестами, дополнительный дублирующий test не требуется.

---

# 111. WeatherAdapter Regression

`WeatherAdapter` продолжает создавать:

```text
WeatherData
```

с:

```text
soil_temperature
soil_temperature_6cm
soil_temperature_18cm
```

Adapter больше не должен быть связан с derived fields.

---

# 112. WeatherAdapter Complete Payload

Существующий complete-payload test должен продолжить проверять:

```text
temperature
humidity
precipitation
wind_speed
soil_temperature
soil_temperature_6cm
soil_temperature_18cm
```

Не проверяем:

```text
soil_temperature_10cm_estimate
degree_days_10c
```

---

# 113. WeatherService Unit Matrix

После cleanup:

```text
coordinates → client

payload → adapter

WeatherData → caller
```

---

# 114. WeatherService Constructor Contract

Проверить, что для создания service достаточно:

```python
WeatherService(
    client=client,
    adapter=adapter,
)
```

Dependency:

```text
SoilTemperatureEstimator
```

больше не требуется.

---

# 115. WeatherService Does Not Derive T10

Необязательно проверять это mock-ом как отрицательное поведение, если dependency полностью удалена из production code.

Architecture gate дополнительно подтвердит отсутствие estimator dependency.

---

# 116. RiskCalculator Base Contract Test

Существующий test:

```text
tests/unit/risk/test_risk_calculator.py
```

мигрирует на:

```text
RiskContext
```

Base Calculator contract должен отражать:

```text
evaluate(context)
→ RiskFactorResult[]
```

---

# 117. Tick Test Migration

Все существующие Tick tests сохраняют свои business cases.

Изменяется только fixture:

```text
WeatherData
↓
RiskContext(weather=WeatherData)
```

---

# 118. Tick Behavioral Equivalence Matrix

Все существующие boundary cases должны остаться неизменными.

В частности:

```text
below threshold
at threshold
above threshold
missing
```

должны давать те же:

```text
RiskFactorState
actual_value
expected
explanation
required
```

---

# 119. Cabbage Aphid Test Migration

Все существующие combinations:

```text
temperature
humidity
```

сохраняются.

Input теперь:

```python
RiskContext(
    weather=weather,
)
```

---

# 120. Cabbage Aphid Behavioral Equivalence

Не меняются существующие cases:

```text
temperature boundaries

humidity boundaries

both matched

one matched / one not matched

missing temperature

missing humidity

missing both
```

если такие cases уже существуют в текущей test matrix.

Не добавляем новые biological cases только из-за refactoring.

---

# 121. Colorado Beetle Test Migration

Было:

```python
WeatherData(
    ...,
    soil_temperature_10cm_estimate=estimate,
)
```

Станет:

```python
RiskContext(
    weather=weather,
    soil_temperature_10cm_estimate=estimate,
)
```

---

# 122. Colorado Beetle Boundary Matrix

Существующие threshold cases сохраняются:

```text
below 13.0
13.0
above 13.0
None
```

Expected outcomes не меняются.

---

# 123. Colorado Beetle Provenance

Calculator по-прежнему получает полный:

```text
SoilTemperatureEstimate
```

но использует его temperature согласно существующему contract.

Provenance object не упрощается до:

```text
float
```

---

# 124. Codling Moth Test Migration

Было:

```python
WeatherData(
    ...,
    degree_days_10c=degree_days,
)
```

Станет:

```python
RiskContext(
    weather=weather,
    degree_days_10c=degree_days,
)
```

---

# 125. Codling Moth Boundary Matrix

Обязательно сохраняются:

```text
None
→ MISSING

0.0
→ NOT_MATCHED

129.9
→ NOT_MATCHED

130.0
→ MATCHED

130.1
→ MATCHED

500.0
→ MATCHED
```

---

# 126. Codling Moth Provenance

В context передаётся:

```text
DegreeDaysResult
```

целиком.

Не заменяем его:

```text
degree_days_10c: float
```

поскольку это уничтожило бы provenance.

---

# 127. Risk Engine Tests

Если `RiskEngine` не принимает `WeatherData` напрямую, его unit tests не должны меняться только ради EPIC-09.

Это важный scope guard.

Не делаем cosmetic migration файлов, которые архитектурно не затронуты.

---

# 128. RiskPolicy Tests

Не меняются.

---

# 129. RiskEvaluation Tests

Не меняются.

---

# 130. Colorado Integration Test

Существующий:

```text
tests/integration/test_colorado_beetle_risk.py
```

должен проверять цепочку:

```text
WeatherData
        ↓
SoilTemperatureEstimator
        ↓
SoilTemperatureEstimate
        ↓
RiskContext
        ↓
ColoradoBeetleRiskCalculator
        ↓
RiskEngine
```

---

# 131. Codling Moth Integration Test

Существующий:

```text
tests/integration/test_codling_moth_risk.py
```

должен проверять:

```text
DailyTemperature[]
        ↓
DegreeDaysCalculator
        ↓
DegreeDaysResult
        ↓
RiskContext
        ↓
CodlingMothRiskCalculator
        ↓
RiskEngine
```

---

# 132. Threat Calculators Integration

Если существующий:

```text
tests/integration/test_threat_risk_calculators.py
```

передаёт `WeatherData` напрямую Calculator-ам, он мигрирует на `RiskContext`.

Expected business results остаются прежними.

---

# 133. Current Weather Integration

Существующий:

```text
tests/integration/test_weather_integration.py
```

после EPIC-09 должен подтверждать только:

```text
provider
→ WeatherData
```

Если сейчас он ожидает автоматически созданный:

```text
soil_temperature_10cm_estimate
```

эта часть expectation удаляется как obsolete responsibility.

---

# 134. Historical Weather Tests

Следующие tests не должны требовать содержательной миграции:

```text
HistoricalWeatherClient tests

HistoricalWeatherAdapter tests

HistoricalWeatherService tests

DegreeDaysCalculator tests
```

Потому что их contracts не меняются.

---

# 135. SoilTemperatureEstimator Tests

Также не меняются.

Estimator contract остаётся прежним.

---

# 136. Behavioral Equivalence Gate

Перед merge необходимо подтвердить:

```text
TICK
→ все прежние outcomes сохранены

CABBAGE_APHID
→ все прежние outcomes сохранены

COLORADO_BEETLE
→ все прежние outcomes сохранены

CODLING_MOTH
→ все прежние outcomes сохранены
```

---

# 137. No Threshold Diff Gate

Перед PR проверить, что refactoring не изменил числовые thresholds.

Для risk calculators:

```powershell
Get-ChildItem .\app\risk\calculators\*.py |
    Select-String -Pattern "10.0|13.0|25.0|26.0|60.0|70.0|130.0"
```

Результат сравнивается с состоянием до EPIC-09.

EPIC-09 не должен добавлять новые threshold values.

---

# 138. WeatherData Derived Fields Removal Gate

Проверить production code:

```powershell
Get-ChildItem .\app\*.py,.\app\*\*.py,.\app\*\*\*.py |
    Select-String -Pattern "weather\.soil_temperature_10cm_estimate|weather\.degree_days_10c"
```

После migration ожидаем отсутствие production usages.

Тестовые файлы при необходимости проверяются отдельно.

---

# 139. RiskContext Usage Gate

Проверить:

```powershell
Get-ChildItem .\app\risk\*.py,.\app\risk\calculators\*.py |
    Select-String -Pattern "RiskContext"
```

Ожидаем:

```text
RiskCalculator contract

TickRiskCalculator

CabbageAphidRiskCalculator

ColoradoBeetleRiskCalculator

CodlingMothRiskCalculator
```

в соответствии с фактической import structure.

---

# 140. WeatherService Architecture Gate

Проверить:

```powershell
Get-Content .\app\services\weather_service.py |
    Select-String -Pattern "SoilTemperatureEstimator|RiskContext|DegreeDays|Historical|RiskCalculator"
```

Ожидаем пустой вывод.

---

# 141. WeatherData Architecture Gate

Проверить:

```powershell
Get-Content .\app\domain\weather_data.py |
    Select-String -Pattern "SoilTemperatureEstimate|DegreeDaysResult|RiskContext"
```

Ожидаем пустой вывод.

---

# 142. RiskContext Architecture Gate

Проверить:

```powershell
Get-Content .\app\domain\risk_context.py |
    Select-String -Pattern "requests|flask|sqlalchemy|WeatherClient|WeatherService|HistoricalWeatherService|Repository|db\."
```

Ожидаем пустой вывод.

---

# 143. RiskContext Forbidden Domain Dependencies

Проверить:

```powershell
Get-Content .\app\domain\risk_context.py |
    Select-String -Pattern "Location|UserProfile|Threat|RiskLevel|RiskResult|Recommendation|Source"
```

Ожидаем пустой вывод.

---

# 144. Colorado Architecture Gate

Проверить:

```powershell
Get-Content .\app\risk\calculators\colorado_beetle.py |
    Select-String -Pattern "6cm|18cm|interpol|WeatherClient|SoilTemperatureEstimator|requests"
```

Ожидаем пустой вывод.

---

# 145. Codling Architecture Gate

Проверить:

```powershell
Get-Content .\app\risk\calculators\codling_moth.py |
    Select-String -Pattern "HistoricalWeather|temperature_2m_mean|DailyTemperature|requests|archive-api"
```

Ожидаем пустой вывод.

---

# 146. Scope Guard — No Assessment

Проверить staged diff перед commit.

Не должны появиться новые production files:

```text
assessment.py

assessment_service.py

risk_context_builder.py

risk_context_factory.py

assessment_repository.py

assessment_controller.py
```

---

# 147. Scope Guard — No Persistence

EPIC-09 не должен содержать:

```text
new SQLAlchemy models

new migrations

new tables

new repository methods

new database schema
```

---

# 148. Scope Guard — No API

Не добавляются:

```text
/api/assessments

/api/risk

/api/history
```

или любые новые endpoints.

---

# 149. Scope Guard — No Provider Changes

Не меняются request contracts:

```text
WeatherClient

HistoricalWeatherClient
```

Не добавляются новые provider fields.

---

# 150. Scope Guard — No Biological Changes

Не меняются:

```text
factor names

thresholds

required flags

explanation semantics

RiskLevel mapping
```

---

# 151. Implementation Strategy

EPIC-09 выполняется маленькими controlled increments.

Не делаем один большой rewrite.

Предлагаемый порядок:

```text
Slice 1
RiskContext domain model

Slice 2
RiskCalculator contract + Tick migration

Slice 3
Cabbage Aphid migration

Slice 4
Colorado Beetle migration

Slice 5
Codling Moth migration

Slice 6
WeatherData cleanup

Slice 7
WeatherService cleanup

Slice 8
integration-test migration

Slice 9
Architecture + Scope + Regression Gate
```

---

# 152. Почему RiskContext создаётся первым

Сначала появляется новый target contract:

```text
RiskContext
```

и только затем consumers мигрируют на него.

Это позволяет избегать временной неопределённости архитектуры.

---

# 153. Почему WeatherData cleanup не первый

Если сначала удалить:

```text
soil_temperature_10cm_estimate
degree_days_10c
```

из `WeatherData`, существующие calculators немедленно ломаются.

Поэтому сначала создаём новый owner:

```text
RiskContext
```

и мигрируем consumers.

После этого старые поля можно безопасно удалить.

---

# 154. Почему WeatherService cleanup после WeatherData

`WeatherService` сейчас создаёт derived T10 именно потому, что `WeatherData` способен его хранить.

После migration ownership:

```text
SoilTemperatureEstimate
→ RiskContext
```

эта ответственность становится лишней.

Поэтому последовательность должна быть:

```text
RiskContext создан
        ↓
Calculators мигрированы
        ↓
derived fields удалены из WeatherData
        ↓
WeatherService очищен от estimator orchestration
```

Так мы не создаём промежуточное состояние, в котором работающий Calculator лишается своего input.

---

# 155. Atomic Slice Rule

Каждый implementation slice должен:

```text
иметь одну архитектурную цель

оставлять repository в рабочем состоянии

иметь собственный test gate

не включать следующий slice заранее
```

Не допускается один commit вида:

```text
refactor everything to RiskContext
```

---

# 156. Slice 1 — RiskContext Domain Model

Scope:

```text
app/domain/risk_context.py

app/domain/__init__.py

tests/unit/domain/test_risk_context.py
```

Не меняются:

```text
WeatherData
RiskCalculator
calculators
WeatherService
```

Gate:

```text
RiskContext существует
immutable
weather required
derived indicators optional
full regression green
```

---

# 157. Slice 2 — RiskCalculator + Tick

Scope:

```text
app/risk/calculator.py

app/risk/calculators/tick.py

соответствующие unit tests
```

Изменение:

```text
evaluate(weather)
→ evaluate(context)
```

только для base contract и Tick implementation.

Business logic не меняется.

---

# 158. Transitional State после Slice 2

На коротком промежуточном этапе часть Calculators уже может принимать:

```text
RiskContext
```

а часть ещё:

```text
WeatherData
```

Это допустимо только внутри последовательной реализации EPIC-09.

Такое состояние:

```text
не является release state
не merge-ится в main
```

Все slices входят в один EPIC branch.

---

# 159. Slice 3 — Cabbage Aphid

Scope:

```text
CabbageAphidRiskCalculator
+
его tests
```

Изменяется только input path:

```text
weather.temperature
weather.humidity
```

→

```text
context.weather.temperature
context.weather.humidity
```

---

# 160. Slice 4 — Colorado Beetle

Scope:

```text
ColoradoBeetleRiskCalculator
+
unit tests
+
при необходимости integration fixture
```

Migration:

```text
weather.soil_temperature_10cm_estimate
```

→

```text
context.soil_temperature_10cm_estimate
```

Threshold:

```text
13.0
```

не меняется.

---

# 161. Slice 5 — Codling Moth

Scope:

```text
CodlingMothRiskCalculator
+
unit tests
+
при необходимости integration fixture
```

Migration:

```text
weather.degree_days_10c
```

→

```text
context.degree_days_10c
```

Threshold:

```text
130.0
```

не меняется.

---

# 162. Slice 6 — WeatherData Cleanup

Только после migration всех Calculator consumers удаляются:

```text
WeatherData.soil_temperature_10cm_estimate

WeatherData.degree_days_10c
```

Обновляются:

```text
WeatherData tests

fixtures

constructors
```

Не меняются provider observation fields.

---

# 163. Slice 7 — WeatherService Cleanup

Удаляется:

```text
SoilTemperatureEstimator dependency
```

и автоматическое создание T10 estimate.

Остаётся:

```text
Location
→ Client
→ Adapter
→ WeatherData
```

Обновляются только tests ответственности `WeatherService`.

---

# 164. Slice 8 — Integration Migration

Проверяются и при необходимости мигрируют:

```text
test_threat_risk_calculators.py

test_colorado_beetle_risk.py

test_codling_moth_risk.py

test_weather_integration.py
```

Главная цель:

```text
старые business outcomes
=
новые business outcomes
```

---

# 165. Slice 9 — Final Architecture Gate

После завершения реализации выполняются:

```text
full pytest

architecture grep checks

scope review

git diff review
```

Новая функциональность на этом slice не добавляется.

---

# 166. Commit Strategy

Допустим один итоговый production commit EPIC, если разработка выполняется локальными незакоммиченными slices и каждый промежуточный gate подтверждён.

Либо отдельные commits по slices.

Обязательное условие:

```text
финальный PR должен представлять
один coherent architectural change
```

---

# 167. Regression Gate

Перед commit:

```powershell
python -m pytest
```

Обязательное условие:

```text
0 failed
0 errors
```

Количество tests должно быть:

```text
>= 277
```

поскольку появляется как минимум новая test matrix `RiskContext`.

Конкретное итоговое число заранее не фиксируется как acceptance criterion.

---

# 168. Почему не фиксируем точное число тестов

EPIC-09 включает migration существующих tests.

Некоторые obsolete tests `WeatherService` могут быть удалены, а новые `RiskContext` tests добавлены.

Поэтому качество gate определяется:

```text
coverage contract
+
0 regressions
```

а не искусственным требованием:

```text
277 + N
```

---

# 169. Required Test Coverage

Перед merge должны быть явно покрыты:

```text
RiskContext construction

RiskContext optional inputs

RiskContext complete input

RiskContext immutability

WeatherData canonical fields

WeatherService canonical responsibility

Tick via RiskContext

Cabbage Aphid via RiskContext

Colorado Beetle via RiskContext

Codling Moth via RiskContext

Colorado derived-input integration

Codling historical-derived-input integration

existing RiskPolicy

existing RiskEngine

existing provider integrations
```

---

# 170. Behavioral Regression Matrix — TICK

Проверяется:

```text
same weather input
        ↓
same RiskFactorResult
        ↓
same RiskResult
```

До и после refactoring должны совпадать:

```text
factor
state
actual_value
expected
explanation
required
risk_level
status
```

---

# 171. Behavioral Regression Matrix — CABBAGE_APHID

Для эквивалентных:

```text
temperature
humidity
```

не должны измениться:

```text
temperature factor

humidity factor

factor states

risk status

risk level

explanations
```

---

# 172. Behavioral Regression Matrix — COLORADO_BEETLE

Для одинакового:

```text
SoilTemperatureEstimate
```

до и после refactoring результат должен быть идентичен.

Особенно:

```text
12.9
13.0
13.1
None
```

если эти значения входят в существующую boundary matrix.

---

# 173. Behavioral Regression Matrix — CODLING_MOTH

Для одинакового:

```text
DegreeDaysResult
```

результат должен быть идентичен.

Обязательные контрольные значения:

```text
None
0.0
129.9
130.0
130.1
500.0
```

---

# 174. Missing Data Regression

`RiskContext` не меняет semantics отсутствующих данных.

Проверяется:

```text
weather.temperature=None
→ Tick existing MISSING behavior

weather.humidity=None
→ Cabbage Aphid existing MISSING behavior

soil_temperature_10cm_estimate=None
→ Colorado Beetle MISSING

degree_days_10c=None
→ Codling Moth MISSING
```

---

# 175. Partial Context Regression

Валидный:

```python
RiskContext(
    weather=weather,
    soil_temperature_10cm_estimate=None,
    degree_days_10c=None,
)
```

не должен глобально блокировать расчёт.

Например:

```text
Tick
```

может быть рассчитан независимо от отсутствия derived indicators.

---

# 176. Provenance Regression

После переноса derived indicators из `WeatherData` в `RiskContext` не должна теряться информация:

```text
SoilTemperatureEstimate
→ source_depths
→ source_temperatures
→ method
```

и:

```text
DegreeDaysResult
→ period
→ observations
→ base_temperature
→ method
```

Context хранит исходные domain objects целиком.

---

# 177. Provider Isolation Gate

После EPIC-09:

```text
RiskContext
RiskCalculator
Risk Calculators
RiskEngine
```

не должны зависеть от:

```text
requests
Open-Meteo endpoint
provider JSON keys
HTTP errors
```

---

# 178. Persistence Isolation Gate

`RiskContext` не должен зависеть от:

```text
SQLAlchemy
db
ORM models
repositories
```

---

# 179. Flask Isolation Gate

Domain и risk layers не должны импортировать:

```text
flask
request
current_app
```

---

# 180. Derived Calculation Isolation Gate

`RiskContext` не должен импортировать:

```text
SoilTemperatureEstimator
DegreeDaysCalculator
```

Он хранит результаты, а не рассчитывает их.

---

# 181. WeatherService Isolation Gate

`WeatherService` после cleanup не должен импортировать:

```text
RiskContext

SoilTemperatureEstimator

DegreeDaysCalculator

HistoricalWeatherService

RiskCalculator

RiskEngine
```

---

# 182. HistoricalWeatherService Isolation Gate

Он не должен импортировать:

```text
RiskContext

DegreeDaysCalculator

CodlingMothRiskCalculator

RiskEngine
```

---

# 183. Calculator Isolation Gate

Ни один Calculator не должен самостоятельно вызывать:

```text
WeatherService

HistoricalWeatherService

SoilTemperatureEstimator

DegreeDaysCalculator
```

Все inputs приходят через:

```text
RiskContext
```

---

# 184. RiskContext Field Ownership Gate

После EPIC-09:

```text
soil_temperature_10cm_estimate
degree_days_10c
```

должны принадлежать:

```text
RiskContext
```

и не:

```text
WeatherData
```

---

# 185. No Duplicate Source of Truth

Не допускается финальное состояние:

```text
WeatherData.degree_days_10c
+
RiskContext.degree_days_10c
```

или:

```text
WeatherData.soil_temperature_10cm_estimate
+
RiskContext.soil_temperature_10cm_estimate
```

После migration существует только один canonical owner.

---

# 186. No Compatibility Shim

Не создаём property:

```python
WeatherData.degree_days_10c
```

который проксирует значение из context.

Не создаём deprecated aliases.

Проект ещё находится до публичного стабильного Assessment API, поэтому внутреннюю границу меняем чисто.

---

# 187. No Derived Recalculation inside Calculator

Например, Colorado Calculator не должен делать:

```text
если estimate отсутствует
→ взять T6/T18
→ самому интерполировать
```

Missing остаётся:

```text
MISSING
```

Аналогично Codling Calculator не должен сам считать Degree Days.

---

# 188. Architecture Review Questions

Перед merge необходимо ответить `YES` на:

```text
1. WeatherData снова представляет только weather observations?

2. Derived indicators находятся вне WeatherData?

3. RiskContext является единственным calculation-input aggregate?

4. RiskContext immutable?

5. RiskContext не содержит services?

6. RiskContext не содержит Location/UserProfile/Threat?

7. Все четыре Calculator используют RiskContext?

8. Ни один Calculator не получает данные самостоятельно?

9. WeatherService больше не рассчитывает T10?

10. HistoricalWeatherService не считает Degree Days?

11. RiskPolicy не изменился?

12. Biological thresholds не изменились?

13. Existing risk outcomes сохранены?

14. Assessment не реализован преждевременно?

15. Persistence не затронут?
```

Любой ответ:

```text
NO
```

требует review до merge.

---

# 189. Scope Review Questions

Перед staging проверить:

```text
Появился ли новый user-facing behavior?
→ должен быть NO

Добавился ли новый threat?
→ NO

Изменились ли thresholds?
→ NO

Добавился ли новый external API call?
→ NO

Появился ли Assessment?
→ NO

Изменилась ли database schema?
→ NO

Добавился ли новый REST endpoint?
→ NO
```

---

# 190. Expected Production Files

Ожидается новый:

```text
app/domain/risk_context.py
```

Ожидаются изменения:

```text
app/domain/__init__.py

app/domain/weather_data.py

app/risk/calculator.py

app/risk/calculators/tick.py

app/risk/calculators/cabbage_aphid.py

app/risk/calculators/colorado_beetle.py

app/risk/calculators/codling_moth.py

app/services/weather_service.py
```

Другие production files меняются только при доказанной необходимости.

---

# 191. Expected Test Files

Новый:

```text
tests/unit/domain/test_risk_context.py
```

Ожидаются изменения существующих:

```text
tests/unit/domain/test_weather_data.py

tests/unit/risk/test_risk_calculator.py

tests/unit/risk/calculators/test_tick.py

tests/unit/risk/calculators/test_cabbage_aphid.py

tests/unit/risk/test_colorado_beetle.py
или фактический текущий файл Colorado tests

tests/unit/risk/calculators/test_codling_moth.py

tests/unit/services/test_weather_service.py

tests/integration/test_threat_risk_calculators.py

tests/integration/test_colorado_beetle_risk.py

tests/integration/test_codling_moth_risk.py
```

Точный список определяется фактическими dependencies.

---

# 192. Files Expected Not To Change

Без отдельного обоснования не должны изменяться:

```text
app/risk/policy.py

app/risk/evaluation.py

app/risk/engine.py

app/weather/soil_temperature_estimator.py

app/weather/degree_days_calculator.py

app/integrations/weather/client.py

app/integrations/weather/historical_client.py

app/integrations/weather/adapter.py

app/integrations/weather/historical_adapter.py

app/services/historical_weather_service.py

database models

repositories

controllers
```

Если какой-либо из них меняется, перед commit требуется объяснить причину.

---

# 193. Documentation During EPIC-09

Исходный системный документ пока не редактируется параллельно каждому slice.

Сначала завершается implementation + architecture review.

После merge EPIC-09 выполняется:

```text
Documentation Alignment
```

и документируется уже окончательное состояние.

---

# 194. Source Traceability

EPIC-09 не меняет scientific/biological source traceability.

Причина изменения — архитектурная:

```text
separation of responsibilities
+
explicit calculation-input boundary
```

Поэтому новый внешний биологический источник для EPIC-09 не требуется.

---

# 195. Architectural Traceability

Причина решения должна быть зафиксирована:

```text
EPIC-07
→ появился SoilTemperatureEstimate

EPIC-08
→ появился DegreeDaysResult

WeatherData
→ начал содержать observations + derived facts

Gap Analysis
→ выявлена перегрузка ответственности

Architecture Decision
→ выбран RiskContext

EPIC-09
→ реализует принятое решение
```

---

# 196. Acceptance Criteria — Domain

- [ ] создан `RiskContext`
- [ ] `RiskContext` immutable
- [ ] `weather` required
- [ ] `soil_temperature_10cm_estimate` optional
- [ ] `degree_days_10c` optional
- [ ] `Location` отсутствует
- [ ] `UserProfile` отсутствует
- [ ] `Threat` отсутствует
- [ ] services отсутствуют
- [ ] persistence dependencies отсутствуют

---

# 197. Acceptance Criteria — WeatherData

- [ ] `WeatherData` содержит только normalized current/provider observations
- [ ] `soil_temperature_10cm_estimate` удалён
- [ ] `degree_days_10c` удалён
- [ ] `soil_temperature_6cm` сохранён
- [ ] `soil_temperature_18cm` сохранён
- [ ] `soil_temperature` сохранён
- [ ] current WeatherAdapter продолжает работать

---

# 198. Acceptance Criteria — WeatherService

- [ ] принимает `WeatherClient`
- [ ] принимает `WeatherAdapter`
- [ ] не принимает `SoilTemperatureEstimator`
- [ ] передаёт координаты Client
- [ ] передаёт payload Adapter
- [ ] возвращает `WeatherData`
- [ ] не создаёт `SoilTemperatureEstimate`
- [ ] не создаёт `RiskContext`

---

# 199. Acceptance Criteria — RiskCalculator

- [ ] canonical input = `RiskContext`
- [ ] старый `WeatherData` contract удалён
- [ ] compatibility overload отсутствует

---

# 200. Acceptance Criteria — Tick

- [ ] использует `context.weather.temperature`
- [ ] threshold не изменён
- [ ] missing semantics не изменена
- [ ] explanations не изменены
- [ ] outcomes не изменены

---

# 201. Acceptance Criteria — Cabbage Aphid

- [ ] использует `context.weather.temperature`
- [ ] использует `context.weather.humidity`
- [ ] thresholds не изменены
- [ ] missing semantics не изменена
- [ ] outcomes не изменены

---

# 202. Acceptance Criteria — Colorado Beetle

- [ ] использует `context.soil_temperature_10cm_estimate`
- [ ] не использует T6/T18 непосредственно
- [ ] не выполняет interpolation
- [ ] threshold `13.0` не изменён
- [ ] missing semantics не изменена
- [ ] outcomes не изменены

---

# 203. Acceptance Criteria — Codling Moth

- [ ] использует `context.degree_days_10c`
- [ ] не получает historical data самостоятельно
- [ ] не рассчитывает Degree Days
- [ ] threshold `130.0` не изменён
- [ ] missing semantics не изменена
- [ ] outcomes не изменены

---

# 204. Acceptance Criteria — Existing Derived Models

- [ ] `SoilTemperatureEstimate` не изменён семантически
- [ ] `SoilTemperatureEstimateMethod` не изменён
- [ ] `SoilTemperatureEstimator` formula не изменена
- [ ] provenance T10 сохранён
- [ ] `DailyTemperature` не изменён семантически
- [ ] `DegreeDaysResult` не изменён семантически
- [ ] `DegreeDaysCalculationMethod` не изменён
- [ ] `DegreeDaysCalculator` formula не изменена
- [ ] provenance Degree Days сохранён
- [ ] missing-data semantics Degree Days сохранена
- [ ] chronology semantics сохранена
- [ ] calendar-gap semantics сохранена

---

# 205. Acceptance Criteria — Risk Engine

- [ ] `RiskEngine` остаётся generic
- [ ] `RiskPolicy` не изменён
- [ ] `RiskEvaluation` не изменён
- [ ] `RiskLevel` semantics не изменена
- [ ] `RiskStatus` semantics не изменена
- [ ] `RiskFactorState` semantics не изменена
- [ ] `RiskFactorResult` semantics не изменена
- [ ] Risk Engine не получает weather/provider data самостоятельно
- [ ] Risk Engine не выполняет derived calculations
- [ ] существующие aggregation outcomes сохранены

---

# 206. Acceptance Criteria — Integration Boundaries

- [ ] `WeatherClient` contract не изменён
- [ ] `WeatherAdapter` provider mapping сохранён
- [ ] `HistoricalWeatherClient` contract не изменён
- [ ] `HistoricalWeatherAdapter` contract не изменён
- [ ] `HistoricalWeatherService` contract не изменён
- [ ] новые HTTP calls не добавлены
- [ ] новые Weather API fields не добавлены
- [ ] provider-specific JSON не попадает в `RiskContext`
- [ ] provider-specific детали не попадают в Risk Calculators

---

# 207. Acceptance Criteria — Behavioral Equivalence

Для эквивалентных входных данных результаты до и после EPIC-09 должны совпадать.

Проверяется:

```text
TICK
→ same RiskFactorResult
→ same RiskResult

CABBAGE_APHID
→ same RiskFactorResult[]
→ same RiskResult

COLORADO_BEETLE
→ same RiskFactorResult
→ same RiskResult

CODLING_MOTH
→ same RiskFactorResult
→ same RiskResult
```

Не должны измениться:

```text
factor
state
actual_value
expected
explanation
required
risk_level
status
```

---

# 208. Acceptance Criteria — Missing Data

Должна сохраниться существующая semantics:

```text
temperature=None
→ Tick MISSING

temperature/humidity missing
→ соответствующий Cabbage Aphid factor MISSING

soil_temperature_10cm_estimate=None
→ Colorado Beetle MISSING

degree_days_10c=None
→ Codling Moth MISSING
```

При этом отсутствие одного derived input не делает весь `RiskContext` невалидным.

---

# 209. Acceptance Criteria — Partial Context

Валиден:

```python
RiskContext(
    weather=weather,
)
```

Также валиден:

```python
RiskContext(
    weather=weather,
    soil_temperature_10cm_estimate=estimate,
)
```

Также валиден:

```python
RiskContext(
    weather=weather,
    degree_days_10c=degree_days,
)
```

И:

```python
RiskContext(
    weather=weather,
    soil_temperature_10cm_estimate=estimate,
    degree_days_10c=degree_days,
)
```

`RiskContext` не требует наличия всех возможных derived indicators.

---

# 210. Acceptance Criteria — Provenance

Перенос ownership не должен уничтожить provenance.

Для:

```text
SoilTemperatureEstimate
```

сохраняются:

```text
depth_cm
temperature
source_depths_cm
source_temperatures
method
```

Для:

```text
DegreeDaysResult
```

сохраняются:

```text
base_temperature
total
period_start
period_end
observations
method
```

`RiskContext` хранит эти objects целиком и не копирует их provenance в собственные поля.

---

# 211. Acceptance Criteria — Architecture

- [ ] `WeatherData` не содержит derived indicators
- [ ] `RiskContext` является canonical calculation-input aggregate
- [ ] `RiskContext` не является service locator
- [ ] `RiskContext` не является generic dictionary
- [ ] `RiskContext` не выполняет calculations
- [ ] `WeatherService` не выполняет derived calculations
- [ ] Calculators не вызывают services
- [ ] Calculators не вызывают estimators
- [ ] Calculators не вызывают external providers
- [ ] derived calculators не знают Risk Engine
- [ ] integration layer не знает biological thresholds
- [ ] duplicate source of truth отсутствует

---

# 212. Acceptance Criteria — Scope

В EPIC-09 отсутствуют:

```text
Assessment

AssessmentService

RiskContextBuilder

RiskContextFactory

production RiskContext orchestration

Assessment persistence

database migrations

new repositories

new controllers

new REST endpoints

new UI

new threats

new biological rules

new thresholds

new weather indicators
```

---

# 213. Full Regression Gate

Перед staging:

```powershell
python -m pytest
```

Обязательный результат:

```text
0 failed
0 errors
```

Baseline до EPIC-09:

```text
277 passed
```

Итоговое количество tests должно быть не меньше baseline с поправкой только на осознанное удаление obsolete tests и добавление новой RiskContext test matrix.

Само число tests не является главным acceptance criterion.

Главный критерий:

```text
all applicable EPIC-01–08 behavior remains green
```

---

# 214. Architecture Gate — WeatherData

Выполнить:

```powershell
Get-Content .\app\domain\weather_data.py |
    Select-String -Pattern "SoilTemperatureEstimate|DegreeDaysResult|RiskContext"
```

Ожидаем:

```text
empty
```

---

# 215. Architecture Gate — RiskContext Infrastructure Isolation

Выполнить:

```powershell
Get-Content .\app\domain\risk_context.py |
    Select-String -Pattern "requests|flask|sqlalchemy|WeatherClient|WeatherService|HistoricalWeatherService|Repository|db\."
```

Ожидаем:

```text
empty
```

---

# 216. Architecture Gate — RiskContext Domain Boundary

Выполнить:

```powershell
Get-Content .\app\domain\risk_context.py |
    Select-String -Pattern "Location|UserProfile|Threat|RiskLevel|RiskResult|Recommendation|Source"
```

Ожидаем:

```text
empty
```

Допустимые domain dependencies:

```text
WeatherData
SoilTemperatureEstimate
DegreeDaysResult
```

---

# 217. Architecture Gate — WeatherService

Выполнить:

```powershell
Get-Content .\app\services\weather_service.py |
    Select-String -Pattern "SoilTemperatureEstimator|RiskContext|DegreeDays|Historical|RiskCalculator|RiskEngine"
```

Ожидаем:

```text
empty
```

---

# 218. Architecture Gate — Calculators use RiskContext

Выполнить:

```powershell
Get-ChildItem .\app\risk\calculators\*.py |
    Select-String -Pattern "RiskContext"
```

Ожидаем использование `RiskContext` всеми четырьмя calculators:

```text
TickRiskCalculator
CabbageAphidRiskCalculator
ColoradoBeetleRiskCalculator
CodlingMothRiskCalculator
```

---

# 219. Architecture Gate — No Old Derived Access

В production code не должно остаться обращений:

```text
weather.soil_temperature_10cm_estimate

weather.degree_days_10c
```

Проверить:

```powershell
Get-ChildItem .\app\*.py,.\app\*\*.py,.\app\*\*\*.py |
    Select-String -Pattern "weather\.soil_temperature_10cm_estimate|weather\.degree_days_10c"
```

Ожидаем:

```text
empty
```

---

# 220. Architecture Gate — Colorado Isolation

Выполнить:

```powershell
Get-Content .\app\risk\calculators\colorado_beetle.py |
    Select-String -Pattern "6cm|18cm|interpol|WeatherClient|WeatherService|SoilTemperatureEstimator|requests"
```

Ожидаем:

```text
empty
```

Colorado Calculator должен знать только готовый:

```text
SoilTemperatureEstimate
```

через `RiskContext`.

---

# 221. Architecture Gate — Codling Moth Isolation

Выполнить:

```powershell
Get-Content .\app\risk\calculators\codling_moth.py |
    Select-String -Pattern "HistoricalWeather|temperature_2m_mean|DailyTemperature|DegreeDaysCalculator|requests|archive-api"
```

Ожидаем:

```text
empty
```

Codling Calculator должен знать только готовый:

```text
DegreeDaysResult
```

через `RiskContext`.

---

# 222. Architecture Gate — No Threshold Drift

Выполнить:

```powershell
Get-ChildItem .\app\risk\calculators\*.py |
    Select-String -Pattern "10.0|13.0|25.0|26.0|60.0|70.0|130.0"
```

Результат сравнивается с состоянием EPIC-08.

EPIC-09 не должен:

```text
добавлять threshold

удалять threshold

изменять threshold
```

---

# 223. Architecture Gate — No New Integration Dependency

Выполнить:

```powershell
Get-ChildItem .\app\risk\*.py,.\app\risk\calculators\*.py |
    Select-String -Pattern "requests|open-meteo|WeatherClient|HistoricalWeatherClient|WeatherService|HistoricalWeatherService"
```

Ожидаем:

```text
empty
```

---

# 224. Scope Gate — Production Files

Перед staging:

```powershell
git status --short
```

Фактический production scope сверяется с ожидаемым.

Ожидаемый новый production file:

```text
app/domain/risk_context.py
```

Ожидаемые modified production files:

```text
app/domain/__init__.py
app/domain/weather_data.py

app/risk/calculator.py

app/risk/calculators/tick.py
app/risk/calculators/cabbage_aphid.py
app/risk/calculators/colorado_beetle.py
app/risk/calculators/codling_moth.py

app/services/weather_service.py
```

Отклонения требуют review.

---

# 225. Scope Gate — Forbidden New Files

Не должны появиться:

```text
app/domain/assessment.py

app/services/assessment_service.py

app/services/risk_context_service.py

app/risk/context_builder.py

app/risk/context_factory.py

app/repositories/assessment_repository.py

новые controller files

новые migration files
```

---

# 226. Scope Gate — Existing Stable Components

Без отдельного обоснования не должны изменяться:

```text
app/risk/policy.py
app/risk/evaluation.py
app/risk/engine.py

app/weather/soil_temperature_estimator.py
app/weather/degree_days_calculator.py

app/integrations/weather/client.py
app/integrations/weather/historical_client.py
app/integrations/weather/adapter.py
app/integrations/weather/historical_adapter.py

app/services/historical_weather_service.py
```

---

# 227. Final Diff Review

После staging:

```powershell
git diff --cached --stat
```

и:

```powershell
git diff --cached --name-only
```

проверяются до commit.

Цель:

```text
убедиться, что PR содержит только Risk Context Refactoring
```

---

# 228. Final Regression после Staging

После:

```powershell
git add .
```

ещё раз:

```powershell
python -m pytest
```

Обязательный результат:

```text
0 failed
0 errors
```

---

# 229. Commit

Предлагаемое сообщение:

```text
EPIC-09: introduce risk context
```

---

# 230. Pull Request

Предлагаемый title:

```text
EPIC-09: Introduce Risk Context
```

PR должен явно описывать изменение границы:

```text
WeatherData
→ weather observations only

RiskContext
→ prepared calculation inputs
```

и отдельно указать:

```text
no business-rule changes
```

---

# 231. Definition of Done — Domain

EPIC-09 Domain считается завершённым, если:

```text
RiskContext существует

RiskContext immutable

WeatherData очищен от derived indicators

SoilTemperatureEstimate остаётся самостоятельным domain object

DegreeDaysResult остаётся самостоятельным domain object

canonical ownership однозначен
```

---

# 232. Definition of Done — Risk Layer

Risk layer считается завершённым, если:

```text
RiskCalculator принимает RiskContext

Tick использует RiskContext

Cabbage Aphid использует RiskContext

Colorado Beetle использует RiskContext

Codling Moth использует RiskContext

RiskPolicy не изменён

RiskEvaluation не изменён

RiskEngine semantics не изменена
```

---

# 233. Definition of Done — Service Layer

Service boundary считается завершённой, если:

```text
WeatherService
→ current weather orchestration only

HistoricalWeatherService
→ historical weather orchestration only

SoilTemperatureEstimator
→ independent derived calculation

DegreeDaysCalculator
→ independent derived calculation
```

Ни один из этих компонентов не создаёт production `RiskContext`.

---

# 234. Definition of Done — Behavioral Equivalence

Для всех четырёх угроз:

```text
same logical input
→ same factor result
→ same risk result
```

Refactoring не изменяет пользовательскую risk semantics.

---

# 235. Definition of Done — Architecture

Должно выполняться:

```text
WeatherData
→ observations

SoilTemperatureEstimate
→ derived soil fact + provenance

DegreeDaysResult
→ derived historical fact + provenance

RiskContext
→ calculation input composition

RiskFactorResult
→ rule evaluation result

RiskResult
→ threat evaluation result
```

Не существует второго source of truth для derived indicators.

---

# 236. Definition of Done — Scope

Не реализованы преждевременно:

```text
Assessment
AssessmentService
RiskContextBuilder
RiskContextFactory
Persistence
REST
UI
```

EPIC-09 остаётся чистым refactoring EPIC.

---

# 237. Definition of Done — Quality

Обязательно:

```text
full regression green

architecture gates green

scope review green

no threshold drift

no provider contract changes

no business semantics changes
```

---

# 238. Final DoD

EPIC-09 считается завершённым при выполнении цепочки:

```text
RiskContext Domain Model
        +
WeatherData Responsibility Cleanup
        +
RiskCalculator Contract Migration
        +
Tick Migration
        +
Cabbage Aphid Migration
        +
Colorado Beetle Migration
        +
Codling Moth Migration
        +
WeatherService Responsibility Cleanup
        +
Unit Test Migration
        +
Integration Test Migration
        +
Behavioral Equivalence
        +
Provenance Preservation
        +
Architecture Gates
        +
Scope Gate
        +
Full Regression
        ↓
EPIC-09 DONE
```

---

# 239. Состояние архитектуры после EPIC-09

Canonical calculation architecture:

```text
Current Weather API
        ↓
WeatherClient
        ↓
WeatherAdapter
        ↓
WeatherService
        ↓
WeatherData
        │
        ├─────────────────────────┐
        │                         │
        ▼                         │
SoilTemperatureEstimator         │
        ↓                         │
SoilTemperatureEstimate          │
                                  │
Historical Weather API            │
        ↓                         │
HistoricalWeatherClient           │
        ↓                         │
HistoricalWeatherAdapter          │
        ↓                         │
HistoricalWeatherService          │
        ↓                         │
DailyTemperature[]                │
        ↓                         │
DegreeDaysCalculator              │
        ↓                         │
DegreeDaysResult                  │
        │                         │
        └────────────┬────────────┘
                     ↓
                RiskContext
                     ↓
              RiskCalculator
                     ↓
            RiskFactorResult[]
                     ↓
                RiskEngine
                     ↓
                RiskResult
```

---

# 240. Следующий шаг после EPIC-09

После merge EPIC-09:

```text
main
    ↓
Documentation Alignment
```

В системной документации фиксируется уже окончательная модель:

```text
WeatherData
Derived Indicators
RiskContext
Risk Calculators
Current Weather
Historical Weather
```

После Documentation Alignment:

```text
Assessment Contract
```

И только затем начинается следующий функциональный EPIC.

---

# 241. Contract Status

После архитектурного review:

```text
EPIC-09
Risk Context Refactoring

STATUS:
READY FOR APPROVAL
```

После утверждения:

```text
create branch
feature/epic-09-risk-context-refactoring
```

Первый implementation slice:

```text
RiskContext domain model only
```

Никакие другие production contracts в первом slice не меняются.
