# EPIC-05 — Risk Engine Core

## 1. Цель EPIC

Создать независимое ядро оценки сезонного риска в PestWatch.

После завершения EPIC система должна уметь:

```text
получить набор результатов факторов
        ↓
определить состояние оценки
        ↓
определить итоговый уровень риска
        ↓
сформировать RiskResult
```

EPIC-05 отвечает на вопрос:

> Как PestWatch преобразует результаты отдельных проверок условий в единый итог оценки риска?

На этом этапе ядро не должно знать:

- откуда пришла погода;
- какой внешний Weather API используется;
- где хранится Threat;
- как работает Flask;
- как результат будет показан пользователю.

---

# 2. Положение EPIC-05 в архитектуре

Текущее состояние:

```text
EPIC-01 — Technical Foundation
        ↓
EPIC-02 — Domain Core
        ↓
EPIC-03 — Threat Catalog
        ↓
EPIC-04 — Weather Integration
        ↓
EPIC-05 — Risk Engine Core
```

Будущая цепочка:

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

Ключевое правило:

```text
Calculator
→ определяет состояние отдельных факторов

RiskEngine
→ агрегирует результаты факторов
```

---

# 3. Git

## Базовая ветка

```text
main
```

после merge:

```text
EPIC-04 — Weather Integration
```

## Рабочая ветка

```text
feature/epic-05-risk-engine-core
```

## Pull Request

```text
EPIC-05: Risk Engine Core
```

---

# 4. Scope

В EPIC-05 входят:

```text
RiskCalculator contract
RiskEvaluation
RiskPolicy
RiskEngine
factor aggregation
RiskStatus determination
RiskLevel determination
RiskResult creation
explanation composition
deterministic unit tests
```

---

# 5. Out of Scope

В EPIC-05 сознательно не входят:

- Open-Meteo;
- HTTP;
- новые Weather integrations;
- Threat ORM;
- Repository;
- SQLite;
- Flask Controller;
- REST API оценки;
- UI оценки;
- Assessment;
- Assessment History;
- уведомления;
- геокодирование;
- historical weather;
- Degree Days;
- конкретные правила для яблонной плодожорки;
- полная реализация всех четырёх Threat calculators.

---

# 6. Главная архитектурная граница

Необходимо разделить:

```text
проверка отдельных условий
```

и:

```text
агрегация результатов
```

Например:

```text
temperature = MATCHED
season      = MATCHED
humidity    = NOT_MATCHED
```

Это ещё не `RiskLevel`.

Именно `RiskEngine` определяет итог:

```text
RiskFactorResult[]
        ↓
aggregation
        ↓
RiskLevel
```

---

# 7. RiskCalculator Contract

Создаём общий контракт калькулятора.

Предлагаемое расположение:

```text
app/risk/calculator.py
```

Контракт:

```python
from abc import ABC, abstractmethod

from app.domain import WeatherData
from app.domain import RiskFactorResult


class RiskCalculator(ABC):
    @abstractmethod
    def evaluate(
        self,
        weather: WeatherData,
    ) -> tuple[RiskFactorResult, ...]:
        ...
```

Калькулятор:

- получает данные;
- проверяет предметные условия;
- возвращает факторы;
- не определяет итоговый `RiskLevel`;
- не сохраняет данные;
- не выполняет HTTP.

---

# 8. Почему Calculator не возвращает RiskResult

Нельзя делать:

```text
TickCalculator
→ RiskResult
```

потому что тогда каждый калькулятор будет самостоятельно:

- определять `RiskStatus`;
- определять `RiskLevel`;
- формировать общий итог;
- дублировать правила агрегации.

Правильная модель:

```text
Calculator
→ RiskFactorResult[]

RiskEngine
→ RiskResult
```

---

# 9. RiskEvaluation

Для внутренней работы Risk Engine вводим отдельный объект:

```text
RiskEvaluation
```

Он представляет набор уже проверенных факторов до формирования итогового `RiskResult`.

Предлагаемая модель:

```python
@dataclass(frozen=True)
class RiskEvaluation:
    threat_code: str
    factors: tuple[RiskFactorResult, ...]
```

Расположение:

```text
app/risk/evaluation.py
```

Важно:

`RiskEvaluation` — внутренний объект Risk Engine.

Он не должен заменять публичный `RiskResult`.

---

# 10. RiskPolicy

Правила агрегации должны быть отделены от orchestration.

Создаём:

```text
app/risk/policy.py
```

Ответственность:

```text
RiskFactorResult[]
        ↓
RiskStatus
RiskLevel
```

Предлагаемый интерфейс:

```python
class RiskPolicy:
    def determine_status(
        self,
        factors: tuple[RiskFactorResult, ...],
    ) -> RiskStatus:
        ...

    def determine_level(
        self,
        factors: tuple[RiskFactorResult, ...],
        status: RiskStatus,
    ) -> RiskLevel | None:
        ...
```

---

# 11. Базовые состояния факторов

Уже существуют:

```text
MATCHED
NOT_MATCHED
MISSING
```

Смысл сохраняется:

```text
MATCHED
→ условие выполнено

NOT_MATCHED
→ показатель известен, но условие не выполнено

MISSING
→ показатель отсутствует
```

Критическое правило:

```text
MISSING != NOT_MATCHED
```

---

# 12. Определение RiskStatus

Для EPIC-05 фиксируем базовый алгоритм.

## CALCULATED

```text
нет MISSING
```

Все необходимые для данного Calculator факторы были проверены.

Пример:

```text
MATCHED
MATCHED
NOT_MATCHED
```

→

```text
CALCULATED
```

---

## LIMITED

Используется, если:

```text
есть MISSING
+
есть минимум один известный фактор
+
результат всё ещё допускает ограниченную оценку
```

Но здесь есть важное ограничение:

RiskEngine сам не знает, является ли конкретный фактор обязательным.

Поэтому в EPIC-05 вводим понятие:

```text
required
```

для результата фактора.

---

# 13. Расширение RiskFactorResult

Текущая модель:

```text
factor
state
actual_value
expected
explanation
```

Для корректного определения `LIMITED / INSUFFICIENT_DATA` необходимо знать:

```text
обязателен ли фактор
```

Поэтому предлагается добавить:

```python
required: bool = True
```

Итог:

```python
@dataclass(frozen=True)
class RiskFactorResult:
    factor: str
    state: RiskFactorState
    actual_value: object | None
    expected: str | None
    explanation: str
    required: bool = True
```

Это изменение Domain Core допустимо в EPIC-05, потому что оно напрямую необходимо для корректной агрегации.

---

# 14. INSUFFICIENT_DATA

Если хотя бы один:

```text
required=True
```

фактор имеет:

```text
MISSING
```

то:

```text
RiskStatus.INSUFFICIENT_DATA
```

и:

```text
risk_level = None
```

Пример:

```text
TEMPERATURE
required=True
MISSING
```

→

```text
INSUFFICIENT_DATA
```

---

# 15. LIMITED

Если:

```text
все required-факторы доступны
```

но отсутствует один или несколько:

```text
required=False
```

факторов:

```text
MISSING
```

то:

```text
LIMITED
```

При этом `RiskLevel` может быть рассчитан.

Пример:

```text
TEMPERATURE required=True  MATCHED
SEASON      required=True  MATCHED
HUMIDITY    required=False MISSING
```

→

```text
LIMITED
+
RiskLevel
```

---

# 16. CALCULATED

Если:

```text
ни одного MISSING
```

то:

```text
CALCULATED
```

---

# 17. ERROR

`ERROR` не должен формироваться из обычных `RiskFactorState`.

Он предназначен для технической ошибки вычисления.

Например:

```text
calculator exception
unexpected calculation failure
```

На уровне чистого `RiskPolicy` `ERROR` не рассчитывается.

Он создаётся `RiskEngine`, если Calculator/Policy завершился неожиданной вычислительной ошибкой.

---

# 18. Определение RiskLevel

Для EPIC-05 фиксируем простой общий механизм.

Считаются только факторы:

```text
state != MISSING
```

Для каждого:

```text
MATCHED     → 1
NOT_MATCHED → 0
```

Получаем:

```text
match_ratio =
matched / known_factors
```

---

# 19. Границы RiskLevel

Фиксируем:

```text
0.00 <= ratio < 0.25
→ LOW

0.25 <= ratio < 0.50
→ MODERATE

0.50 <= ratio < 0.75
→ ELEVATED

0.75 <= ratio <= 1.00
→ HIGH
```

Примеры:

```text
0 / 4
→ LOW

1 / 4
→ MODERATE

2 / 4
→ ELEVATED

3 / 4
→ HIGH

4 / 4
→ HIGH
```

---

# 20. Почему используем ratio

Это базовый общий механизм MVP.

Он:

- детерминирован;
- понятен;
- легко тестируется;
- не скрывает probabilistic model;
- не выдаёт себя за вероятность.

Важно:

```text
75% matched
```

НЕ означает:

```text
75% вероятность появления вредителя
```

Это только доля совпавших условий.

---

# 21. Ограничение Ratio Model

Не все факторы в реальности равнозначны.

Например:

```text
SEASON
```

может быть важнее:

```text
HUMIDITY
```

Но weighted scoring в EPIC-05 не реализуется.

Отдельная система:

```text
weights
```

может появиться позднее только при наличии обоснованных правил.

---

# 22. Пустой набор факторов

Если Calculator вернул:

```text
()
```

то невозможно вычислить результат.

RiskEngine должен вернуть:

```text
status = INSUFFICIENT_DATA
risk_level = None
```

с explanation:

```text
Недостаточно факторов для оценки.
```

---

# 23. Все факторы MISSING

Например:

```text
TEMPERATURE MISSING
SEASON      MISSING
```

результат:

```text
INSUFFICIENT_DATA
risk_level=None
```

---

# 24. Optional MISSING

Например:

```text
TEMPERATURE required=True MATCHED
SEASON      required=True MATCHED
HUMIDITY    required=False MISSING
```

Результат:

```text
LIMITED
```

Уровень считается только по известным факторам:

```text
2 MATCHED / 2 known
→ HIGH
```

Важно:

`MISSING` не входит в denominator.

---

# 25. Explanation

RiskEngine должен создавать краткое системное объяснение.

Примеры:

## CALCULATED

```text
Оценка выполнена по всем доступным факторам.
```

## LIMITED

```text
Оценка выполнена по обязательным факторам, часть дополнительных данных отсутствует.
```

## INSUFFICIENT_DATA

```text
Недостаточно обязательных данных для оценки.
```

## ERROR

```text
Не удалось выполнить оценку риска.
```

Threat-specific explanation остаётся внутри `RiskFactorResult.explanation`.

---

# 26. RiskEngine

Создаём:

```text
app/risk/engine.py
```

Предлагаемый интерфейс:

```python
class RiskEngine:
    def __init__(
        self,
        policy: RiskPolicy,
    ):
        self._policy = policy

    def evaluate(
        self,
        threat_code: str,
        factors: tuple[RiskFactorResult, ...],
    ) -> RiskResult:
        ...
```

RiskEngine:

- получает уже рассчитанные факторы;
- определяет status;
- определяет level;
- формирует `RiskResult`;
- формирует system explanation.

---

# 27. Почему RiskEngine пока не вызывает Calculator

В EPIC-05 сохраняем ядро максимально чистым.

То есть:

```text
Calculator
→ factors
```

и:

```text
RiskEngine
→ aggregate factors
```

Соединение:

```text
Threat
→ correct Calculator
→ RiskEngine
```

будет отдельным orchestration layer в следующем EPIC.

---

# 28. Error Handling

Если в `RiskEngine.evaluate()` возникает неожиданная ошибка Policy:

```text
RiskResult(
    threat_code=...,
    status=ERROR,
    risk_level=None,
    factors=...,
    explanation="Не удалось выполнить оценку риска."
)
```

Но:

```text
ValueError
```

из-за некорректного входа не следует автоматически скрывать как `ERROR`, если это programming error.

Поэтому в EPIC-05 желательно не использовать широкий:

```python
except Exception
```

без необходимости.

---

# 29. Immutable Results

Сохраняем существующий подход:

```text
@dataclass(frozen=True)
```

и:

```text
tuple[RiskFactorResult, ...]
```

Итог после создания не изменяется.

---

# 30. Risk Package

После EPIC-05:

```text
app/risk/
├── __init__.py
├── calculator.py
├── evaluation.py
├── policy.py
└── engine.py
```

---

# 31. Unit Tests Structure

```text
tests/unit/risk/
├── __init__.py
├── test_risk_policy.py
├── test_risk_engine.py
└── test_risk_evaluation.py
```

Дополняются существующие:

```text
tests/unit/domain/test_risk_factor_result.py
```

из-за поля:

```text
required
```

---

# 32. RiskPolicy Test Matrix

Проверить:

```text
all MATCHED
→ CALCULATED + HIGH
```

```text
all NOT_MATCHED
→ CALCULATED + LOW
```

```text
1/4 MATCHED
→ MODERATE
```

```text
2/4 MATCHED
→ ELEVATED
```

```text
3/4 MATCHED
→ HIGH
```

```text
required MISSING
→ INSUFFICIENT_DATA + None
```

```text
optional MISSING
→ LIMITED + RiskLevel
```

```text
all MISSING
→ INSUFFICIENT_DATA + None
```

```text
empty factors
→ INSUFFICIENT_DATA + None
```

---

# 33. Boundary Tests RiskLevel

Обязательно проверяем именно границы:

```text
0.00
→ LOW

0.249...
→ LOW

0.25
→ MODERATE

0.50
→ ELEVATED

0.75
→ HIGH

1.00
→ HIGH
```

На практике ratio получается из целого количества факторов, поэтому некоторые дробные значения можно тестировать напрямую через внутренний helper либо через подходящие размеры наборов.

---

# 34. RiskFactorResult Tests

После добавления:

```text
required
```

проверить:

```text
default required=True
```

и:

```text
required=False
```

---

# 35. RiskEngine Tests

Проверить:

```text
threat_code сохраняется
```

```text
factors сохраняются
```

```text
CALCULATED
→ RiskLevel обязательно присутствует
```

```text
LIMITED
→ RiskLevel присутствует
```

```text
INSUFFICIENT_DATA
→ RiskLevel=None
```

```text
empty factors
→ INSUFFICIENT_DATA
```

---

# 36. Calculator Contract Tests

Конкретную реализацию Calculator в EPIC-05 создавать не обязательно.

Но следует проверить, что абстрактный контракт нельзя instantiate напрямую.

Например:

```python
with pytest.raises(TypeError):
    RiskCalculator()
```

---

# 37. Первый реальный Calculator

В EPIC-05 **не реализуем все четыре вида**.

Чтобы проверить архитектуру end-to-end, допускается один минимальный reference calculator:

```text
TickRiskCalculator
```

НО только если это необходимо для доказательства контракта.

Моя рекомендация:

```text
не добавлять его в EPIC-05
```

Потому что конкретные пороги требуют возвращения к исследовательскому документу и должны быть реализованы отдельным EPIC.

EPIC-05 должен оставаться generic.

---

# 38. Яблонная плодожорка

В EPIC-05 точно не реализуется.

Причина:

```text
Degree Days
```

требуют временного ряда температур.

Текущий:

```text
WeatherData
```

представляет один погодный snapshot.

Поэтому:

```text
CODLING_MOTH
```

не должен быть искусственно адаптирован к текущей модели.

---

# 39. Архитектурное правило для Degree Days

Будущий Degree Days flow:

```text
historical / daily temperatures
        ↓
DegreeDaysCalculator
        ↓
accumulated temperature
        ↓
CodlingMothCalculator
```

Это отдельная capability.

EPIC-05 лишь должен позволить такому Calculator в будущем вернуть:

```text
RiskFactorResult(
    factor="DEGREE_DAYS",
    ...
)
```

---

# 40. TASKS

## TASK-05.01

Добавить:

```text
required: bool = True
```

в `RiskFactorResult`.

---

## TASK-05.02

Обновить существующие unit tests Domain Core.

---

## TASK-05.03

Создать `RiskCalculator` ABC.

---

## TASK-05.04

Создать `RiskEvaluation`.

---

## TASK-05.05

Создать `RiskPolicy`.

---

## TASK-05.06

Реализовать status aggregation.

---

## TASK-05.07

Реализовать match ratio.

---

## TASK-05.08

Реализовать RiskLevel boundaries.

---

## TASK-05.09

Создать `RiskEngine`.

---

## TASK-05.10

Реализовать system explanations.

---

## TASK-05.11

Покрыть RiskPolicy unit tests.

---

## TASK-05.12

Покрыть RiskEngine unit tests.

---

## TASK-05.13

Покрыть RiskEvaluation unit tests.

---

## TASK-05.14

Проверить Calculator contract.

---

## TASK-05.15

Выполнить полный regression EPIC-01–04.

---

# 41. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-05-01 | `RiskFactorResult.required` реализован |
| AC-05-02 | default `required=True` |
| AC-05-03 | `RiskCalculator` contract реализован |
| AC-05-04 | `RiskEvaluation` реализован |
| AC-05-05 | `RiskPolicy` реализован |
| AC-05-06 | `RiskEngine` реализован |
| AC-05-07 | MATCHED учитывается как совпавший фактор |
| AC-05-08 | NOT_MATCHED учитывается как известный несовпавший |
| AC-05-09 | MISSING не считается NOT_MATCHED |
| AC-05-10 | required MISSING → INSUFFICIENT_DATA |
| AC-05-11 | optional MISSING → LIMITED |
| AC-05-12 | empty factors → INSUFFICIENT_DATA |
| AC-05-13 | all MISSING → INSUFFICIENT_DATA |
| AC-05-14 | CALCULATED формируется без MISSING |
| AC-05-15 | LOW boundary работает |
| AC-05-16 | MODERATE boundary работает |
| AC-05-17 | ELEVATED boundary работает |
| AC-05-18 | HIGH boundary работает |
| AC-05-19 | missing factors не входят в ratio denominator |
| AC-05-20 | RiskResult создаётся через RiskEngine |
| AC-05-21 | RiskEngine не зависит от Flask |
| AC-05-22 | RiskEngine не зависит от SQLAlchemy |
| AC-05-23 | RiskEngine не зависит от Open-Meteo |
| AC-05-24 | RiskEngine не знает Threat ORM |
| AC-05-25 | конкретные биологические пороги не добавлены |
| AC-05-26 | Degree Days не реализованы |
| AC-05-27 | unit tests deterministic |
| AC-05-28 | regression EPIC-01–04 проходит |

---

# 42. Architecture Review Checklist

Перед PR проверить:

- [ ] `app/risk` не импортирует Flask;
- [ ] `app/risk` не импортирует SQLAlchemy;
- [ ] `app/risk` не импортирует `requests`;
- [ ] `app/risk` не знает Open-Meteo;
- [ ] `RiskCalculator` не знает Repository;
- [ ] `RiskPolicy` не знает Threat;
- [ ] `RiskPolicy` не выполняет HTTP;
- [ ] `RiskEngine` не выполняет HTTP;
- [ ] `RiskEngine` не обращается к SQLite;
- [ ] `RiskEngine` не содержит порогов конкретных вредителей;
- [ ] `MISSING != NOT_MATCHED`;
- [ ] required/optional факторы различаются;
- [ ] `RiskLevel` не интерпретируется как вероятность;
- [ ] Degree Days не добавлены;
- [ ] concrete calculators не добавлены преждевременно;
- [ ] tests не используют Flask context без необходимости;
- [ ] tests не используют интернет.

---

# 43. PR Checklist

## Domain

- [ ] `RiskFactorResult.required`;
- [ ] existing Domain tests updated.

## Risk Core

- [ ] `RiskCalculator`;
- [ ] `RiskEvaluation`;
- [ ] `RiskPolicy`;
- [ ] `RiskEngine`.

## Aggregation

- [ ] CALCULATED;
- [ ] LIMITED;
- [ ] INSUFFICIENT_DATA;
- [ ] LOW;
- [ ] MODERATE;
- [ ] ELEVATED;
- [ ] HIGH;
- [ ] empty factors;
- [ ] all MISSING;
- [ ] optional MISSING.

## Tests

- [ ] RiskCalculator contract tests;
- [ ] RiskEvaluation tests;
- [ ] RiskPolicy tests;
- [ ] RiskEngine tests;
- [ ] EPIC-01–04 regression.

---

# 44. Definition of Done

EPIC-05 считается завершённым:

```text
RiskFactorResult.required
        +
RiskCalculator Contract
        +
RiskEvaluation
        +
RiskPolicy
        +
RiskStatus Aggregation
        +
RiskLevel Aggregation
        +
RiskEngine
        +
System Explanations
        +
Deterministic Unit Tests
        +
EPIC-01–04 Regression
        +
Architecture Review
        ↓
READY FOR PR
```

---

# 45. Что получится после EPIC-05

После merge:

```text
EPIC-01 — Technical Foundation
EPIC-02 — Domain Core
EPIC-03 — Threat Catalog
EPIC-04 — Weather Integration
EPIC-05 — Risk Engine Core
```

PestWatch будет иметь:

```text
данные о Threat
        +
актуальный WeatherData
        +
универсальный механизм оценки
```

Но всё ещё не будет знать реальные биологические пороги конкретных видов.

---

# 46. Следующий EPIC

После EPIC-05 логично перейти к:

```text
EPIC-06 — Threat Risk Calculators
```

Там уже на основании исследовательских материалов будут реализованы конкретные правила:

```text
TickRiskCalculator
CabbageAphidRiskCalculator
ColoradoBeetleRiskCalculator
```

А яблонную плодожорку либо включим туда после расширения погодного контракта историческими данными, либо вынесем в отдельный Degree Days EPIC.

---

# 47. Ключевые решения EPIC-05

Перед разработкой фиксируем:

```text
1. Calculator ≠ RiskEngine

2. Calculator возвращает RiskFactorResult[]

3. RiskEngine агрегирует факторы в RiskResult

4. RiskFactorResult получает required flag

5. required MISSING
   → INSUFFICIENT_DATA

6. optional MISSING
   → LIMITED

7. MISSING не входит в denominator

8. RiskLevel определяется долей MATCHED среди известных факторов

9. RiskLevel не является вероятностью

10. Конкретные биологические пороги вне EPIC-05

11. Degree Days вне EPIC-05
```
