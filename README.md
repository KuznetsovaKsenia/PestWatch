# EPIC-07 — Colorado Beetle Soil Temperature Support

## 1. Цель EPIC

Добавить в PestWatch корректную поддержку оценки сезонного риска активности колорадского жука.

Для этого необходимо:

```text
получить температуру почвы на 6 см
        +
получить температуру почвы на 18 см
        ↓
оценить температуру почвы на глубине 10 см
        ↓
применить подтверждённое правило колорадского жука
        ↓
RiskFactorResult
        ↓
RiskEngine
        ↓
RiskResult
```

EPIC-07 впервые добавляет в PestWatch производный погодный показатель.

---

# 2. Основание

Исследование проекта устанавливает связь активности колорадского жука с температурой почвы.

В материалах Россельхозцентра зафиксировано, что выход жуков связан с прогреванием почвы примерно до:

```text
+13 °C
```

Исследовательский документ PestWatch также фиксирует диапазон:

```text
+13…+15 °C
```

и делает вывод, что температура почвы является подходящим сезонным триггером для оценки риска колорадского жука.

Для EPIC-07 используется минимальная граница:

```text
>= 13 °C
```

как условие, соответствующее периоду интенсивного выхода.

---

# 3. Важное ограничение источника данных

Предметное правило относится к температуре почвы примерно на глубине:

```text
10 см
```

Текущий Open-Meteo Forecast API предоставляет точечные значения:

```text
soil_temperature_0cm
soil_temperature_6cm
soil_temperature_18cm
soil_temperature_54cm
```

Он не предоставляет:

```text
soil_temperature_10cm
```

Поэтому нельзя без дополнительного преобразования использовать:

```text
soil_temperature_6cm
```

как температуру на 10 см.

Также нельзя использовать:

```text
soil_temperature_0_to_10cm
```

из model-specific API как эквивалент температуры на глубине 10 см, поскольку это среднее значение слоя, а не значение на конкретной глубине.

---

# 4. Архитектурное решение

PestWatch оценивает температуру на глубине 10 см методом линейной интерполяции между модельными значениями Open-Meteo на глубинах:

```text
6 см
18 см
```

Цепочка:

```text
Open-Meteo
    ↓
T6 + T18
    ↓
WeatherAdapter
    ↓
WeatherData
    ↓
SoilTemperatureEstimator
    ↓
SoilTemperatureEstimate(depth=10)
    ↓
ColoradoBeetleRiskCalculator
    ↓
RiskFactorResult
```

---

# 5. Семантика результата

Результат интерполяции НЕ является:

```text
измеренной температурой почвы на глубине 10 см
```

Он является:

```text
расчётной оценкой температуры почвы
на глубине 10 см
```

Это различие должно сохраняться в domain-модели.

---

# 6. Пользовательская семантика

Во внутреннем коде используется точное техническое понятие:

```text
estimated soil temperature at 10 cm
```

Пользователю не показывается тяжёлая техническая формулировка как основной текст.

Основное объяснение:

```text
Температура почвы на глубине около 10 см — 14,2 °C.
```

Дополнительное объяснение:

```text
Значение рассчитано по данным погодной модели
для глубин 6 и 18 см.
```

При необходимости в UI позднее может появиться:

```text
Как рассчитано?
```

с подробным описанием метода.

---

# 7. Scope

В EPIC-07 входят:

```text
Open-Meteo soil_temperature_6cm
Open-Meteo soil_temperature_18cm

расширение WeatherData

SoilTemperatureEstimateMethod

SoilTemperatureEstimate

SoilTemperatureEstimator

линейная интерполяция на 10 см

provenance расчётного значения

ColoradoBeetleRiskCalculator

unit tests

Weather integration tests

Calculator → RiskEngine integration tests

real Open-Meteo smoke test

source traceability review

architecture review

regression EPIC-01–06
```

---

# 8. Out of Scope

В EPIC-07 сознательно не входят:

```text
CodlingMothRiskCalculator
Historical Weather
Degree Days
СЭТ

новый Weather Provider
GFS-specific integration

soil moisture
soil type
snow cover

Assessment
Assessment persistence

REST API оценки
Web UI оценки
notifications
geocoding

ML
probability model
weighted scoring
```

---

# 9. Git

Базовая ветка:

```text
main
```

Рабочая ветка:

```text
feature/epic-07-colorado-beetle-soil-temperature
```

Pull Request:

```text
EPIC-07: Colorado Beetle Soil Temperature Support
```

---

# 10. Изменение WeatherData

Текущий `WeatherData` уже содержит:

```text
soil_temperature
```

В EPIC-04 это поле было связано с:

```text
soil_temperature_0cm
```

то есть температурой поверхности почвы.

Его семантику не меняем.

Добавляются отдельные поля:

```python
soil_temperature_6cm: float | None = None
soil_temperature_18cm: float | None = None
soil_temperature_10cm_estimate: SoilTemperatureEstimate | None = None
```

Таким образом:

```text
soil_temperature
→ поверхность, 0 см

soil_temperature_6cm
→ значение Open-Meteo на 6 см

soil_temperature_18cm
→ значение Open-Meteo на 18 см

soil_temperature_10cm_estimate
→ производная оценка PestWatch
```

---

# 11. Почему не переименовываем soil_temperature

Существующее:

```text
soil_temperature
```

уже является частью контракта EPIC-02/04.

Его переименование сейчас:

```text
soil_temperature
→ soil_temperature_0cm
```

создало бы ненужное breaking change.

Поэтому в EPIC-07:

```text
существующая семантика сохраняется
```

а новые показатели добавляются явно.

---

# 12. Backward Compatibility WeatherData

Новые поля должны иметь:

```text
default=None
```

Существующий код:

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

должен продолжить работать без изменений.

---

# 13. SoilTemperatureEstimateMethod

Создаётся enum:

```python
class SoilTemperatureEstimateMethod(Enum):
    LINEAR_INTERPOLATION = "LINEAR_INTERPOLATION"
```

Расположение:

```text
app/domain/soil_temperature_estimate_method.py
```

Не используется произвольная строка:

```text
"linear"
"interpolation"
"linear_interpolation"
```

---

# 14. SoilTemperatureEstimate

Создаётся immutable domain-модель:

```python
@dataclass(frozen=True)
class SoilTemperatureEstimate:
    depth_cm: float
    temperature: float

    source_depths_cm: tuple[float, float]
    source_temperatures: tuple[float, float]

    method: SoilTemperatureEstimateMethod
```

Расположение:

```text
app/domain/soil_temperature_estimate.py
```

---

# 15. Пример SoilTemperatureEstimate

Например:

```text
T6  = 16.0 °C
T18 = 10.0 °C
```

после расчёта:

```python
SoilTemperatureEstimate(
    depth_cm=10.0,
    temperature=14.0,
    source_depths_cm=(6.0, 18.0),
    source_temperatures=(16.0, 10.0),
    method=SoilTemperatureEstimateMethod.LINEAR_INTERPOLATION,
)
```

---

# 16. Почему provenance хранится отдельно

В `RiskFactorResult` не добавляются:

```text
source_depths
source_temperatures
calculation_method
estimated
```

`RiskFactorResult` остаётся generic-моделью Risk Engine.

Специфика производного погодного показателя хранится в:

```text
SoilTemperatureEstimate
```

---

# 17. Формула интерполяции

Для известных точек:

```text
depth1 = 6
depth2 = 18
target = 10
```

используется:

```text
Ttarget =
T1 +
(T2 - T1)
×
(target - depth1) / (depth2 - depth1)
```

Для нашего случая:

```text
T10 =
T6 +
(T18 - T6)
×
(10 - 6) / (18 - 6)
```

то есть:

```text
T10 =
T6 +
(T18 - T6) × 1/3
```

---

# 18. Почему не используется среднее арифметическое

Формула:

```text
(T6 + T18) / 2
```

оценивает значение в середине интервала:

```text
12 см
```

поскольку:

```text
(6 + 18) / 2 = 12
```

Нам требуется значение:

```text
10 см
```

поэтому используется именно интерполяция по расстоянию.

---

# 19. SoilTemperatureEstimator

Создаётся отдельный вычислительный компонент:

```text
SoilTemperatureEstimator
```

Расположение:

```text
app/weather/soil_temperature_estimator.py
```

либо в существующей структуре integrations/domain-services — окончательное расположение должно соблюдать правило:

```text
это не HTTP integration
и не Risk Calculator
```

Предпочтительное расположение:

```text
app/weather/
```

---

# 20. Ответственность SoilTemperatureEstimator

Estimator:

```text
получает T6 и T18
        ↓
проверяет наличие обоих значений
        ↓
выполняет интерполяцию
        ↓
создаёт SoilTemperatureEstimate
```

Estimator не:

```text
выполняет HTTP
знает Open-Meteo JSON
знает колорадского жука
определяет RiskLevel
обращается в БД
```

---

# 21. Интерфейс Estimator

Предлагаемый контракт:

```python
class SoilTemperatureEstimator:
    def estimate_at_10cm(
        self,
        temperature_6cm: float | None,
        temperature_18cm: float | None,
    ) -> SoilTemperatureEstimate | None:
        ...
```

---

# 22. Missing semantics Estimator

Если:

```text
T6 is None
```

или:

```text
T18 is None
```

Estimator возвращает:

```text
None
```

Не допускается:

```text
экстраполяция из одного значения
```

или:

```text
подстановка второго значения
```

---

# 23. Zero semantics

Ноль является известной температурой.

Например:

```text
T6 = 0.0
T18 = 6.0
```

является валидным входом.

`0.0` не трактуется как:

```text
missing
```

---

# 24. Отрицательные температуры

Отрицательные значения являются валидными.

Например:

```text
T6  = -4
T18 = 2
```

должны интерполироваться обычным способом.

Estimator не выполняет биологическую интерпретацию значения.

---

# 25. Precision

Внутренний расчёт выполняется без искусственного округления до целых значений.

Например:

```text
13.266666...
```

может сохраняться как float.

Округление для UI:

```text
13.3 °C
```

не относится к EPIC-07 Calculator/Domain layer.

---

# 26. WeatherClient

В запрос Open-Meteo добавляются:

```text
soil_temperature_6cm
soil_temperature_18cm
```

Сохраняется существующий:

```text
soil_temperature_0cm
```

Итоговый current contract:

```text
temperature_2m
relative_humidity_2m
precipitation
wind_speed_10m
soil_temperature_0cm
soil_temperature_6cm
soil_temperature_18cm
```

---

# 27. WeatherAdapter

WeatherAdapter только преобразует:

```text
Open-Meteo JSON
```

в:

```text
WeatherData
```

Mapping:

```text
soil_temperature_0cm
→ soil_temperature

soil_temperature_6cm
→ soil_temperature_6cm

soil_temperature_18cm
→ soil_temperature_18cm
```

Adapter НЕ выполняет интерполяцию.

---

# 28. Где создаётся estimate

После получения raw WeatherData выполняется:

```text
WeatherAdapter
        ↓
WeatherData with T6/T18
        ↓
SoilTemperatureEstimator
        ↓
SoilTemperatureEstimate
```

После этого итоговый WeatherData должен содержать:

```text
soil_temperature_10cm_estimate
```

---

# 29. WeatherService orchestration

`WeatherService` становится orchestration point:

```text
WeatherClient
        ↓
WeatherAdapter
        ↓
WeatherData
        ↓
SoilTemperatureEstimator
        ↓
final WeatherData
```

Для frozen dataclass допускается создание нового объекта через:

```python
dataclasses.replace(...)
```

Например концептуально:

```python
weather = adapter.to_weather_data(payload)

estimate = estimator.estimate_at_10cm(
    weather.soil_temperature_6cm,
    weather.soil_temperature_18cm,
)

return replace(
    weather,
    soil_temperature_10cm_estimate=estimate,
)
```

---

# 30. Dependency Injection WeatherService

`SoilTemperatureEstimator` должен передаваться в `WeatherService` явно либо создаваться через согласованный composition root.

Предпочтительно:

```python
WeatherService(
    client=...,
    adapter=...,
    soil_temperature_estimator=...,
)
```

Это сохраняет testability.

---

# 31. WeatherService не знает формулу

WeatherService не должен содержать:

```text
1/3
6
10
18
```

и не должен выполнять арифметику интерполяции.

Формула принадлежит:

```text
SoilTemperatureEstimator
```

---

# 32. ColoradoBeetleRiskCalculator

Добавляется:

```text
ColoradoBeetleRiskCalculator
```

Threat code:

```text
COLORADO_BEETLE
```

Расположение:

```text
app/risk/calculators/colorado_beetle.py
```

---

# 33. Input Colorado Calculator

Calculator использует:

```text
WeatherData.soil_temperature_10cm_estimate
```

Он НЕ использует напрямую:

```text
soil_temperature
soil_temperature_6cm
soil_temperature_18cm
```

И не выполняет интерполяцию самостоятельно.

---

# 34. Colorado factor

Используется один фактор:

```text
SOIL_TEMPERATURE_10CM
```

Он:

```text
required=True
```

---

# 35. Colorado threshold

Правило EPIC-07:

```text
estimated T10 is None
→ MISSING

estimated T10 < 13.0
→ NOT_MATCHED

estimated T10 >= 13.0
→ MATCHED
```

---

# 36. Почему используется >= 13 °C

Исследовательская база связывает температуру почвы около:

```text
13 °C
```

с интенсивным выходом колорадского жука.

Для сезонного индикатора PestWatch выбирается нижняя граница:

```text
13 °C
```

а не верхняя:

```text
15 °C
```

Это даёт прозрачное бинарное правило:

```text
>=13
```

---

# 37. Colorado RiskFactorResult

Пример:

```text
estimated T10 = 14.2 °C
```

Calculator возвращает:

```text
factor:
SOIL_TEMPERATURE_10CM

state:
MATCHED

actual_value:
14.2

expected:
>= 13 °C

required:
True
```

---

# 38. Explanation — MATCHED

Предлагаемый текст:

```text
Температура почвы на глубине около 10 см соответствует условиям активного выхода колорадского жука.
```

---

# 39. Explanation — NOT_MATCHED

```text
Температура почвы на глубине около 10 см ниже уровня, связанного с активным выходом колорадского жука.
```

Не допускается:

```text
Колорадского жука нет.
```

---

# 40. Explanation — MISSING

```text
Недостаточно данных для оценки температуры почвы на глубине около 10 см.
```

---

# 41. Provenance и RiskFactorResult

`RiskFactorResult.actual_value` содержит:

```text
estimate.temperature
```

например:

```text
14.2
```

Но provenance остаётся в:

```text
WeatherData
→ SoilTemperatureEstimate
```

Это означает:

```text
RiskFactorResult
→ результат проверки

SoilTemperatureEstimate
→ происхождение используемого значения
```

---

# 42. Assessment readiness

EPIC-07 не реализует Assessment persistence.

Но модель должна позволять в будущем сохранить:

```text
T6
T18
estimated T10
method
source depths
```

чтобы оценка была воспроизводимой.

---

# 43. Пользовательское «Как рассчитано?»

UI не входит в EPIC-07.

Но domain-модель должна позволять позднее показать:

```text
Температура почвы на глубине около 10 см: 14,2 °C

Как рассчитано:
по данным погодной модели для глубин 6 и 18 см.
```

Расширенное техническое описание может содержать:

```text
использована линейная интерполяция
```

---

# 44. Test Structure

Предлагаемая структура:

```text
tests/unit/domain/
    test_soil_temperature_estimate.py

tests/unit/weather/
    test_soil_temperature_estimator.py

tests/unit/risk/calculators/
    test_colorado_beetle.py

tests/unit/integrations/weather/
    test_weather_client.py
    test_weather_adapter.py

tests/unit/services/
    test_weather_service.py

tests/integration/
    test_colorado_beetle_risk.py
    test_weather_integration.py
```

---

# 45. Domain tests

Проверить:

```text
SoilTemperatureEstimate создаётся

depth_cm сохраняется

temperature сохраняется

source_depths сохраняются

source_temperatures сохраняются

method сохраняется

объект immutable
```

---

# 46. Estimator base test

Например:

```text
T6  = 16
T18 = 10
```

Расчёт:

```text
16 + (10 - 16) × 1/3
= 14
```

Expected:

```text
T10 = 14
```

---

# 47. Estimator ascending profile

```text
T6  = 10
T18 = 16
```

Expected:

```text
T10 = 12
```

---

# 48. Equal temperatures

```text
T6  = 13
T18 = 13
```

Expected:

```text
T10 = 13
```

---

# 49. Zero test

```text
T6  = 0
T18 = 6
```

Expected:

```text
T10 = 2
```

Zero не считается missing.

---

# 50. Negative test

```text
T6  = -4
T18 = 2
```

Expected:

```text
T10 = -2
```

---

# 51. Missing T6

```text
T6 = None
T18 = 14
```

Expected:

```text
None
```

---

# 52. Missing T18

```text
T6 = 14
T18 = None
```

Expected:

```text
None
```

---

# 53. Both missing

```text
T6 = None
T18 = None
```

Expected:

```text
None
```

---

# 54. Provenance test

Для:

```text
T6=16
T18=10
```

проверить:

```text
depth_cm == 10

source_depths_cm == (6, 18)

source_temperatures == (16, 10)

method == LINEAR_INTERPOLATION
```

---

# 55. WeatherClient tests

Проверить наличие в request:

```text
soil_temperature_6cm
soil_temperature_18cm
```

И сохранить все проверки EPIC-04:

```text
timeout
units
coordinates
error handling
```

---

# 56. WeatherAdapter tests

Payload:

```json
{
  "current": {
    "soil_temperature_0cm": 18.0,
    "soil_temperature_6cm": 16.0,
    "soil_temperature_18cm": 10.0
  }
}
```

Mapping:

```text
soil_temperature = 18
soil_temperature_6cm = 16
soil_temperature_18cm = 10
```

Adapter:

```text
НЕ создаёт SoilTemperatureEstimate
```

---

# 57. WeatherService tests

Проверить цепочку:

```text
Adapter
→ WeatherData(T6/T18)
→ Estimator
→ WeatherData(estimate)
```

Также проверить:

```text
Estimator получает правильные T6 / T18
```

---

# 58. Missing weather data integration

Если Open-Meteo не вернул:

```text
soil_temperature_6cm
```

или:

```text
soil_temperature_18cm
```

final:

```text
soil_temperature_10cm_estimate=None
```

Это не является technical error Weather Integration.

---

# 59. Colorado Calculator boundary matrix

| Estimated T10 | State |
|---:|---|
| `None` | `MISSING` |
| `-5.0` | `NOT_MATCHED` |
| `0.0` | `NOT_MATCHED` |
| `12.9` | `NOT_MATCHED` |
| `13.0` | `MATCHED` |
| `13.1` | `MATCHED` |
| `20.0` | `MATCHED` |

---

# 60. Colorado calculator contract tests

Проверить:

```text
factor == SOIL_TEMPERATURE_10CM

required == True

actual_value == estimate.temperature

expected == >= 13 °C

explanation заполнен
```

---

# 61. Calculator не знает provenance arithmetic

Проверить архитектурно, что:

```text
ColoradoBeetleRiskCalculator
```

не содержит:

```text
6
18
1/3
interpolation
```

Calculator получает уже подготовленный estimate.

---

# 62. End-to-End RiskEngine — HIGH

Например:

```text
T6  = 16
T18 = 10
```

→

```text
estimated T10 = 14
```

→

```text
MATCHED
```

→

```text
CALCULATED
HIGH
```

---

# 63. End-to-End RiskEngine — LOW

Например:

```text
T6  = 12
T18 = 9
```

→

```text
estimated T10 = 11
```

→

```text
NOT_MATCHED
```

→

```text
CALCULATED
LOW
```

---

# 64. End-to-End RiskEngine — INSUFFICIENT_DATA

```text
T6 = None
T18 = 14
```

→

```text
estimate=None
```

→

```text
MISSING
```

→

```text
INSUFFICIENT_DATA
risk_level=None
```

---

# 65. Real Open-Meteo Smoke

После автоматических тестов выполнить реальный запрос.

Не проверять заранее конкретные температуры.

Подтвердить наличие:

```text
soil_temperature_6cm
soil_temperature_18cm
```

После обработки подтвердить:

```text
SoilTemperatureEstimate
```

с:

```text
depth_cm=10
method=LINEAR_INTERPOLATION
```

---

# 66. Source Traceability

Перед PR подтвердить две независимые цепочки.

## Weather data

```text
Open-Meteo documentation
        ↓
soil_temperature_6cm
soil_temperature_18cm
```

## Biological rule

```text
Россельхозцентр
        ↓
температура почвы около 10 см
        ↓
около 13 °C
        ↓
интенсивный выход
        ↓
PestWatch threshold >= 13 °C
```

---

# 67. Разделение факта и инженерного решения

Источник подтверждает:

```text
температура почвы
+
биологический порог
```

Источник НЕ подтверждает:

```text
линейную интерполяцию Open-Meteo
```

Линейная интерполяция является:

```text
инженерным решением PestWatch
```

Это должно быть явно задокументировано.

---

# 68. Architecture Boundaries

## WeatherClient

Знает:

```text
Open-Meteo field names
```

Не знает:

```text
Colorado Beetle
13 °C
interpolation
```

## WeatherAdapter

Знает:

```text
Open-Meteo JSON
WeatherData
```

Не знает:

```text
Colorado Beetle
13 °C
interpolation
```

## SoilTemperatureEstimator

Знает:

```text
6 см
10 см
18 см
linear interpolation
```

Не знает:

```text
Colorado Beetle
13 °C
RiskLevel
```

## ColoradoBeetleRiskCalculator

Знает:

```text
estimated T10
13 °C
```

Не знает:

```text
Open-Meteo
T6/T18 interpolation formula
HTTP
```

## RiskEngine

Не меняется и ничего не знает о:

```text
почве
глубине
Open-Meteo
колорадском жуке
```

---

# 69. Architecture Review Commands

Перед PR проверить отсутствие Risk specifics в Weather Integration:

```powershell
Get-ChildItem .\app\integrations\weather\*.py |
    Select-String -Pattern "COLORADO|Colorado|13.0|RiskLevel|RiskResult"
```

Ожидаем пустой вывод.

Проверить Calculator:

```powershell
Get-ChildItem .\app\risk\calculators\colorado_beetle.py |
    Select-String -Pattern "requests|flask|sqlalchemy|WeatherClient|6cm|18cm|interpol"
```

Ожидаем пустой вывод.

---

# 70. TASKS

## TASK-07.01

Добавить:

```text
SoilTemperatureEstimateMethod
```

## TASK-07.02

Добавить:

```text
SoilTemperatureEstimate
```

## TASK-07.03

Расширить `WeatherData`.

## TASK-07.04

Обновить Domain tests.

## TASK-07.05

Расширить WeatherClient:

```text
soil_temperature_6cm
soil_temperature_18cm
```

## TASK-07.06

Расширить WeatherAdapter.

## TASK-07.07

Создать:

```text
SoilTemperatureEstimator
```

## TASK-07.08

Реализовать линейную интерполяцию.

## TASK-07.09

Реализовать missing semantics.

## TASK-07.10

Добавить provenance.

## TASK-07.11

Подключить estimator к WeatherService.

## TASK-07.12

Реализовать:

```text
ColoradoBeetleRiskCalculator
```

## TASK-07.13

Покрыть threshold boundary tests.

## TASK-07.14

Добавить Calculator → RiskEngine integration.

## TASK-07.15

Выполнить real Open-Meteo smoke.

## TASK-07.16

Выполнить regression EPIC-01–06.

## TASK-07.17

Провести Source Traceability Review.

## TASK-07.18

Провести Architecture Review.

## TASK-07.19

Провести Scope Review.

---

# 71. Acceptance Criteria

- [ ] `WeatherData` содержит `soil_temperature_6cm`;
- [ ] `WeatherData` содержит `soil_temperature_18cm`;
- [ ] `WeatherData` содержит `soil_temperature_10cm_estimate`;
- [ ] существующий `soil_temperature` сохраняет semantics 0 cm;
- [ ] новые поля backward compatible;
- [ ] WeatherClient запрашивает 6 cm;
- [ ] WeatherClient запрашивает 18 cm;
- [ ] WeatherAdapter mapping 6 cm работает;
- [ ] WeatherAdapter mapping 18 cm работает;
- [ ] WeatherAdapter не интерполирует;
- [ ] `SoilTemperatureEstimateMethod` реализован;
- [ ] `SoilTemperatureEstimate` реализован;
- [ ] provenance сохраняется;
- [ ] estimator реализован;
- [ ] estimator не выполняет HTTP;
- [ ] estimator не знает Colorado Beetle;
- [ ] используется linear interpolation;
- [ ] target depth = 10 cm;
- [ ] T6 missing → estimate None;
- [ ] T18 missing → estimate None;
- [ ] zero является валидным значением;
- [ ] отрицательные температуры валидны;
- [ ] WeatherService orchestration работает;
- [ ] `ColoradoBeetleRiskCalculator` реализован;
- [ ] Calculator использует только estimate;
- [ ] `<13 °C → NOT_MATCHED`;
- [ ] `>=13 °C → MATCHED`;
- [ ] missing estimate → MISSING;
- [ ] фактор required;
- [ ] Calculator не интерполирует;
- [ ] Calculator не выполняет HTTP;
- [ ] Calculator не определяет RiskLevel;
- [ ] Calculator → RiskEngine flow работает;
- [ ] missing → INSUFFICIENT_DATA;
- [ ] source traceability подтверждена;
- [ ] real Open-Meteo smoke пройден;
- [ ] regression EPIC-01–06 проходит.

---

# 72. PR Checklist

## Domain

```text
[ ] SoilTemperatureEstimateMethod
[ ] SoilTemperatureEstimate
[ ] WeatherData extension
[ ] backward compatibility
```

## Weather

```text
[ ] 6 cm requested
[ ] 18 cm requested
[ ] Adapter mapping
[ ] missing values
[ ] WeatherService integration
```

## Estimator

```text
[ ] interpolation
[ ] ascending profile
[ ] descending profile
[ ] equal temperatures
[ ] zero
[ ] negative
[ ] T6 missing
[ ] T18 missing
[ ] provenance
```

## Colorado Beetle

```text
[ ] calculator
[ ] 12.9
[ ] 13.0
[ ] 13.1
[ ] missing
[ ] explanation
[ ] required
```

## Integration

```text
[ ] Weather → Estimate
[ ] Estimate → Calculator
[ ] Calculator → RiskEngine
[ ] real Open-Meteo smoke
[ ] full regression
```

---

# 73. Definition of Done

EPIC-07 считается завершённым:

```text
Open-Meteo T6 / T18
        +
WeatherData Extension
        +
SoilTemperatureEstimate
        +
Provenance
        +
SoilTemperatureEstimator
        +
Linear Interpolation T10
        +
ColoradoBeetleRiskCalculator
        +
Boundary Tests
        +
Missing Data Tests
        +
Calculator → RiskEngine Integration
        +
Real Open-Meteo Smoke
        +
Source Traceability Review
        +
EPIC-01–06 Regression
        +
Architecture Review
        +
Scope Review
        ↓
READY FOR PR
```

---

# 74. Что получится после EPIC-07

После merge PestWatch будет поддерживать реальные калькуляторы для трёх из четырёх угроз:

```text
Иксодовые клещи           ✓
Капустная тля             ✓
Колорадский жук           ✓
Яблонная плодожорка       следующий этап
```

Следующей незакрытой предметной моделью останется:

```text
Codling Moth
        ↓
Historical Weather
        ↓
Degree Days
        ↓
CodlingMothRiskCalculator
```

---

# 75. Главное правило EPIC-07

PestWatch не утверждает:

```text
Open-Meteo измерил температуру
на глубине 10 см.
```

PestWatch утверждает:

```text
На основании модельных температур
на глубинах 6 и 18 см
рассчитана оценка температуры
на глубине около 10 см.
```

А затем именно к этой оценке применяется предметный порог:

```text
>= 13 °C
```
