# EPIC-06 — Threat Risk Calculators

## 1. Цель EPIC

Реализовать первые конкретные калькуляторы сезонного риска PestWatch на основании исследовательских материалов проекта и официальных источников.

EPIC-06 впервые соединяет:

```text
WeatherData
        ↓
Threat-specific Calculator
        ↓
RiskFactorResult[]
        ↓
RiskEngine
        ↓
RiskResult
```

Каждый калькулятор отвечает только за правила конкретной угрозы.

Общая агрегация:

```text
RiskStatus
RiskLevel
RiskResult
```

остаётся ответственностью уже реализованного `RiskEngine`.

---

# 2. Принцип достоверности

Каждое программное правило должно иметь трассируемую цепочку:

```text
официальный источник
        ↓
исследовательский вывод
        ↓
формализованный фактор
        ↓
unit test
        ↓
RiskFactorResult
```

Нельзя добавлять порог только потому, что он выглядит биологически правдоподобным.

Нельзя подменять:

```text
наблюдение
```

на:

```text
универсальную закономерность
```

без основания в источнике.

PestWatch оценивает соответствие условиям активности, а не вероятность фактического появления вредителя.

---

# 3. Git

Базовая ветка:

```text
main
```

Рабочая ветка:

```text
feature/epic-06-threat-risk-calculators
```

Pull Request:

```text
EPIC-06: Threat Risk Calculators
```

---

# 4. Calculators in Scope

В EPIC-06 входят:

```text
TickRiskCalculator
CabbageAphidRiskCalculator
```

Не входят:

```text
ColoradoBeetleRiskCalculator
CodlingMothRiskCalculator
```

Их исключение является осознанным архитектурным решением, а не незавершённой реализацией.

---

# 5. Почему только два Calculator

## TickRiskCalculator

Для иксодовых клещей официальный источник непосредственно связывает активность с температурой воздуха.

Подтверждено:

```text
+1…+4 °C
→ активизация после схода снежного покрова

около +10 °C
→ выраженная активность / клещи активны
```

Для программного правила EPIC-06 используется:

```text
temperature >= 10 °C
→ MATCHED
```

Порог `+1…+4 °C` не превращается во второй самостоятельный фактор, потому что в источнике он связан также со сходом снежного покрова, а данных о снежном покрове PestWatch сейчас не получает.

---

## CabbageAphidRiskCalculator

Для капустной тли официальный материал непосредственно задаёт оптимальные условия:

```text
temperature = 25–26 °C
humidity    = 60–70 %
```

Оба показателя уже присутствуют в `WeatherData`.

Следовательно, правило может быть реализовано без дополнительных предположений.

---

# 6. ColoradoBeetle — Deferred

Исследование проекта фиксирует:

```text
почва около +13 °C
→ выход колорадского жука на поверхность
```

и материалы Центральной России также указывают:

```text
+13…+15 °C
```

Однако текущая интеграция PestWatch предоставляет:

```text
soil_temperature_0cm
```

то есть температуру поверхности почвы.

В официальных материалах встречается температурная характеристика почвы на другой глубине, включая 10 см.

Следовательно:

```text
source soil temperature
≠ автоматически
Open-Meteo soil_temperature_0cm
```

EPIC-06 не должен скрывать это различие.

`ColoradoBeetleRiskCalculator` будет реализован после отдельного решения о корректной глубине измерения и, при необходимости, расширения Weather Integration.

---

# 7. CodlingMoth — Deferred

Для яблонной плодожорки исследование подтверждает использование:

```text
СЭТ — сумма эффективных температур
```

с базовым порогом:

```text
10 °C
```

В наблюдении Тамбовской области:

```text
массовый лёт
→ СЭТ около 117.9 °C
```

Но текущий:

```text
WeatherData
```

содержит только погодный snapshot.

Для расчёта СЭТ нужен временной ряд.

Поэтому:

```text
CodlingMothRiskCalculator
```

не реализуется до появления:

```text
historical/daily temperatures
        ↓
DegreeDaysCalculator
        ↓
accumulated degree days
```

Также значение `117.9 °C` не объявляется универсальным порогом для всей Центральной России без дополнительного обоснования.

---

# 8. Out of Scope

В EPIC-06 не входят:

```text
ColoradoBeetleRiskCalculator
CodlingMothRiskCalculator
DegreeDaysCalculator
historical weather
новые Weather API fields
новая Weather integration
геокодирование
RiskPolicy changes
RiskEngine changes
Assessment
Assessment persistence
REST API оценки
Web UI оценки
notifications
ML / probability model
weighted scoring
```

---

# 9. Архитектура

После EPIC-06:

```text
                  WeatherData
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
 TickRiskCalculator       CabbageAphidRiskCalculator
          │                         │
          ▼                         ▼
 RiskFactorResult[]        RiskFactorResult[]
          │                         │
          └────────────┬────────────┘
                       ▼
                  RiskEngine
                       ↓
                  RiskResult
```

---

# 10. Расположение

Создаём:

```text
app/risk/calculators/
├── __init__.py
├── tick.py
└── cabbage_aphid.py
```

Тесты:

```text
tests/unit/risk/calculators/
├── __init__.py
├── test_tick.py
└── test_cabbage_aphid.py
```

---

# 11. Общий Calculator Contract

Используется уже существующий:

```python
RiskCalculator.evaluate(
    weather: WeatherData,
) -> tuple[RiskFactorResult, ...]
```

EPIC-06 не изменяет этот контракт.

Calculator:

```text
получает WeatherData
        ↓
проверяет свои факторы
        ↓
возвращает RiskFactorResult[]
```

Calculator не вызывает `RiskEngine`.

---

# 12. TickRiskCalculator

Threat code:

```text
TICK
```

В EPIC-06 используется один формализованный фактор:

```text
AIR_TEMPERATURE
```

Источник подтверждает выраженную активность клещей примерно при:

```text
+10 °C
```

Правило:

```text
temperature is None
→ MISSING

temperature < 10.0
→ NOT_MATCHED

temperature >= 10.0
→ MATCHED
```

Фактор:

```text
required=True
```

---

# 13. Tick factor result

При `temperature=12.0`:

```text
factor:
AIR_TEMPERATURE

state:
MATCHED

actual_value:
12.0

expected:
>= 10 °C

required:
True
```

Объяснение:

```text
Температура воздуха соответствует условиям выраженной активности иксодовых клещей.
```

---

# 14. Tick below threshold

При:

```text
temperature=9.9
```

результат:

```text
NOT_MATCHED
```

Объяснение не должно утверждать:

```text
клещей нет
```

Корректная семантика:

```text
Температура воздуха не соответствует выбранному условию выраженной активности иксодовых клещей.
```

---

# 15. Почему +1…+4 °C не отдельный scoring factor

Исследование связывает этот диапазон с:

```text
сход снега
+
среднесуточная температура
```

PestWatch сейчас не получает:

```text
snow cover
```

Кроме того, создание двух факторов:

```text
TEMPERATURE_ONSET
TEMPERATURE_ACTIVE
```

из одного и того же измерения искусственно удвоило бы вес температуры в ratio-модели EPIC-05.

Поэтому в EPIC-06 используется один температурный критерий:

```text
>= 10 °C
```

---

# 16. Tick season factor

В EPIC-06 отдельный:

```text
SEASON
```

не добавляется.

Причина:

исследование подтверждает сезонность, но не задаёт полный универсальный календарный диапазон:

```text
month >= X
and
month <= Y
```

достаточный для всей территории MVP.

Кроме того, официальные материалы показывают повторный пик в конце августа — начале сентября и возможность сохранения активности до ноября при тёплой погоде.

Поэтому фиксированный календарный диапазон без дополнительной формализации сейчас не вводится.

---

# 17. Tick region factor

Отдельный:

```text
REGION
```

в Calculator также не добавляется.

Исследование показывает значимость территории, но не содержит правил вида:

```text
region A → MATCHED
region B → NOT_MATCHED
```

Следовательно, такая таблица была бы выдуманной инженерной логикой.

Географическая применимость пока обеспечивается общим scope проекта:

```text
Центральная Россия
```

---

# 18. CabbageAphidRiskCalculator

Threat code:

```text
CABBAGE_APHID
```

Факторы:

```text
AIR_TEMPERATURE
RELATIVE_HUMIDITY
```

Оба:

```text
required=True
```

---

# 19. Cabbage aphid temperature rule

Официально зафиксированный оптимальный диапазон:

```text
25–26 °C
```

Правило:

```text
temperature is None
→ MISSING

25.0 <= temperature <= 26.0
→ MATCHED

temperature < 25.0
or
temperature > 26.0
→ NOT_MATCHED
```

Фактор:

```text
AIR_TEMPERATURE
```

Expected:

```text
25–26 °C
```

---

# 20. Cabbage aphid humidity rule

Официально зафиксированный диапазон:

```text
60–70 %
```

Правило:

```text
humidity is None
→ MISSING

60.0 <= humidity <= 70.0
→ MATCHED

humidity < 60.0
or
humidity > 70.0
→ NOT_MATCHED
```

Фактор:

```text
RELATIVE_HUMIDITY
```

Expected:

```text
60–70 %
```

---

# 21. Inclusive boundaries

Границы являются inclusive.

То есть:

```text
25.0 °C → MATCHED
26.0 °C → MATCHED

60.0 % → MATCHED
70.0 % → MATCHED
```

А:

```text
24.9 °C → NOT_MATCHED
26.1 °C → NOT_MATCHED

59.9 % → NOT_MATCHED
70.1 % → NOT_MATCHED
```

---

# 22. Missing values

Calculator не подставляет значения по умолчанию.

Например:

```text
temperature=None
humidity=65
```

даёт:

```text
AIR_TEMPERATURE
→ MISSING

RELATIVE_HUMIDITY
→ MATCHED
```

Так как оба фактора:

```text
required=True
```

последующий `RiskEngine` определит:

```text
INSUFFICIENT_DATA
risk_level=None
```

Calculator не принимает это решение самостоятельно.

---

# 23. Zero values

Сохраняется принцип:

```text
None != 0
```

Например:

```text
humidity=0.0
```

→

```text
NOT_MATCHED
```

но не:

```text
MISSING
```

То же относится к температуре:

```text
temperature=0.0
→ NOT_MATCHED
```

---

# 24. Determinism

При одинаковом `WeatherData` Calculator всегда обязан возвращать одинаковый результат.

Не допускаются:

```text
random
current system time
HTTP
database
external source lookup
```

внутри Calculator.

Дата используется только если она явно находится во входной domain-модели и предусмотрена правилом.

В EPIC-06 дата в concrete calculators не используется.

---

# 25. Side Effects

Calculators являются чистыми вычислительными компонентами.

Они не должны:

```text
изменять WeatherData
сохранять данные
писать в SQLite
вызывать HTTP
читать Flask config
обращаться к Repository
```

---

# 26. RiskLevel consequence

EPIC-06 не изменяет ratio aggregation EPIC-05.

Это означает важное следствие.

## Tick

У одного известного фактора возможны:

```text
MATCHED
→ 1 / 1
→ HIGH

NOT_MATCHED
→ 0 / 1
→ LOW
```

То есть текущая модель Tick Calculator производит:

```text
LOW / HIGH
```

но не обязана искусственно генерировать:

```text
MODERATE / ELEVATED
```

---

# 27. Cabbage aphid RiskLevel consequence

Два фактора дают:

```text
0 / 2
→ LOW

1 / 2
→ ELEVATED

2 / 2
→ HIGH
```

Уровень:

```text
MODERATE
```

для этого Calculator при двух бинарных факторах естественным образом не возникает.

Это допустимо.

Не существует требования, что каждый Threat обязательно должен использовать все четыре `RiskLevel`.

---

# 28. Нельзя искусственно создавать факторы ради шкалы

Запрещено добавлять, например:

```text
TEMPERATURE_LOW_BOUND
TEMPERATURE_HIGH_BOUND
HUMIDITY_LOW_BOUND
HUMIDITY_HIGH_BOUND
```

как четыре разных фактора только для получения дополнительных уровней `RiskLevel`.

Один биологический показатель должен оставаться одним фактором.

---

# 29. Explanation contract

Каждый `RiskFactorResult` должен быть объясним пользователю.

Для MATCHED:

```text
<показатель> соответствует условиям активности.
```

Для NOT_MATCHED:

```text
<показатель> не соответствует выбранным условиям активности.
```

Для MISSING:

```text
Данные о <показателе> отсутствуют.
```

Объяснение не должно утверждать фактическое наличие или отсутствие вредителя.

---

# 30. Source traceability

Каждое правило должно быть связано с существующим Threat Catalog source.

На уровне Calculator в EPIC-06 URL не дублируется.

Архитектура:

```text
Threat Catalog
→ Source

Calculator
→ rule implementation
```

Связь проверяется документацией и тестами.

Не создаём:

```text
URL constants
```

внутри Calculator.

---

# 31. Источниковая база — TICK

Основной источник:

```text
Управление Роспотребнадзора
по Ивановской области
```

Подтверждённое правило:

```text
клещи активны около +10 °C
```

Исследование также фиксирует начало активизации после схода снега при среднесуточной температуре около `+1…+4 °C`.

В EPIC-06 программно используется только:

```text
>= 10 °C
```

---

# 32. Источниковая база — CABBAGE_APHID

Основной источник:

```text
ФГБУ «Россельхозцентр»
Орловская область
```

Подтверждённые оптимальные условия:

```text
25–26 °C
60–70 %
```

Именно эти значения используются Calculator без расширения диапазонов.

---

# 33. Источниковая база — COLORADO_BEETLE

Исследование сохраняется как основание будущего правила:

```text
почва около +13 °C
```

и:

```text
+13…+15 °C
```

Но Calculator не реализуется до фиксации semantics температуры почвы.

Нужно отдельно решить:

```text
какая глубина
```

и какой Weather API parameter ей соответствует.

---

# 34. Источниковая база — CODLING_MOTH

Исследование фиксирует:

```text
СЭТ
base temperature = 10 °C
```

и региональное наблюдение:

```text
117.9 °C СЭТ
на момент массового лёта
```

Эти данные сохраняются для будущего Degree Days EPIC.

EPIC-06 не трактует `117.9` как универсальный threshold.

---

# 35. Unit Test Matrix — Tick

Обязательные test cases:

| temperature | Expected state |
|---:|---|
| `None` | `MISSING` |
| `0.0` | `NOT_MATCHED` |
| `9.9` | `NOT_MATCHED` |
| `10.0` | `MATCHED` |
| `10.1` | `MATCHED` |
| `25.0` | `MATCHED` |

Дополнительно проверить:

```text
factor == AIR_TEMPERATURE
required == True
actual_value сохраняется
expected содержит >= 10 °C
explanation заполнен
```

---

# 36. Unit Test Matrix — Cabbage Aphid Temperature

| temperature | Expected state |
|---:|---|
| `None` | `MISSING` |
| `0.0` | `NOT_MATCHED` |
| `24.9` | `NOT_MATCHED` |
| `25.0` | `MATCHED` |
| `25.5` | `MATCHED` |
| `26.0` | `MATCHED` |
| `26.1` | `NOT_MATCHED` |

---

# 37. Unit Test Matrix — Cabbage Aphid Humidity

| humidity | Expected state |
|---:|---|
| `None` | `MISSING` |
| `0.0` | `NOT_MATCHED` |
| `59.9` | `NOT_MATCHED` |
| `60.0` | `MATCHED` |
| `65.0` | `MATCHED` |
| `70.0` | `MATCHED` |
| `70.1` | `NOT_MATCHED` |
| `100.0` | `NOT_MATCHED` |

---

# 38. Calculator Output Order

Для `CabbageAphidRiskCalculator` порядок факторов фиксирован:

```text
1. AIR_TEMPERATURE
2. RELATIVE_HUMIDITY
```

Это обеспечивает воспроизводимость вывода и тестов.

---

# 39. Integration with RiskEngine tests

Отдельно проверить:

```text
TickRiskCalculator
        ↓
RiskEngine
```

и:

```text
CabbageAphidRiskCalculator
        ↓
RiskEngine
```

Без HTTP, Flask и SQLite.

---

# 40. Tick end-to-end matrix

```text
temperature = 12
```

→

```text
AIR_TEMPERATURE MATCHED
```

→

```text
CALCULATED
HIGH
```

---

```text
temperature = 5
```

→

```text
AIR_TEMPERATURE NOT_MATCHED
```

→

```text
CALCULATED
LOW
```

---

```text
temperature = None
```

→

```text
AIR_TEMPERATURE MISSING
```

→

```text
INSUFFICIENT_DATA
risk_level=None
```

---

# 41. Cabbage aphid end-to-end matrix

```text
temperature=25.5
humidity=65
```

→

```text
MATCHED
MATCHED
```

→

```text
CALCULATED
HIGH
```

---

```text
temperature=25.5
humidity=50
```

→

```text
MATCHED
NOT_MATCHED
```

→

```text
CALCULATED
ELEVATED
```

---

```text
temperature=20
humidity=50
```

→

```text
NOT_MATCHED
NOT_MATCHED
```

→

```text
CALCULATED
LOW
```

---

```text
temperature=None
humidity=65
```

→

```text
MISSING
MATCHED
```

→

```text
INSUFFICIENT_DATA
risk_level=None
```

---

# 42. Test Isolation

Все Calculator tests:

```text
не используют интернет
не запускают Flask
не создают SQLite
не используют текущую погоду
```

В тестах создаётся `WeatherData` вручную.

---

# 43. TASKS

## TASK-06.01

Создать package:

```text
app/risk/calculators/
```

## TASK-06.02

Реализовать:

```text
TickRiskCalculator
```

## TASK-06.03

Покрыть Tick boundary tests.

## TASK-06.04

Реализовать:

```text
CabbageAphidRiskCalculator
```

## TASK-06.05

Покрыть temperature boundaries.

## TASK-06.06

Покрыть humidity boundaries.

## TASK-06.07

Проверить missing values.

## TASK-06.08

Проверить zero values.

## TASK-06.09

Проверить `required=True`.

## TASK-06.10

Проверить стабильный порядок factors.

## TASK-06.11

Добавить Calculator → RiskEngine integration tests.

## TASK-06.12

Выполнить regression EPIC-01–05.

## TASK-06.13

Провести source traceability review.

## TASK-06.14

Провести Architecture Review.

---

# 44. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-06-01 | `TickRiskCalculator` реализован |
| AC-06-02 | TICK использует `WeatherData.temperature` |
| AC-06-03 | `temperature >= 10 °C` → MATCHED |
| AC-06-04 | `temperature < 10 °C` → NOT_MATCHED |
| AC-06-05 | missing temperature → MISSING |
| AC-06-06 | TICK temperature required |
| AC-06-07 | `CabbageAphidRiskCalculator` реализован |
| AC-06-08 | CABBAGE_APHID использует temperature |
| AC-06-09 | `25–26 °C` inclusive → MATCHED |
| AC-06-10 | CABBAGE_APHID использует humidity |
| AC-06-11 | `60–70 %` inclusive → MATCHED |
| AC-06-12 | missing temperature → MISSING |
| AC-06-13 | missing humidity → MISSING |
| AC-06-14 | оба фактора required |
| AC-06-15 | zero не считается missing |
| AC-06-16 | Calculator возвращает tuple |
| AC-06-17 | Calculator не определяет RiskLevel |
| AC-06-18 | Calculator не создаёт RiskResult |
| AC-06-19 | Calculator не выполняет HTTP |
| AC-06-20 | Calculator не использует SQLAlchemy |
| AC-06-21 | Calculator не зависит от Flask |
| AC-06-22 | Calculator не содержит URL источника |
| AC-06-23 | Tick → RiskEngine flow протестирован |
| AC-06-24 | Cabbage Aphid → RiskEngine flow протестирован |
| AC-06-25 | Colorado calculator не реализован с некорректной soil semantics |
| AC-06-26 | Codling Moth calculator не реализован без Degree Days |
| AC-06-27 | реальные пороги трассируются до источников |
| AC-06-28 | regression EPIC-01–05 проходит |

---

# 45. Architecture Review

Перед PR проверить:

```text
app/risk/calculators
```

не импортирует:

```text
flask
sqlalchemy
requests
WeatherClient
WeatherService
Repository
ThreatModel
db
```

Также проверить отсутствие:

```text
HTTP
SQLite
current datetime
random
```

---

# 46. Source Review

Перед PR отдельно подтверждаем:

```text
TICK >= 10 °C
```

→ Роспотребнадзор.

```text
CABBAGE_APHID 25–26 °C
```

→ Россельхозцентр.

```text
CABBAGE_APHID 60–70 %
```

→ Россельхозцентр.

Если код содержит любое другое числовое предметное значение, оно должно быть объяснено отдельно.

---

# 47. PR Checklist

## Tick

```text
[ ] calculator
[ ] >=10 boundary
[ ] below boundary
[ ] missing
[ ] zero
[ ] explanation
[ ] required
```

## Cabbage Aphid

```text
[ ] calculator
[ ] temperature lower boundary
[ ] temperature upper boundary
[ ] humidity lower boundary
[ ] humidity upper boundary
[ ] values outside ranges
[ ] missing temperature
[ ] missing humidity
[ ] zero
[ ] explanation
[ ] required
[ ] stable factor order
```

## Integration

```text
[ ] Tick → RiskEngine
[ ] Cabbage Aphid → RiskEngine
[ ] full regression
```

## Scope

```text
[ ] no Colorado implementation
[ ] no Codling Moth implementation
[ ] no Degree Days
[ ] no Weather changes
[ ] no API
[ ] no UI
```

---

# 48. Definition of Done

EPIC-06 считается завершённым:

```text
Official research rules
        +
TickRiskCalculator
        +
CabbageAphidRiskCalculator
        +
Boundary Tests
        +
Missing Data Tests
        +
Zero Value Tests
        +
Calculator → RiskEngine Tests
        +
Source Traceability Review
        +
EPIC-01–05 Regression
        +
Architecture Review
        ↓
READY FOR PR
```

---

# 49. Следующие необходимые EPIC

После EPIC-06 остаются две отдельные предметные задачи.

```text
Colorado Beetle
        ↓
soil-temperature semantics
        ↓
Weather Integration extension if required
        ↓
ColoradoBeetleRiskCalculator
```

и:

```text
Codling Moth
        ↓
Historical Weather
        ↓
DegreeDaysCalculator
        ↓
CodlingMothRiskCalculator
```

Они не должны быть искусственно втиснуты в EPIC-06.

---

# 50. Главное правило EPIC-06

Если между:

```text
официальным источником
```

и:

```text
if в Python
```

невозможно показать прозрачную связь,

такой `if` в EPIC-06 не добавляется.
