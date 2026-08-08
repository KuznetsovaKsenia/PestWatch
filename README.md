# EPIC-03 — Threat Catalog

## 1. Цель EPIC

Создать справочник поддерживаемых видов, источников и профилактических рекомендаций для PestWatch.

После завершения EPIC система должна уметь:

```text
хранить сведения о поддерживаемых видах
        +
хранить официальные источники
        +
хранить профилактические рекомендации
        +
получать эти данные через Repository / Service
        +
отдавать их через API
        +
показывать базовую справочную страницу
```

На этом этапе система ещё не оценивает риск и не получает реальную погоду.

Главный результат EPIC:

> В PestWatch появляется централизованный предметный каталог, на который позже смогут ссылаться Risk Engine, Assessment Flow и UI.

---

# 2. Git

## 2.1 Базовая ветка

EPIC-03 создаётся от актуального:

```text
main
```

после merge:

```text
EPIC-02 — Domain Core
```

## 2.2 Рабочая ветка

```text
feature/epic-03-threat-catalog
```

## 2.3 Pull Request

Планируемое название:

```text
EPIC-03: Threat Catalog
```

Рабочий цикл:

```text
main
  ↓
feature/epic-03-threat-catalog
  ↓
implementation
  ↓
unit tests
  ↓
integration/API tests
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

В EPIC-03 входят:

## Domain / reference data

```text
Threat
Source
Recommendation
```

## Persistence

SQLAlchemy ORM-модели для:

```text
Threat
Source
Recommendation
```

## Seed data

Первоначальное наполнение справочника четырьмя поддерживаемыми видами:

```text
Иксодовые клещи
Колорадский жук
Капустная тля
Яблонная плодожорка
```

## Repository Layer

Минимальные операции чтения каталога.

## Service Layer

Получение и подготовка справочных данных для приложения.

## API

Минимальные endpoints:

```http
GET /api/threats
GET /api/threats/{code}
```

## Web UI

Минимальная справочная страница со списком поддерживаемых видов.

## Tests

- unit tests;
- repository integration tests;
- API tests;
- regression EPIC-01 + EPIC-02.

---

# 4. Out of Scope

В EPIC-03 сознательно не входят:

- Weather API;
- геокодирование;
- WeatherData mapping;
- RiskEngine;
- RiskCalculator;
- Risk Rules;
- DegreeDaysCalculator;
- Assessment;
- история Assessment;
- пользовательский выбор профиля;
- расчет RiskLevel;
- прогноз риска;
- уведомления;
- административный интерфейс;
- редактирование каталога через UI;
- пользовательские аккаунты.

Важно:

> Threat Catalog хранит знания о поддерживаемых видах, но не выполняет расчет риска.

---

# 5. Архитектурное положение EPIC-03

После EPIC-03 архитектура выглядит так:

```text
Controller / API
        ↓
ThreatService
        ↓
ThreatRepository
        ↓
SQLAlchemy ORM
        ↓
SQLite
```

При этом:

```text
Domain
```

остаётся независимым от инфраструктуры.

Направление зависимостей:

```text
controllers
    ↓
services
    ↓
repositories
    ↓
models
```

Допустимо:

```text
services → domain
repositories → domain
```

Недопустимо:

```text
domain → SQLAlchemy
domain → Flask
domain → repositories
```

---

# 6. Предметная модель Threat Catalog

## 6.1 Threat

`Threat` описывает один поддерживаемый системой вид.

Минимальные поля:

```text
code
name
category
description
active
```

Предлагаемая модель:

```python
@dataclass(frozen=True)
class Threat:
    code: str
    name: str
    category: str
    description: str
    active: bool
```

На текущем этапе `category` может быть строкой.

Примеры:

```text
HUMAN
GARDEN
VEGETABLE_GARDEN
```

Создание отдельного enum `ThreatCategory` сейчас не обязательно, если в этом нет реальной необходимости.

---

## 6.2 Source

`Source` описывает источник информации, используемый для формирования справочных сведений и будущих правил.

Минимальные поля:

```text
id
title
organization
url
description
```

Пример:

```text
organization:
Роспотребнадзор

title:
Профилактика укусов клещей
```

---

## 6.3 Recommendation

`Recommendation` содержит профилактический совет для конкретного вида.

Минимальные поля:

```text
id
threat_code
text
priority
```

`priority` используется для стабильного порядка отображения.

---

# 7. Связи

Логическая модель:

```text
Threat
  │
  ├── Recommendation[]
  │
  └── Source[]
```

Для MVP:

```text
Threat → Recommendation
```

может быть one-to-many.

Для:

```text
Threat ↔ Source
```

возможны два подхода:

```text
one-to-many
```

или:

```text
many-to-many
```

Для текущего MVP выбираем **many-to-many**, потому что один официальный источник может использоваться для нескольких видов, а один вид может иметь несколько источников.

---

# 8. ORM-модель

## 8.1 ThreatModel

Минимальные поля:

```text
id
code
name
category
description
active
```

Ограничения:

```text
code
→ unique
→ not null
```

---

## 8.2 SourceModel

Минимальные поля:

```text
id
title
organization
url
description
```

---

## 8.3 RecommendationModel

Минимальные поля:

```text
id
threat_id
text
priority
```

Foreign Key:

```text
threat_id → ThreatModel.id
```

---

## 8.4 ThreatSourceModel

Association table:

```text
threat_id
source_id
```

для связи many-to-many.

---

# 9. Seed Data

В базе должны появиться четыре Threat.

## 9.1 Иксодовые клещи

```text
code:
TICK

name:
Иксодовые клещи

category:
HUMAN
```

Описание:

> Клещи, активность которых имеет выраженную сезонность и зависит в том числе от погодных условий.

---

## 9.2 Колорадский жук

```text
code:
COLORADO_BEETLE

name:
Колорадский жук

category:
VEGETABLE_GARDEN
```

Описание:

> Вредитель картофеля и других паслёновых культур.

---

## 9.3 Капустная тля

```text
code:
CABBAGE_APHID

name:
Капустная тля

category:
VEGETABLE_GARDEN
```

Описание:

> Вредитель капустных культур, активность которого зависит от погодных условий.

---

## 9.4 Яблонная плодожорка

```text
code:
CODLING_MOTH

name:
Яблонная плодожорка

category:
GARDEN
```

Описание:

> Один из распространённых вредителей плодовых культур.

---

# 10. Source Seed Data

В seed должны быть добавлены официальные или исследовательские источники, уже использованные в проекте.

На уровне EPIC-03 фиксируем структуру, но конкретный окончательный набор URL должен соответствовать исследованию.

Важно:

> Не добавлять вымышленные URL и не создавать «примерные источники» только ради заполнения таблицы.

---

# 11. Recommendation Seed Data

Для каждого Threat должно быть минимум 2–3 профилактических рекомендации.

Пример для клещей:

```text
использовать закрытую одежду
проводить самоосмотр после прогулки
использовать разрешённые репелленты
```

Для растительных вредителей рекомендации должны быть информационными и профилактическими.

На этом этапе не реализуем подробные схемы применения химических препаратов.

---

# 12. Repository Layer

Создать:

```text
app/repositories/threat_repository.py
```

Минимальный интерфейс:

```python
class ThreatRepository:
    def get_all(self) -> list[Threat]:
        ...

    def get_by_code(self, code: str) -> Threat | None:
        ...
```

Если необходимо вернуть связанные данные, допускается отдельная структура результата.

Repository:

- знает SQLAlchemy;
- знает ORM;
- не содержит HTTP;
- не содержит Flask route logic;
- не рассчитывает риск.

---

# 13. Service Layer

Создать:

```text
app/services/threat_service.py
```

Минимальные операции:

```python
get_all_threats()
get_threat_by_code(code)
```

Service:

```text
Controller
   ↓
ThreatService
   ↓
ThreatRepository
```

Service не должен обращаться к SQLAlchemy напрямую.

---

# 14. API

## 14.1 GET /api/threats

Возвращает список поддерживаемых видов.

Пример структуры:

```json
{
  "success": true,
  "data": [
    {
      "code": "TICK",
      "name": "Иксодовые клещи",
      "category": "HUMAN",
      "description": "..."
    }
  ]
}
```

---

## 14.2 GET /api/threats/{code}

Возвращает подробную информацию.

Пример:

```json
{
  "success": true,
  "data": {
    "code": "TICK",
    "name": "Иксодовые клещи",
    "category": "HUMAN",
    "description": "...",
    "recommendations": [],
    "sources": []
  }
}
```

---

## 14.3 Неизвестный code

Например:

```http
GET /api/threats/UNKNOWN
```

Ответ:

```http
404
```

Тело:

```json
{
  "success": false,
  "error": {
    "code": "THREAT_NOT_FOUND",
    "message": "Threat not found."
  }
}
```

---

# 15. Web UI

В EPIC-03 достаточно минимальной справочной страницы.

Например:

```http
GET /threats
```

Показывает:

```text
Иксодовые клещи
Колорадский жук
Капустная тля
Яблонная плодожорка
```

Можно отображать:

- название;
- категорию;
- краткое описание.

Подробный дизайн не требуется.

---

# 16. TASKS

## TASK-03.01 — Добавить domain model Threat

Создать:

```text
app/domain/threat.py
```

---

## TASK-03.02 — Добавить domain model Source

Создать:

```text
app/domain/source.py
```

---

## TASK-03.03 — Добавить domain model Recommendation

Создать:

```text
app/domain/recommendation.py
```

---

## TASK-03.04 — Добавить ORM ThreatModel

Создать:

```text
app/models/threat.py
```

---

## TASK-03.05 — Добавить ORM SourceModel

Создать:

```text
app/models/source.py
```

---

## TASK-03.06 — Добавить ORM RecommendationModel

Создать:

```text
app/models/recommendation.py
```

---

## TASK-03.07 — Добавить association table Threat ↔ Source

---

## TASK-03.08 — Создать механизм инициализации schema

Убедиться, что:

```python
db.create_all()
```

создаёт все новые таблицы.

---

## TASK-03.09 — Создать seed script/function

Добавить четыре Threat и связанные данные.

Seed должен быть idempotent:

```text
повторный запуск
→ не создаёт дубликаты
```

---

## TASK-03.10 — Создать ThreatRepository

Реализовать:

```text
get_all
get_by_code
```

---

## TASK-03.11 — Создать ThreatService

Реализовать:

```text
get_all_threats
get_threat_by_code
```

---

## TASK-03.12 — Создать API route GET /api/threats

---

## TASK-03.13 — Создать API route GET /api/threats/{code}

---

## TASK-03.14 — Реализовать 404 THREAT_NOT_FOUND

---

## TASK-03.15 — Создать справочную страницу /threats

---

## TASK-03.16 — Добавить unit tests domain models

---

## TASK-03.17 — Добавить repository integration tests

---

## TASK-03.18 — Добавить service tests

---

## TASK-03.19 — Добавить API tests

---

## TASK-03.20 — Выполнить regression EPIC-01 + EPIC-02

---

# 17. Unit Test Scope

## Threat

Проверить:

- создание;
- code;
- name;
- category;
- description;
- active.

## Source

Проверить:

- создание;
- title;
- organization;
- url.

## Recommendation

Проверить:

- создание;
- threat_code;
- text;
- priority.

---

# 18. Repository Integration Tests

Проверить:

```text
save/seed data
        ↓
ThreatRepository.get_all()
        ↓
4 Threat
```

и:

```text
get_by_code("TICK")
→ Threat
```

а:

```text
get_by_code("UNKNOWN")
→ None
```

---

# 19. Seed Tests

Проверить:

```text
первый seed
→ 4 Threat
```

повторный:

```text
второй seed
→ всё ещё 4 Threat
```

То есть seed idempotent.

---

# 20. API Test Scope

## GET /api/threats

Проверить:

```text
HTTP 200
success = true
4 элемента
```

---

## GET /api/threats/TICK

Проверить:

```text
HTTP 200
code = TICK
name = Иксодовые клещи
recommendations присутствуют
sources присутствуют
```

---

## GET /api/threats/UNKNOWN

Проверить:

```text
HTTP 404
success = false
error.code = THREAT_NOT_FOUND
```

---

# 21. Regression Gate

Перед PR:

```powershell
python -m pytest
```

должны пройти:

```text
EPIC-01 integration tests
+
EPIC-02 domain unit tests
+
EPIC-03 unit tests
+
repository integration tests
+
service tests
+
API tests
```

---

# 22. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-03-01 | Threat domain model реализован |
| AC-03-02 | Source domain model реализован |
| AC-03-03 | Recommendation domain model реализован |
| AC-03-04 | ORM ThreatModel реализован |
| AC-03-05 | ORM SourceModel реализован |
| AC-03-06 | ORM RecommendationModel реализован |
| AC-03-07 | Threat ↔ Source association реализована |
| AC-03-08 | schema создаётся |
| AC-03-09 | seed содержит 4 Threat |
| AC-03-10 | seed idempotent |
| AC-03-11 | ThreatRepository реализован |
| AC-03-12 | ThreatService реализован |
| AC-03-13 | GET /api/threats работает |
| AC-03-14 | GET /api/threats/{code} работает |
| AC-03-15 | неизвестный code возвращает 404 |
| AC-03-16 | recommendations возвращаются |
| AC-03-17 | sources возвращаются |
| AC-03-18 | /threats отображает каталог |
| AC-03-19 | unit tests проходят |
| AC-03-20 | integration/API tests проходят |
| AC-03-21 | regression EPIC-01/02 проходит |
| AC-03-22 | Risk Engine не реализован преждевременно |

---

# 23. Architecture Review Checklist

Перед PR проверить:

- [ ] domain models не импортируют SQLAlchemy;
- [ ] ORM находится только в `app/models`;
- [ ] Repository работает с ORM;
- [ ] Service не обращается к SQLAlchemy напрямую;
- [ ] Controller не обращается к Repository напрямую;
- [ ] Controller не содержит SQL;
- [ ] Threat Catalog не содержит Risk Rules;
- [ ] Threat Catalog не обращается к Weather API;
- [ ] seed не создаёт дубликаты;
- [ ] code Threat уникален;
- [ ] API возвращает стабильную структуру;
- [ ] 404 обрабатывается явно;
- [ ] существующие tests EPIC-01 и EPIC-02 остаются green.

---

# 24. PR Checklist

## Scope

- [ ] реализован только Threat Catalog;
- [ ] Risk Engine не добавлен;
- [ ] Weather Integration не добавлена;
- [ ] Assessment не добавлен.

## Domain

- [ ] Threat;
- [ ] Source;
- [ ] Recommendation.

## Persistence

- [ ] ThreatModel;
- [ ] SourceModel;
- [ ] RecommendationModel;
- [ ] ThreatSource association;
- [ ] schema initialization;
- [ ] seed.

## Application

- [ ] ThreatRepository;
- [ ] ThreatService;
- [ ] API list;
- [ ] API details;
- [ ] 404 handling;
- [ ] basic web catalog.

## Tests

- [ ] domain unit tests;
- [ ] seed tests;
- [ ] repository tests;
- [ ] service tests;
- [ ] API tests;
- [ ] full regression.

---

# 25. Definition of Done

EPIC-03 считается завершённым, когда:

```text
Threat
        +
Source
        +
Recommendation
        +
ORM Models
        +
Threat ↔ Source
        +
Seed Data
        +
ThreatRepository
        +
ThreatService
        +
GET /api/threats
        +
GET /api/threats/{code}
        +
404 handling
        +
Web catalog
        +
Tests
        +
Regression
        +
Architecture Review
        ↓
READY FOR PR
```

После merge в:

```text
main
```

проект будет содержать:

```text
EPIC-01
Technical Foundation

+

EPIC-02
Domain Core

+

EPIC-03
Threat Catalog
```

и можно будет переходить к:

```text
EPIC-04 — Weather Integration
```

---

# 26. Условие перехода к EPIC-04

EPIC-04 не начинается, пока:

- EPIC-03 полностью реализован;
- seed проверен;
- API tests проходят;
- regression green;
- architecture review завершён;
- PR создан;
- замечания исправлены;
- PR merged в `main`.
