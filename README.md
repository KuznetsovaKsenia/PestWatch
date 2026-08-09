# EPIC-08 — Historical Weather, Degree Days & Codling Moth Risk

## 1. Цель EPIC

Реализовать четвёртую и последнюю предметную расчётную модель MVP PestWatch — оценку сезонного риска яблонной плодожорки на основании накопленной суммы эффективных температур.

Исходная декомпозиция проекта предусматривает для яблонной плодожорки:

- `DegreeDaysCalculator`;
- базовую температуру;
- расчёт эффективной температуры;
- накопление суммы эффективных температур;
- получение исторических температур;
- расчёт риска;
- обработку недостатка данных;
- unit-тесты.

После EPIC-08 все четыре угрозы MVP будут иметь независимые проверяемые расчётные модели.

---

## 2. Git

Базовая ветка:

```text
main
```

Рабочая ветка:

```text
feature/epic-08-codling-moth-degree-days
```

Pull Request:

```text
EPIC-08: Historical Weather and Codling Moth Degree Days
```

---

## 3. Целевая архитектурная цепочка

```text
Location
    +
assessment date
        ↓
HistoricalWeatherClient
        ↓
HistoricalWeatherAdapter
        ↓
DailyTemperature[]
        ↓
DegreeDaysCalculator
        ↓
DegreeDaysResult
        ↓
WeatherData
        ↓
CodlingMothRiskCalculator
        ↓
RiskFactorResult[]
        ↓
RiskEngine
        ↓
RiskResult
```

После завершения EPIC-08 предметная часть MVP:

```text
TICK               ✓
CABBAGE_APHID      ✓
COLORADO_BEETLE    ✓
CODLING_MOTH       ✓
```

---

## 4. Основной принцип

PestWatch не прогнозирует точное появление яблонной плодожорки.

Система оценивает:

```text
соответствуют ли накопленные температурные условия
сезонному периоду активности вредителя
```

Результат является:

```text
seasonal risk indicator
```

а не:

```text
вероятностью появления вредителя
```

и не:

```text
точной датой лёта
```

---

## 5. Weather Provider

Используется:

```text
Open-Meteo Historical Weather API
```

Endpoint:

```text
https://archive-api.open-meteo.com/v1/archive
```

Для Degree Days необходим временной ряд дневных температур.

Текущий Forecast API и текущий погодный snapshot для этого недостаточны.

---

## 6. Почему отдельный HistoricalWeatherClient

Существующий:

```text
WeatherClient
```

отвечает за:

```text
current weather
```

Новый:

```text
HistoricalWeatherClient
```

отвечает за:

```text
historical daily weather
```

Эти integrations имеют разные:

```text
endpoint
request contract
response contract
date range
use case
```

Поэтому они не объединяются в один универсальный client.

Предлагаемая структура:

```text
app/integrations/weather/
├── client.py
├── adapter.py
├── exceptions.py
├── historical_client.py
└── historical_adapter.py
```

---

## 7. Historical Weather Request Contract

PestWatch запрашивает:

```text
latitude
longitude
start_date
end_date
daily=temperature_2m_mean
temperature_unit=celsius
timezone=auto
```

Основной погодный показатель:

```text
temperature_2m_mean
```

То есть средняя дневная температура воздуха на высоте 2 м.

---

## 8. Почему используется temperature_2m_mean

Не используется собственный расчёт:

```text
(Tmin + Tmax) / 2
```

поскольку provider уже предоставляет:

```text
temperature_2m_mean
```

Это уменьшает количество собственных инженерных предположений PestWatch.

---

## 9. API Key

В выбранном публичном режиме Open-Meteo API key не требуется.

Не добавляем фиктивную конфигурацию:

```text
WEATHER_API_KEY
```

---

## 10. Configuration

Добавляется:

```text
WEATHER_ARCHIVE_API_BASE_URL
```

Значение:

```text
https://archive-api.open-meteo.com/v1/archive
```

Существующий:

```text
WEATHER_API_TIMEOUT_SECONDS
```

используется также для historical request.

---

## 11. Assessment Date

Degree Days рассчитываются относительно:

```text
assessment_date
```

Например:

```text
assessment_date = 2026-08-09
```

---

## 12. Начало периода

Для MVP фиксируется:

```text
period_start = 1 января assessment year
```

Например:

```text
assessment_date = 2026-08-09

period_start = 2026-01-01
```

Это инженерное решение PestWatch.

Официальные источники подтверждают использование накопленной СЭТ выше базовой температуры 10 °C, но не дают универсальный программный контракт начальной календарной даты для нашего приложения.

---

## 13. Почему можно начинать с 1 января

Дни, средняя температура которых:

```text
<= 10 °C
```

дают вклад:

```text
0
```

Поэтому зимние холодные дни не увеличивают СЭТ.

Такое начало периода:

```text
детерминировано
воспроизводимо
не требует дополнительной региональной фенологической даты
```

---

## 14. Конец периода

Используются только полностью завершённые сутки.

```text
period_end = assessment_date - 1 day
```

Например:

```text
assessment_date = 2026-08-09

period_end = 2026-08-08
```

---

## 15. Почему не используется текущий день

Не смешиваются:

```text
полностью завершённые historical days
```

и:

```text
частично прошедшие текущие сутки
```

Также не подмешивается forecast остатка дня.

EPIC-08 ориентирован на:

```text
deterministic
reproducible
historical accumulation
```

---

## 16. Current-day Degree Days

В EPIC-08 не реализуются:

```text
partial current-day SET
forecast SET
predicted future SET
```

Это отдельное возможное развитие проекта.

---

## 17. Domain Model — DailyTemperature

Создаётся:

```text
app/domain/daily_temperature.py
```

Модель:

```python
@dataclass(frozen=True)
class DailyTemperature:
    date: date
    mean_temperature: float | None
```

---

## 18. DailyTemperature semantics

`DailyTemperature` является provider-independent domain object.

Он не знает:

```text
Open-Meteo
HTTP
JSON
ERA5
Risk Engine
Codling Moth
```

---

## 19. Missing temperature

Поле:

```python
mean_temperature: float | None
```

явно допускает:

```text
None
```

Отсутствующее значение не превращается в:

```text
0 °C
```

---

## 20. DegreeDaysCalculationMethod

Создаётся:

```text
app/domain/degree_days_calculation_method.py
```

Enum:

```python
class DegreeDaysCalculationMethod(Enum):
    DAILY_MEAN_ABOVE_BASE = "DAILY_MEAN_ABOVE_BASE"
```

---

## 21. Почему method хранится явно

Degree Days являются derived weather indicator.

Для воспроизводимости необходимо сохранить:

```text
какие данные использованы
какая базовая температура использована
каким алгоритмом выполнен расчёт
```

Это тот же принцип provenance, который был реализован для `SoilTemperatureEstimate` в EPIC-07.

---

## 22. DegreeDaysResult

Создаётся:

```text
app/domain/degree_days_result.py
```

Контракт:

```python
@dataclass(frozen=True)
class DegreeDaysResult:
    base_temperature: float
    total: float
    period_start: date
    period_end: date
    observations: tuple[DailyTemperature, ...]
    method: DegreeDaysCalculationMethod
```

---

## 23. DegreeDaysResult provenance

Объект позволяет восстановить:

```text
base_temperature
period_start
period_end
исходный daily series
calculation method
итоговую SET
```

---

## 24. Immutable Domain

Используется:

```python
@dataclass(frozen=True)
```

для:

```text
DailyTemperature
DegreeDaysResult
```

Расчётный результат после создания не изменяется.

---

## 25. WeatherData Extension

Для сохранения общего Calculator contract:

```python
evaluate(weather: WeatherData)
```

`WeatherData` расширяется полем:

```python
degree_days_10c: DegreeDaysResult | None = None
```

Поле добавляется в конец dataclass.

---

## 26. Backward Compatibility

Существующие constructors:

```python
WeatherData(
    observed_at=...,
    temperature=...,
    humidity=...,
    precipitation=...,
    wind_speed=...,
    soil_temperature=...,
)
```

продолжают работать.

Новое поле:

```text
degree_days_10c
```

по умолчанию:

```text
None
```

---

## 27. Architecture Note — WeatherData

Изначально `WeatherData` является snapshot-моделью текущей погоды.

Добавление:

```text
DegreeDaysResult
```

расширяет её роль derived historical indicator.

Для MVP это принимается, чтобы сохранить единый Calculator contract:

```python
evaluate(weather: WeatherData)
```

После MVP, если количество derived/historical факторов существенно увеличится, необходимо рассмотреть отдельную агрегирующую модель:

```text
RiskContext
```

Такой рефакторинг не входит в EPIC-08.

---

## 28. HistoricalWeatherClient

Создаётся:

```text
app/integrations/weather/historical_client.py
```

Контракт:

```python
get_daily_mean_temperatures(
    latitude: float,
    longitude: float,
    start_date: date,
    end_date: date,
) -> dict
```

---

## 29. HistoricalWeatherClient responsibility

Client:

```text
формирует HTTP request
выполняет request
обрабатывает network errors
возвращает JSON payload
```

Client не:

```text
парсит Domain Models
считает Degree Days
знает Codling Moth
знает threshold 130
```

---

## 30. Historical request example

```text
latitude=55.7558
longitude=37.6173

start_date=2026-01-01
end_date=2026-08-08

daily=temperature_2m_mean

temperature_unit=celsius
timezone=auto
```

---

## 31. Historical Client Errors

Используются существующие generic weather integration errors, если их semantics подходят:

```text
WeatherTimeoutError
WeatherConnectionError
WeatherResponseError
```

Новые exception classes не создаются без необходимости.

Если существующий `WeatherResponseError` действительно описывает provider-level HTTP/JSON failure независимо от current/historical endpoint, он переиспользуется.

Если при реализации выяснится, что его контракт привязан именно к current weather, изменение exception hierarchy должно быть отдельно обосновано до реализации.

## 32. HistoricalWeatherAdapter

Создаётся:

```text
app/integrations/weather/historical_adapter.py
```

Он преобразует response provider-а:

```text
Open-Meteo JSON
```

в provider-independent domain collection:

```text
tuple[DailyTemperature, ...]
```

Adapter не:

```text
считает Degree Days
знает base temperature
знает Codling Moth
знает threshold 130
```

---

## 33. Ожидаемый Historical Response

Концептуально:

```json
{
  "daily": {
    "time": [
      "2026-05-01",
      "2026-05-02"
    ],
    "temperature_2m_mean": [
      12.5,
      14.0
    ]
  }
}
```

Результат:

```text
DailyTemperature(
    date=2026-05-01,
    mean_temperature=12.5
)

DailyTemperature(
    date=2026-05-02,
    mean_temperature=14.0
)
```

---

## 34. HistoricalWeatherAdapter validation

Adapter обязан проверить:

```text
daily существует
time существует
temperature_2m_mean существует
time является list
temperature_2m_mean является list
arrays имеют одинаковую длину
dates валидны
```

---

## 35. Missing daily temperature

Если конкретный элемент:

```text
temperature_2m_mean = None
```

Adapter сохраняет:

```python
DailyTemperature(
    date=...,
    mean_temperature=None,
)
```

Adapter не решает, допустим ли partial Degree Days calculation.

Это ответственность:

```text
DegreeDaysCalculator
```

---

## 36. Zero and negative values

Значения:

```text
0.0
-5.0
```

являются валидными температурами.

Они не трактуются как missing.

---

## 37. Invalid Historical Response

Если:

```text
daily отсутствует
```

или:

```text
time отсутствует
```

или:

```text
temperature_2m_mean отсутствует
```

или:

```text
длины arrays различаются
```

или:

```text
date невозможно распарсить
```

Adapter выбрасывает:

```text
WeatherDataError
```

если существующий exception contract является generic для weather-data mapping.

Не создаём отдельный historical exception без необходимости.

---

## 38. HistoricalWeatherService

Создаётся:

```text
app/services/historical_weather_service.py
```

Ответственность:

```text
Location
+
start_date
+
end_date
        ↓
HistoricalWeatherClient
        ↓
raw payload
        ↓
HistoricalWeatherAdapter
        ↓
tuple[DailyTemperature, ...]
```

---

## 39. HistoricalWeatherService Contract

Предлагаемый интерфейс:

```python
class HistoricalWeatherService:
    def __init__(
        self,
        client: HistoricalWeatherClient,
        adapter: HistoricalWeatherAdapter,
    ):
        ...

    def get_daily_temperatures(
        self,
        location: Location,
        start_date: date,
        end_date: date,
    ) -> tuple[DailyTemperature, ...]:
        ...
```

---

## 40. HistoricalWeatherService responsibilities

Service:

```text
передаёт координаты Location клиенту
передаёт диапазон дат
передаёт payload adapter-у
возвращает domain observations
```

Service не:

```text
считает Degree Days
содержит base temperature 10 °C
содержит threshold 130 °C
знает Codling Moth
создаёт RiskResult
```

---

## 41. DegreeDaysCalculator

Создаётся:

```text
app/weather/degree_days_calculator.py
```

Предлагаемый интерфейс:

```python
class DegreeDaysCalculator:
    BASE_TEMPERATURE = 10.0

    def calculate(
        self,
        observations: tuple[DailyTemperature, ...],
    ) -> DegreeDaysResult | None:
        ...
```

---

## 42. DegreeDaysCalculator responsibility

Calculator знает:

```text
base temperature = 10 °C
формулу daily effective temperature
накопление суммы
validation временного ряда
формирование DegreeDaysResult
```

Calculator не знает:

```text
Open-Meteo
HTTP
JSON
Codling Moth
threshold 130
RiskLevel
RiskResult
```

---

## 43. Базовая температура

Для яблонной плодожорки в EPIC-08 используется:

```text
10 °C
```

Это base temperature для расчёта суммы эффективных температур.

---

## 44. Daily Effective Temperature

Для каждого дня:

```text
daily_effective_temperature =
max(
    0,
    mean_temperature - 10
)
```

Примеры:

```text
mean = -5
→ contribution = 0

mean = 5
→ contribution = 0

mean = 9.9
→ contribution = 0

mean = 10.0
→ contribution = 0

mean = 10.1
→ contribution = 0.1

mean = 12.0
→ contribution = 2.0

mean = 20.0
→ contribution = 10.0
```

---

## 45. Сумма эффективных температур

Итоговый показатель:

```text
SET =
Σ daily_effective_temperature
```

То есть:

```text
SET =
Σ max(0, Tmean(day) - 10)
```

Пример:

```text
Daily means:
9
10
12
15
```

Contributions:

```text
0
0
2
5
```

Result:

```text
SET = 7
```

---

## 46. Единицы

Внутреннее поле:

```python
DegreeDaysResult.total
```

хранится как:

```text
float
```

Например:

```text
137.4
```

Семантически это:

```text
137.4 °C·days
```

или в пользовательской терминологии проекта:

```text
137.4 °C СЭТ
```

UI formatting не входит в EPIC-08.

---

## 47. Empty Series

Если:

```python
observations == ()
```

результат:

```text
None
```

Это означает:

```text
недостаточно исторических данных
```

а не:

```text
SET = 0
```

---

## 48. Missing Temperature in Series

Если хотя бы один `DailyTemperature` содержит:

```python
mean_temperature=None
```

Calculator возвращает:

```text
None
```

В MVP partial Degree Days не рассчитываются.

Причина:

```text
неизвестный вклад одного дня
→ неизвестна итоговая накопленная сумма
```

---

## 49. Chronological Order

Input должен быть отсортирован:

```text
oldest
→
newest
```

Например:

```text
2026-05-01
2026-05-02
2026-05-03
```

Если series идёт:

```text
2026-05-02
2026-05-01
```

Calculator выбрасывает:

```text
ValueError
```

Не выполняем silent sorting.

---

## 50. Duplicate Dates

Input:

```text
2026-05-01
2026-05-01
```

является invalid contract.

Результат:

```text
ValueError
```

Duplicate date означает upstream/data-contract defect, а не недостаток погодных данных.

---

## 51. Missing Calendar Day

Например:

```text
2026-05-01
2026-05-03
```

без:

```text
2026-05-02
```

означает incomplete historical series.

Calculator возвращает:

```text
None
```

Разделяем:

```text
unsorted / duplicate
→ invalid contract
→ ValueError

calendar gap
→ incomplete provider data
→ None
```

---

## 52. DegreeDaysResult period

Если observations валидны и contiguous:

```text
period_start = observations[0].date
period_end = observations[-1].date
```

Calculator не получает period отдельно.

Тем самым provenance строится непосредственно по фактически использованному ряду.

---

## 53. DegreeDaysResult creation

При успешном расчёте:

```python
DegreeDaysResult(
    base_temperature=10.0,
    total=calculated_total,
    period_start=observations[0].date,
    period_end=observations[-1].date,
    observations=observations,
    method=DegreeDaysCalculationMethod.DAILY_MEAN_ABOVE_BASE,
)
```

---

## 54. CodlingMothRiskCalculator

Создаётся:

```text
app/risk/calculators/codling_moth.py
```

Threat code:

```text
CODLING_MOTH
```

Calculator использует:

```text
WeatherData.degree_days_10c
```

и не получает historical observations напрямую.

---

## 55. Codling Moth Factor

Используется один фактор:

```text
DEGREE_DAYS_ABOVE_10C
```

Он:

```text
required=True
```

---

## 56. Seasonal Threshold

Для MVP фиксируется:

```text
130 °C СЭТ
```

с base temperature:

```text
10 °C
```

Правило:

```text
degree_days_10c is None
→ MISSING

total < 130
→ NOT_MATCHED

total >= 130
→ MATCHED
```

---

## 57. Почему используется 130 °C

`130 °C СЭТ` используется как:

```text
сезонный ориентир,
связанный с началом лёта
яблонной плодожорки
```

Он не трактуется как:

```text
гарантированная дата появления вредителя
```

или:

```text
точная граница массового лёта
```

Наблюдаемые фактические значения могут отличаться между сезонами.

---

## 58. Почему не используется 117.9 °C

В исследовании PestWatch значение:

```text
117.9 °C
```

зафиксировано как фактическая СЭТ на момент массового лёта в Тамбовской области в мае 2026 года.

Это:

```text
наблюдение конкретного сезона
```

а не:

```text
универсальный нормативный threshold
```

Поэтому в коде не создаётся:

```text
CODLING_MOTH_THRESHOLD = 117.9
```

---

## 59. Почему не используется 104.7 °C

Аналогично, наблюдавшееся в другом сезоне значение:

```text
104.7 °C
```

не используется как universal threshold.

Изменчивость фактических наблюдений подтверждает, что PestWatch должен показывать:

```text
seasonal risk indicator
```

а не точный биологический прогноз.

---

## 60. RiskFactorResult — MATCHED

Например:

```text
SET = 137.4
```

Calculator возвращает:

```text
factor:
DEGREE_DAYS_ABOVE_10C

state:
MATCHED

actual_value:
137.4

expected:
>= 130 °C СЭТ при базовой температуре 10 °C

required:
True
```

---

## 61. Explanation — MATCHED

Предлагаемый текст:

```text
Накопленная сумма эффективных температур
достигла уровня, связанного с началом
сезонного лёта яблонной плодожорки.
```

---

## 62. Explanation — NOT_MATCHED

```text
Накопленная сумма эффективных температур
пока ниже ориентира, связанного с началом
сезонного лёта яблонной плодожорки.
```

Не допускается:

```text
Яблонной плодожорки нет.
```

---

## 63. Explanation — MISSING

```text
Недостаточно исторических температур
для расчёта сезонного показателя
яблонной плодожорки.
```

---

## 64. RiskLevel consequence

У Calculator один required binary factor.

По существующей RiskPolicy:

```text
MATCHED
→ CALCULATED
→ HIGH

NOT_MATCHED
→ CALCULATED
→ LOW

MISSING
→ INSUFFICIENT_DATA
→ risk_level=None
```

Не добавляем искусственные факторы только ради появления:

```text
MODERATE
ELEVATED
```

---

## 65. Что не входит в модель плодожорки EPIC-08

Не реализуются:

```text
actual pheromone-trap observations
дата фактического начала массового лёта
larval emergence
egg laying
second generation
future flight forecast
```

EPIC-08 содержит только первый сезонный Degree Days indicator.

---

## 66. Larval Emergence

Материалы Россельхозцентра используют также дополнительную СЭТ после начала массового лёта для оценки отрождения гусениц.

Это правило требует известной даты:

```text
начала массового лёта
```

PestWatch не имеет данных феромонных ловушек для конкретной территории.

Поэтому такое правило не реализуется.

---

## 67. Second Generation

EPIC-08 не моделирует:

```text
второе поколение яблонной плодожорки
```

Даже если официальные материалы содержат дополнительные accumulated-temperature ориентиры.

Для MVP достаточно:

```text
первичного сезонного индикатора
```

---

## 68. Egg-laying Temperature

Не добавляется дополнительный factor:

```text
AIR_TEMPERATURE_FOR_EGG_LAYING
```

Цель EPIC-08:

```text
Degree Days seasonal model
```

а не полный фенологический simulator.

---

## 69. Responsibility Separation

Итоговое разделение:

```text
HistoricalWeatherClient
→ HTTP

HistoricalWeatherAdapter
→ provider JSON → DailyTemperature[]

HistoricalWeatherService
→ orchestration

DegreeDaysCalculator
→ temperature-series mathematics

CodlingMothRiskCalculator
→ biological threshold 130

RiskEngine
→ generic aggregation
```

---

## 70. Главная архитектурная граница

Ни один слой не должен знать больше, чем ему требуется.

```text
Historical Weather Integration
не знает плодожорку

DegreeDaysCalculator
не знает threshold 130

CodlingMothRiskCalculator
не знает Open-Meteo

RiskEngine
не знает ни Degree Days,
ни плодожорку,
ни Historical Weather API
```

## 71. Test Structure

Предлагаемая структура автоматизированных тестов:

```text
tests/unit/domain/
├── test_daily_temperature.py
├── test_degree_days_result.py
└── test_weather_data.py

tests/unit/integrations/weather/
├── test_historical_weather_client.py
└── test_historical_weather_adapter.py

tests/unit/services/
└── test_historical_weather_service.py

tests/unit/weather/
└── test_degree_days_calculator.py

tests/unit/risk/calculators/
└── test_codling_moth.py

tests/integration/
└── test_codling_moth_risk.py
```

---

## 72. DailyTemperature Tests

Проверить:

```text
объект создаётся
date сохраняется
mean_temperature сохраняется
None допускается
zero допускается
negative temperature допускается
объект immutable
```

---

## 73. DegreeDaysCalculationMethod Tests

Проверить стабильное значение:

```text
DAILY_MEAN_ABOVE_BASE
```

---

## 74. DegreeDaysResult Tests

Проверить:

```text
base_temperature сохраняется
total сохраняется
period_start сохраняется
period_end сохраняется
observations сохраняются
method сохраняется
объект immutable
```

---

## 75. WeatherData Backward Compatibility Tests

Проверить, что старый constructor продолжает работать:

```python
WeatherData(
    observed_at=...,
    temperature=...,
    humidity=...,
    precipitation=...,
    wind_speed=...,
    soil_temperature=...,
)
```

и:

```text
weather.degree_days_10c is None
```

Также проверить, что `WeatherData` может хранить:

```text
DegreeDaysResult
```

---

## 76. HistoricalWeatherClient Request Test

Проверить точный HTTP contract:

```text
latitude
longitude
start_date
end_date
daily=temperature_2m_mean
temperature_unit=celsius
timezone=auto
timeout
```

Пример expected params:

```python
{
    "latitude": 55.7558,
    "longitude": 37.6173,
    "start_date": "2026-01-01",
    "end_date": "2026-08-08",
    "daily": "temperature_2m_mean",
    "temperature_unit": "celsius",
    "timezone": "auto",
}
```

---

## 77. HistoricalWeatherClient Error Tests

Проверить:

```text
requests.Timeout
→ WeatherTimeoutError

requests.ConnectionError
→ WeatherConnectionError

HTTP error
→ WeatherResponseError

invalid JSON
→ WeatherResponseError
```

Если в процессе реализации существующие exception contracts окажутся current-weather-specific, это должно быть исправлено отдельно и покрыто regression tests.

---

## 78. HistoricalWeatherAdapter — Complete Payload

Payload:

```json
{
  "daily": {
    "time": [
      "2026-05-01",
      "2026-05-02",
      "2026-05-03"
    ],
    "temperature_2m_mean": [
      12.5,
      14.0,
      9.0
    ]
  }
}
```

Expected:

```text
DailyTemperature(
    date=2026-05-01,
    mean_temperature=12.5
)

DailyTemperature(
    date=2026-05-02,
    mean_temperature=14.0
)

DailyTemperature(
    date=2026-05-03,
    mean_temperature=9.0
)
```

Порядок должен сохраняться.

---

## 79. HistoricalWeatherAdapter — Zero Values

Payload:

```text
temperature_2m_mean = [0.0]
```

Expected:

```text
mean_temperature == 0.0
mean_temperature is not None
```

---

## 80. HistoricalWeatherAdapter — Negative Values

Payload:

```text
temperature_2m_mean = [-5.0]
```

Expected:

```text
mean_temperature == -5.0
```

---

## 81. HistoricalWeatherAdapter — Missing Value

Payload:

```text
temperature_2m_mean = [None]
```

Expected:

```text
DailyTemperature.mean_temperature is None
```

Adapter не преобразует missing в `0.0`.

---

## 82. HistoricalWeatherAdapter — Invalid Payload Matrix

Проверить:

```text
daily отсутствует
time отсутствует
temperature_2m_mean отсутствует
time не list
temperature_2m_mean не list
arrays разной длины
invalid date
```

Expected:

```text
WeatherDataError
```

---

## 83. HistoricalWeatherService Tests

Проверить:

```text
Location.latitude → client
Location.longitude → client
start_date → client
end_date → client
client payload → adapter
adapter result → caller
```

Service test выполняется без реального HTTP.

---

## 84. DegreeDaysCalculator — Base Matrix

Обязательные cases:

```text
Daily means:
(5.0, 8.0, 9.0)

Contributions:
0
0
0

Total:
0
```

```text
Daily means:
(10.0,)

Contribution:
0

Total:
0
```

```text
Daily means:
(11.0,)

Contribution:
1

Total:
1
```

```text
Daily means:
(12.0, 15.0)

Contributions:
2
5

Total:
7
```

```text
Daily means:
(9.0, 10.0, 12.0, 15.0)

Contributions:
0
0
2
5

Total:
7
```

```text
Daily means:
(20.0, 20.0)

Contributions:
10
10

Total:
20
```

---

## 85. DegreeDays Boundary Matrix

Обязательно проверить:

```text
9.9
→ contribution 0

10.0
→ contribution 0

10.1
→ contribution 0.1
```

Для float использовать:

```python
pytest.approx(...)
```

---

## 86. Negative Temperature Matrix

Например:

```text
-20.0
-5.0
0.0
```

Каждый день:

```text
contribution = 0
```

Итог:

```text
total = 0
```

---

## 87. Missing Temperature

Input:

```text
2026-05-01 → 12.0
2026-05-02 → None
2026-05-03 → 15.0
```

Expected:

```text
DegreeDaysResult = None
```

Не рассчитываем partial total.

---

## 88. Empty Historical Series

Input:

```python
()
```

Expected:

```text
None
```

Не возвращаем:

```text
DegreeDaysResult(total=0)
```

поскольку отсутствие данных и реальная нулевая СЭТ имеют разную семантику.

---

## 89. Chronological Validation Test

Input:

```text
2026-05-02
2026-05-01
```

Expected:

```text
ValueError
```

Calculator не сортирует данные автоматически.

---

## 90. Duplicate Date Test

Input:

```text
2026-05-01
2026-05-01
```

Expected:

```text
ValueError
```

---

## 91. Calendar Gap Test

Input:

```text
2026-05-01
2026-05-03
```

Expected:

```text
None
```

Missing calendar day трактуется как:

```text
insufficient historical data
```

---

## 92. Complete Contiguous Series

Input:

```text
2026-05-01
2026-05-02
2026-05-03
```

Expected:

```text
DegreeDaysResult
```

с:

```text
period_start = 2026-05-01
period_end   = 2026-05-03
```

---

## 93. DegreeDays Provenance Test

Проверить:

```text
base_temperature == 10.0
period_start
period_end
observations
method == DAILY_MEAN_ABOVE_BASE
total
```

---

## 94. Determinism Test

Один и тот же:

```text
DailyTemperature[]
```

при повторном вызове:

```text
DegreeDaysCalculator.calculate(...)
```

должен давать эквивалентный:

```text
DegreeDaysResult
```

---

## 95. CodlingMothRiskCalculator Boundary Matrix

Проверить:

```text
degree_days = None
→ MISSING

total = 0.0
→ NOT_MATCHED

total = 129.9
→ NOT_MATCHED

total = 130.0
→ MATCHED

total = 130.1
→ MATCHED

total = 500.0
→ MATCHED
```

---

## 96. CodlingMoth Calculator Contract Tests

Проверить:

```text
factor == DEGREE_DAYS_ABOVE_10C
required == True
actual_value == DegreeDaysResult.total
expected содержит threshold 130
expected содержит base 10 °C
explanation заполнен
```

---

## 97. Calculator не знает Historical Weather

Архитектурно проверить, что:

```text
CodlingMothRiskCalculator
```

не содержит:

```text
requests
archive-api
HistoricalWeatherClient
temperature_2m_mean
start_date
end_date
```

---

## 98. DegreeDaysCalculator не знает Codling Moth

Архитектурно проверить отсутствие:

```text
CODLING
Codling
130.0
RiskLevel
RiskResult
```

в:

```text
degree_days_calculator.py
```

`DegreeDaysCalculator` знает только:

```text
base = 10
degree-days algorithm
```

---

## 99. Historical Integration не знает Biology

В:

```text
historical_client.py
historical_adapter.py
historical_weather_service.py
```

не должно быть:

```text
CODLING
Codling
130
RiskLevel
RiskResult
```

---

## 100. End-to-End Integration

Создать:

```text
tests/integration/test_codling_moth_risk.py
```

Проверяется цепочка:

```text
DailyTemperature[]
        ↓
DegreeDaysCalculator
        ↓
DegreeDaysResult
        ↓
WeatherData
        ↓
CodlingMothRiskCalculator
        ↓
RiskEngine
```

---

## 101. Integration — HIGH

Подготовить contiguous observations, сумма которых:

```text
>= 130
```

Например, synthetic series:

```text
13 последовательных дней
mean_temperature = 20 °C
```

Каждый день:

```text
20 - 10 = 10
```

Итог:

```text
130
```

Expected:

```text
factor = MATCHED
status = CALCULATED
risk_level = HIGH
```

---

## 102. Integration — LOW

Например:

```text
10 последовательных дней
mean_temperature = 20 °C
```

Итог:

```text
100
```

Expected:

```text
factor = NOT_MATCHED
status = CALCULATED
risk_level = LOW
```

---

## 103. Integration — INSUFFICIENT_DATA

Например series содержит:

```text
mean_temperature=None
```

DegreeDaysCalculator:

```text
→ None
```

WeatherData:

```text
degree_days_10c=None
```

Calculator:

```text
→ MISSING
```

RiskEngine:

```text
status = INSUFFICIENT_DATA
risk_level = None
```

---

## 104. Real Historical Weather Smoke

После всех автоматизированных tests выполняется реальный запрос Open-Meteo.

Пример location:

```text
Москва
55.7558
37.6173
```

Для текущего assessment date:

```text
period_start =
1 января текущего года

period_end =
вчера
```

---

## 105. Что проверяется в real smoke

Не фиксируем заранее:

```text
конкретную температуру
конкретное число дней
конкретную SET
конкретный RiskLevel
```

Проверяем контракт:

```text
historical request выполняется
daily series возвращается
dates парсятся
temperature_2m_mean возвращается
series chronological
series contiguous
DegreeDaysResult создаётся
base_temperature == 10
total >= 0
period_start корректен
period_end корректен
observations сохранены
method == DAILY_MEAN_ABOVE_BASE
```

---

## 106. Почему smoke не проверяет RiskLevel

Реальная накопленная СЭТ зависит от:

```text
location
assessment date
historical weather
```

Smoke предназначен для проверки integration contract, а не фиксированного бизнес-результата.

Business thresholds уже проверяются deterministic unit/integration tests.

---

## 107. Source Traceability Review

Перед PR необходимо отдельно подтвердить три цепочки.

### Weather Source

```text
Open-Meteo Historical Weather API
        ↓
daily temperature_2m_mean
```

### Biological Source

```text
Россельхозцентр
        ↓
СЭТ выше базовой температуры 10 °C
        ↓
ориентир около 130 °C
для начала сезонного лёта
```

### Engineering Decision

```text
period start = 1 января

current day excluded

daily contribution =
max(0, daily_mean - 10)

missing day
→ insufficient data
```

Эти решения являются инженерным контрактом PestWatch и не выдаются за прямую формулировку официального источника.

---

## 108. Important Source Distinction

Не смешиваются:

```text
официально наблюдавшиеся значения
```

например:

```text
117.9 °C
104.7 °C
```

с:

```text
PestWatch program threshold
130 °C
```

`117.9` и `104.7` остаются наблюдениями конкретных сезонов.

---

## 109. Scope

В EPIC-08 входят:

```text
DailyTemperature

DegreeDaysCalculationMethod

DegreeDaysResult

WeatherData.degree_days_10c

Historical Weather configuration

HistoricalWeatherClient

HistoricalWeatherAdapter

HistoricalWeatherService

DegreeDaysCalculator

base temperature 10 °C

historical accumulation

missing-data semantics

series continuity validation

provenance

CodlingMothRiskCalculator

130 °C seasonal indicator

unit tests

integration tests

real Historical Weather smoke

source traceability review

architecture review

scope review

regression EPIC-01–07
```

---

## 110. Out of Scope

Не входят:

```text
pheromone traps

реальное наблюдение лёта

фактическая дата массового лёта

larval emergence model

106 °C after mass flight

egg-laying model

second generation

500+ °C generation stages

current-day partial SET

forecast Degree Days

future SET forecast

новый Weather Provider

Assessment

Assessment persistence

WeatherSnapshot persistence

REST API оценки

Web UI оценки

notifications

geocoding

ML

probability model

weighted scoring
```

---

## 111. Architecture Boundaries

### HistoricalWeatherClient

Знает:

```text
Open-Meteo
HTTP
request params
```

Не знает:

```text
Degree Days formula
Codling Moth
130 °C
RiskLevel
```

### HistoricalWeatherAdapter

Знает:

```text
provider JSON
DailyTemperature
```

Не знает:

```text
Degree Days formula
Codling Moth
130 °C
```

### HistoricalWeatherService

Знает:

```text
Location
Client
Adapter
date range
```

Не знает:

```text
base 10 °C
130 °C
Codling Moth
RiskLevel
```

### DegreeDaysCalculator

Знает:

```text
DailyTemperature
base 10 °C
accumulation algorithm
series validation
```

Не знает:

```text
Open-Meteo
Codling Moth
130 °C
RiskLevel
```

### CodlingMothRiskCalculator

Знает:

```text
DegreeDaysResult
threshold 130 °C
```

Не знает:

```text
Open-Meteo
HTTP
daily temperature arrays
Degree Days formula
```

### RiskEngine

Не меняется.

Не знает:

```text
Historical Weather
Degree Days
Codling Moth
130 °C
```

---

## 112. Architecture Review Commands

Перед PR проверить Historical Integration:

```powershell
Get-ChildItem .\app\integrations\weather\historical*.py |
    Select-String -Pattern "CODLING|Codling|130.0|RiskLevel|RiskResult"
```

Ожидаем пустой вывод.

Проверить HistoricalWeatherService:

```powershell
Get-Content .\app\services\historical_weather_service.py |
    Select-String -Pattern "CODLING|Codling|130.0|10.0|RiskLevel"
```

Ожидаем пустой вывод.

Проверить DegreeDaysCalculator:

```powershell
Get-Content .\app\weather\degree_days_calculator.py |
    Select-String -Pattern "CODLING|Codling|130.0|requests|Open-Meteo|RiskLevel"
```

Ожидаем пустой вывод.

Проверить CodlingMothRiskCalculator:

```powershell
Get-Content .\app\risk\calculators\codling_moth.py |
    Select-String -Pattern "requests|archive-api|HistoricalWeatherClient|temperature_2m_mean"
```

Ожидаем пустой вывод.

Проверить предметный threshold:

```powershell
Get-Content .\app\risk\calculators\codling_moth.py |
    Select-String -Pattern "130.0"
```

Ожидаем threshold только в предметном Calculator.

---

## 113. Regression Gate

Перед commit обязательно:

```powershell
python -m pytest
```

Должны пройти:

```text
EPIC-01
EPIC-02
EPIC-03
EPIC-04
EPIC-05
EPIC-06
EPIC-07
EPIC-08
```

Без:

```text
skipped regression tests
temporary xfail
commented-out failures
```

---

## 114. TASKS

### TASK-08.01

Создать:

```text
DailyTemperature
```

и unit tests.

### TASK-08.02

Создать:

```text
DegreeDaysCalculationMethod
```

и unit tests.

### TASK-08.03

Создать:

```text
DegreeDaysResult
```

и provenance tests.

### TASK-08.04

Расширить:

```text
WeatherData
```

полем:

```text
degree_days_10c
```

и проверить backward compatibility.

### TASK-08.05

Добавить:

```text
WEATHER_ARCHIVE_API_BASE_URL
```

### TASK-08.06

Реализовать:

```text
HistoricalWeatherClient
```

### TASK-08.07

Покрыть Historical Client errors.

### TASK-08.08

Реализовать:

```text
HistoricalWeatherAdapter
```

### TASK-08.09

Покрыть mapping и invalid payload.

### TASK-08.10

Реализовать:

```text
HistoricalWeatherService
```

### TASK-08.11

Реализовать:

```text
DegreeDaysCalculator
```

### TASK-08.12

Реализовать:

```text
base temperature = 10 °C
```

### TASK-08.13

Реализовать:

```text
daily contribution
```

### TASK-08.14

Реализовать:

```text
accumulation
```

### TASK-08.15

Реализовать:

```text
missing temperature semantics
```

### TASK-08.16

Реализовать:

```text
chronology validation
duplicate validation
continuity validation
```

### TASK-08.17

Реализовать provenance:

```text
period
observations
method
base
```

### TASK-08.18

Реализовать:

```text
CodlingMothRiskCalculator
```

### TASK-08.19

Реализовать threshold:

```text
130 °C
```

### TASK-08.20

Добавить Calculator boundary tests.

### TASK-08.21

Добавить:

```text
DegreeDays
→ CodlingMoth
→ RiskEngine
```

integration tests.

### TASK-08.22

Выполнить real Open-Meteo Historical Weather smoke.

### TASK-08.23

Выполнить Source Traceability Review.

### TASK-08.24

Выполнить Architecture Review.

### TASK-08.25

Выполнить Scope Review.

### TASK-08.26

Выполнить полный regression.

---

## 115. Acceptance Criteria

### Domain

```text
[ ] DailyTemperature реализован
[ ] DailyTemperature immutable
[ ] mean_temperature допускает None

[ ] DegreeDaysCalculationMethod реализован
[ ] DAILY_MEAN_ABOVE_BASE стабилен

[ ] DegreeDaysResult реализован
[ ] DegreeDaysResult immutable
[ ] provenance сохраняется

[ ] WeatherData.degree_days_10c существует
[ ] поле optional
[ ] backward compatibility сохранена
```

### Historical Weather

```text
[ ] archive endpoint configured
[ ] API key не придуман
[ ] temperature_2m_mean запрашивается
[ ] Celsius используется
[ ] timezone=auto используется

[ ] latitude передаётся
[ ] longitude передаётся
[ ] start_date передаётся
[ ] end_date передаётся

[ ] timeout обработан
[ ] connection error обработан
[ ] HTTP error обработан
[ ] invalid JSON обработан
```

### Historical Adapter

```text
[ ] daily mapping работает
[ ] даты парсятся
[ ] order сохраняется
[ ] zero сохраняется
[ ] negative сохраняется
[ ] None сохраняется

[ ] missing daily rejected
[ ] missing time rejected
[ ] missing temperature array rejected
[ ] length mismatch rejected
[ ] invalid date rejected
```

### Degree Days

```text
[ ] base temperature = 10.0
[ ] <= 10 contributes 0
[ ] > 10 contributes Tmean - 10
[ ] total accumulation работает

[ ] 9.9 boundary проверена
[ ] 10.0 boundary проверена
[ ] 10.1 boundary проверена

[ ] negative temperatures valid
[ ] zero valid

[ ] empty series → None
[ ] missing temperature → None
[ ] calendar gap → None

[ ] duplicate date → ValueError
[ ] unsorted dates → ValueError

[ ] period_start сохраняется
[ ] period_end сохраняется
[ ] observations сохраняются
[ ] method сохраняется
```

### Codling Moth

```text
[ ] CodlingMothRiskCalculator реализован

[ ] используется WeatherData.degree_days_10c

[ ] missing → MISSING

[ ] < 130 → NOT_MATCHED
[ ] 130 → MATCHED
[ ] > 130 → MATCHED

[ ] factor == DEGREE_DAYS_ABOVE_10C
[ ] factor required

[ ] actual_value == DegreeDaysResult.total
[ ] explanation заполнен
```

### Architecture

```text
[ ] Historical Client не знает Codling Moth
[ ] Historical Adapter не знает Codling Moth
[ ] Historical Service не знает threshold 130

[ ] DegreeDaysCalculator не знает Codling Moth
[ ] DegreeDaysCalculator не знает threshold 130
[ ] DegreeDaysCalculator не выполняет HTTP

[ ] CodlingMothRiskCalculator не выполняет HTTP
[ ] Calculator не знает Open-Meteo
[ ] Calculator не рассчитывает Degree Days

[ ] RiskEngine не изменён
```

### Integration

```text
[ ] SET >= 130 → HIGH
[ ] SET < 130 → LOW
[ ] insufficient data → INSUFFICIENT_DATA

[ ] real Historical Weather smoke пройден
[ ] Source Traceability Review пройден
[ ] EPIC-01–07 regression проходит
```

---

## 116. PR Checklist

### Domain

```text
[ ] DailyTemperature
[ ] DegreeDaysCalculationMethod
[ ] DegreeDaysResult
[ ] WeatherData extension
[ ] immutability
[ ] backward compatibility
```

### Historical Integration

```text
[ ] configuration
[ ] HistoricalWeatherClient
[ ] request contract
[ ] timeout
[ ] connection error
[ ] HTTP error
[ ] invalid JSON
[ ] HistoricalWeatherAdapter
[ ] payload validation
[ ] HistoricalWeatherService
```

### Degree Days

```text
[ ] base 10 °C
[ ] contribution formula
[ ] accumulation
[ ] empty series
[ ] missing temperature
[ ] zero
[ ] negative
[ ] chronology
[ ] duplicates
[ ] continuity
[ ] provenance
[ ] determinism
```

### Codling Moth

```text
[ ] Calculator
[ ] threshold 130
[ ] 129.9
[ ] 130.0
[ ] 130.1
[ ] missing
[ ] explanation
[ ] required factor
```

### Integration

```text
[ ] DegreeDays → Calculator
[ ] Calculator → RiskEngine
[ ] HIGH
[ ] LOW
[ ] INSUFFICIENT_DATA
[ ] real historical smoke
```

### Review

```text
[ ] Source Traceability Review
[ ] Architecture Review
[ ] Scope Review
[ ] full regression
```

---

## 117. Definition of Done

EPIC-08 считается завершённым:

```text
Historical Weather Contract
        +
DailyTemperature
        +
DegreeDaysCalculationMethod
        +
DegreeDaysResult
        +
Provenance
        +
HistoricalWeatherClient
        +
HistoricalWeatherAdapter
        +
HistoricalWeatherService
        +
DegreeDaysCalculator
        +
Base Temperature 10 °C
        +
Historical Accumulation
        +
Missing / Continuity Semantics
        +
CodlingMothRiskCalculator
        +
Seasonal Indicator 130 °C
        +
Boundary Tests
        +
Calculator → RiskEngine Integration
        +
Real Open-Meteo Historical Smoke
        +
Source Traceability Review
        +
Architecture Review
        +
Scope Review
        +
EPIC-01–07 Regression
        ↓
READY FOR PR
```

---

## 118. Что получится после EPIC-08

Все четыре объекта MVP будут иметь работающую предметную модель:

```text
Иксодовые клещи
→ текущая температура воздуха
→ TickRiskCalculator
✓

Капустная тля
→ температура + влажность
→ CabbageAphidRiskCalculator
✓

Колорадский жук
→ T6/T18
→ estimated T10
→ ColoradoBeetleRiskCalculator
✓

Яблонная плодожорка
→ Historical Weather
→ Degree Days
→ CodlingMothRiskCalculator
✓
```

---

## 119. Что идёт после EPIC-08

EPIC-08 завершает отдельные расчётные модели угроз.

До начала следующего крупного функционального этапа выполняется:

```text
Documentation Alignment
```

Необходимо привести фактическую архитектуру в соответствие с исходным системным документом:

```text
Domain Model
WeatherData
Derived Weather Indicators
Historical Weather
Risk Calculators
Data Flow
```

После Documentation Alignment следующий крупный этап:

```text
Assessment
```

где будет собрана пользовательская цепочка:

```text
Location
+
UserProfile
        ↓
Current Weather
+
Historical Weather
        ↓
Threat Calculators
        ↓
RiskResult[]
        ↓
Assessment
        ↓
Persistence
```

---

## 120. Финальное правило EPIC-08

PestWatch не утверждает:

```text
При 130 °C СЭТ
яблонная плодожорка обязательно появилась.
```

PestWatch утверждает:

```text
Накопленная сумма эффективных температур
достигла сезонного ориентира,
связанного с началом лёта
яблонной плодожорки.
```

И не утверждает:

```text
117.9 °C является универсальным порогом.
```

Значения вроде:

```text
117.9
104.7
```

рассматриваются как фактические наблюдения отдельных сезонов.

Программный сезонный ориентир PestWatch:

```text
base temperature = 10 °C
SET threshold     = 130 °C
```

при этом он остаётся:

```text
объяснимым
трассируемым
воспроизводимым
и не выдаётся за точный прогноз появления вредителя
```.
