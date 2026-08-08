# EPIC-04 — Weather Integration

## 1. Цель EPIC

Интегрировать PestWatch с внешним погодным сервисом и преобразовывать внешние погодные данные во внутреннюю domain-модель:

```text
Location
    ↓
WeatherClient
    ↓
Open-Meteo
    ↓
WeatherAdapter
    ↓
WeatherData
    ↓
WeatherService
```

После завершения EPIC система должна уметь:

- получить текущие погодные данные по координатам;
- безопасно обработать HTTP-ответ Open-Meteo;
- преобразовать внешний JSON в `WeatherData`;
- отличать отсутствие отдельных показателей от значения `0`;
- корректно обрабатывать timeout, сетевые ошибки, HTTP errors и некорректный response;
- работать в тестах без реальных HTTP-запросов.

---

# 2. Git

## Базовая ветка

```text
main
```

после merge:

```text
EPIC-03 — Threat Catalog
```

## Рабочая ветка

```text
feature/epic-04-weather-integration
```

## Pull Request

```text
EPIC-04: Weather Integration
```

---

# 3. Выбранный Weather API

Используем:

```text
Open-Meteo Forecast API
```

Endpoint:

```text
https://api.open-meteo.com/v1/forecast
```

Для запроса обязательны координаты:

```text
latitude
longitude
```

Open-Meteo поддерживает параметр `current`, через который можно запросить текущие погодные показатели. Документация также указывает, что переменные, доступные как hourly, могут использоваться как current conditions. :contentReference[oaicite:1]{index=1}

---

# 4. Почему Open-Meteo

Для текущего проекта он подходит по следующим причинам:

```text
✓ JSON API
✓ HTTP GET
✓ не требует API key для free non-commercial tier
✓ поддерживает координаты
✓ поддерживает temperature_2m
✓ поддерживает relative_humidity_2m
✓ поддерживает precipitation
✓ поддерживает wind_speed_10m
✓ поддерживает soil_temperature_0cm
✓ позволяет явно задать единицы измерения
✓ позволяет использовать timezone=auto
```

Free API предназначен для некоммерческого использования и имеет rate limits. :contentReference[oaicite:2]{index=2}

---

# 5. API Key

Для текущего образовательного PestWatch:

```text
API key не требуется
```

Поэтому в EPIC-04 **не вводим фиктивный `WEATHER_API_KEY`**.

Это сознательное отличие от первоначального общего архитектурного предположения:

```text
.env → API key
```

Для Open-Meteo free API такого ключа нет.

Но конфигурацию внешнего сервиса всё равно вводим:

```text
WEATHER_API_BASE_URL
WEATHER_API_TIMEOUT_SECONDS
```

Чтобы код не содержал hardcoded infrastructure settings.

Если в будущем проект перейдёт на коммерческий Open-Meteo endpoint, API key можно будет добавить без изменения Domain/Service API.

---

# 6. Запрашиваемые данные

Domain-модель EPIC-02 уже содержит:

```python
WeatherData(
    observed_at,
    temperature,
    humidity,
    precipitation,
    wind_speed,
    soil_temperature,
)
```

Поэтому EPIC-04 запрашивает только необходимые параметры.

Open-Meteo mapping:

```text
temperature_2m
→ WeatherData.temperature

relative_humidity_2m
→ WeatherData.humidity

precipitation
→ WeatherData.precipitation

wind_speed_10m
→ WeatherData.wind_speed

soil_temperature_0cm
→ WeatherData.soil_temperature

time
→ WeatherData.observed_at
```

Open-Meteo документирует `soil_temperature_0cm` как температуру поверхности почвы/суши; это не температура на глубине 10 см. Этот смысл должен быть явно сохранён в коде и документации. :contentReference[oaicite:3]{index=3}

---

# 7. Единицы измерения

Внутренний Domain Core уже зафиксировал:

```text
temperature
→ °C

humidity
→ %

precipitation
→ mm

wind_speed
→ m/s

soil_temperature
→ °C
```

Поэтому запрос Open-Meteo должен явно содержать:

```text
temperature_unit=celsius
wind_speed_unit=ms
precipitation_unit=mm
```

Температура у Open-Meteo по умолчанию Celsius, precipitation — mm, но параметры задаём явно, чтобы контракт интеграции не зависел от default behaviour.

Open-Meteo по умолчанию возвращает ветер в km/h, поэтому `wind_speed_unit=ms` для PestWatch обязателен. :contentReference[oaicite:4]{index=4}

---

# 8. Timezone

Используем:

```text
timezone=auto
```

Open-Meteo в этом режиме автоматически определяет timezone по координатам. :contentReference[oaicite:5]{index=5}

Это важно, потому что:

```text
observed_at
```

должен отражать локальное время выбранной территории, а не время машины, на которой работает PestWatch.

---

# 9. HTTP Request Contract

Минимальный запрос:

```text
GET /v1/forecast

latitude=<latitude>
longitude=<longitude>

current=
    temperature_2m,
    relative_humidity_2m,
    precipitation,
    wind_speed_10m,
    soil_temperature_0cm

temperature_unit=celsius
wind_speed_unit=ms
precipitation_unit=mm
timezone=auto
```

Логически:

```text
Location
    ↓
latitude + longitude
    ↓
Open-Meteo request
```

`name`, `region` и `country` во внешний Weather API не передаются.

---

# 10. Архитектура EPIC-04

Создаём:

```text
app/integrations/weather/
├── __init__.py
├── client.py
├── adapter.py
├── exceptions.py
└── models.py
```

и:

```text
app/services/weather_service.py
```

Архитектура:

```text
WeatherService
      ↓
WeatherClient
      ↓
Open-Meteo
      ↓
raw response
      ↓
WeatherAdapter
      ↓
WeatherData
```

---

# 11. WeatherClient

Ответственность:

```text
HTTP
```

Только HTTP.

Он:

- формирует URL/query params;
- задаёт timeout;
- выполняет GET;
- проверяет HTTP status;
- получает JSON;
- переводит infrastructure failures в наши integration exceptions.

Он **не**:

- создаёт `WeatherData`;
- рассчитывает RiskLevel;
- знает про Threat;
- знает про Risk Engine.

Предлагаемый интерфейс:

```python
class WeatherClient:
    def get_current_weather(
        self,
        latitude: float,
        longitude: float,
    ) -> dict:
        ...
```

---

# 12. WeatherAdapter

Ответственность:

```text
external JSON → WeatherData
```

Интерфейс:

```python
class WeatherAdapter:
    def to_weather_data(
        self,
        payload: dict,
    ) -> WeatherData:
        ...
```

Adapter знает:

```text
Open-Meteo JSON structure
```

и:

```text
WeatherData
```

Но не выполняет HTTP.

---

# 13. WeatherService

Ответственность:

```text
application use case
```

Интерфейс:

```python
class WeatherService:
    def get_current_weather(
        self,
        location: Location,
    ) -> WeatherData:
        ...
```

Логика:

```text
Location
    ↓
WeatherClient
    ↓
raw payload
    ↓
WeatherAdapter
    ↓
WeatherData
```

Service не знает деталей JSON Open-Meteo.

---

# 14. External Response

Ожидаемый фрагмент Open-Meteo response:

```json
{
  "latitude": 55.75,
  "longitude": 37.62,
  "timezone": "Europe/Moscow",
  "current": {
    "time": "2026-08-08T19:00",
    "temperature_2m": 18.4,
    "relative_humidity_2m": 67,
    "precipitation": 0.0,
    "wind_speed_10m": 3.2,
    "soil_temperature_0cm": 16.1
  }
}
```

Важно:

> Это infrastructure DTO, а не Domain Model.

Он не должен распространяться за пределы integration layer.

---

# 15. Missing Data

Если отдельный optional показатель отсутствует:

```text
soil_temperature_0cm отсутствует
```

Adapter создаёт:

```python
WeatherData(
    ...
    soil_temperature=None,
)
```

Нельзя:

```text
missing → 0
```

Потому что уже в EPIC-02 зафиксировано:

```text
None != 0.0
```

То же правило применимо к остальным погодным показателям.

---

# 16. Обязательные данные

Для создания осмысленного `WeatherData` обязательно наличие:

```text
current
current.time
```

Погодные показатели:

```text
temperature
humidity
precipitation
wind_speed
soil_temperature
```

считаются optional и допускают `None`.

Причина:

в будущем Risk Engine сам определит, хватает ли конкретному Threat имеющихся показателей.

Weather Integration не должна принимать это решение вместо Risk Engine.

---

# 17. Ошибки интеграции

Вводим собственную иерархию exceptions:

```text
WeatherIntegrationError
├── WeatherTimeoutError
├── WeatherConnectionError
├── WeatherResponseError
└── WeatherDataError
```

---

# 18. WeatherTimeoutError

Возникает при превышении timeout HTTP-запроса.

Пример:

```text
Open-Meteo не ответил за установленное время
```

---

# 19. WeatherConnectionError

Используется для сетевых проблем:

```text
DNS
connection refused
network unreachable
```

---

# 20. WeatherResponseError

Используется при:

```text
HTTP 4xx
HTTP 5xx
invalid JSON
```

На этом уровне мы не пытаемся интерпретировать причины Open-Meteo.

---

# 21. WeatherDataError

Используется, если HTTP response технически успешен, но не содержит минимально необходимой структуры:

```text
нет current
нет current.time
неподдерживаемый формат time
```

---

# 22. Timeout

Фиксируем default:

```text
5 seconds
```

Конфигурация:

```text
WEATHER_API_TIMEOUT_SECONDS=5
```

Почему timeout обязателен:

```text
внешний сервис не должен бесконечно удерживать request PestWatch
```

Не используем HTTP request без timeout.

---

# 23. Retry

В EPIC-04:

```text
автоматический retry НЕ реализуем
```

Причины:

- усложняет поведение;
- увеличивает latency;
- требует отдельной retry policy;
- не нужен для MVP.

Retry может появиться позднее отдельным решением.

---

# 24. HTTP Library

Добавляем:

```text
requests
```

в:

```text
requirements.txt
```

Выбор:

```text
requests
```

потому что:

- API синхронный;
- Flask-приложение сейчас синхронное;
- integration простая;
- async infrastructure в MVP не требуется.

---

# 25. Configuration

В `Config`:

```text
WEATHER_API_BASE_URL
WEATHER_API_TIMEOUT_SECONDS
```

Default:

```text
WEATHER_API_BASE_URL=
https://api.open-meteo.com/v1/forecast

WEATHER_API_TIMEOUT_SECONDS=
5
```

`.env.example`:

```text
WEATHER_API_BASE_URL=https://api.open-meteo.com/v1/forecast
WEATHER_API_TIMEOUT_SECONDS=5
```

API key в текущем EPIC отсутствует.

---

# 26. Out of Scope

В EPIC-04 сознательно не входят:

- Risk Engine;
- Risk Calculators;
- пороговые правила;
- Degree Days;
- Threat-specific weather requirements;
- forecast UI;
- недельный прогноз;
- historical weather;
- Assessment;
- сохранение WeatherData в SQLite;
- weather cache;
- retries;
- circuit breaker;
- asynchronous HTTP;
- background jobs;
- multiple weather providers;
- automatic provider fallback;
- коммерческий Open-Meteo API;
- Weather API key;
- геокодирование названия города.

---

# 27. Геокодирование

Open-Meteo имеет отдельный Geocoding API, который умеет искать location по имени. :contentReference[oaicite:6]{index=6}

Но в EPIC-04 его **не подключаем**.

WeatherService принимает уже готовый:

```python
Location
```

с:

```text
latitude
longitude
```

То есть:

```text
"Москва"
→ coordinates
```

не является задачей Weather Integration данного EPIC.

---

# 28. TASKS

## TASK-04.01

Добавить:

```text
requests
```

в `requirements.txt`.

---

## TASK-04.02

Добавить Weather configuration:

```text
WEATHER_API_BASE_URL
WEATHER_API_TIMEOUT_SECONDS
```

---

## TASK-04.03

Создать integration exceptions.

---

## TASK-04.04

Создать `WeatherClient`.

---

## TASK-04.05

Реализовать query contract Open-Meteo.

---

## TASK-04.06

Реализовать timeout.

---

## TASK-04.07

Реализовать HTTP error handling.

---

## TASK-04.08

Создать `WeatherAdapter`.

---

## TASK-04.09

Реализовать mapping:

```text
Open-Meteo
→ WeatherData
```

---

## TASK-04.10

Реализовать missing-value handling.

---

## TASK-04.11

Реализовать `WeatherDataError`.

---

## TASK-04.12

Создать `WeatherService`.

---

## TASK-04.13

Покрыть WeatherClient unit tests.

---

## TASK-04.14

Покрыть WeatherAdapter unit tests.

---

## TASK-04.15

Покрыть WeatherService unit tests.

---

## TASK-04.16

Добавить integration test внешнего contract mapping без реального HTTP.

---

## TASK-04.17

Выполнить regression EPIC-01–03.

---

# 29. WeatherClient Test Scope

HTTP полностью mock/stub.

Ни один unit test не должен реально обращаться к:

```text
api.open-meteo.com
```

Проверить:

```text
correct URL
correct latitude
correct longitude
correct current variables
temperature_unit=celsius
wind_speed_unit=ms
precipitation_unit=mm
timezone=auto
timeout
```

---

# 30. Client Error Tests

Проверить:

```text
Timeout
→ WeatherTimeoutError
```

```text
ConnectionError
→ WeatherConnectionError
```

```text
HTTP 500
→ WeatherResponseError
```

```text
HTTP 400
→ WeatherResponseError
```

```text
invalid JSON
→ WeatherResponseError
```

---

# 31. Adapter Tests

Проверить полный payload:

```text
temperature_2m
relative_humidity_2m
precipitation
wind_speed_10m
soil_temperature_0cm
```

и результат:

```text
WeatherData
```

---

# 32. Missing Data Tests

Например payload:

```json
{
  "current": {
    "time": "2026-08-08T19:00",
    "temperature_2m": 18.4
  }
}
```

должен создать:

```text
temperature = 18.4
humidity = None
precipitation = None
wind_speed = None
soil_temperature = None
```

---

# 33. Zero Value Tests

Проверить:

```json
{
  "precipitation": 0.0,
  "wind_speed_10m": 0.0
}
```

результат:

```text
0.0
```

а не:

```text
None
```

---

# 34. Invalid Payload Tests

Проверить:

```text
{}
```

→ `WeatherDataError`

```json
{
  "current": {}
}
```

→ `WeatherDataError`

Некорректный:

```text
current.time
```

→ `WeatherDataError`

---

# 35. WeatherService Tests

Используем:

```text
FakeWeatherClient
FakeWeatherAdapter
```

или mocks.

Service unit test не должен:

```text
запускать Flask
создавать SQLite
вызывать интернет
```

Проверить:

```text
Location.coordinates
→ передаются client
```

и:

```text
client payload
→ передаётся adapter
```

и:

```text
adapter result
→ возвращается service
```

---

# 36. Real HTTP Tests

В обычном test suite:

```text
НЕ ДЕЛАЕМ
```

Причины:

- интернет может быть недоступен;
- API может временно не отвечать;
- response меняется со временем;
- тест становится nondeterministic;
- CI не должен зависеть от сторонней системы.

Реальный Open-Meteo request проверяем только отдельным manual smoke test.

---

# 37. Manual Smoke Test

После unit/integration tests допускается один ручной запрос через приложение или Python shell.

Пример location:

```text
Москва
55.7558
37.6173
```

Проверяем:

```text
response получен
WeatherData создан
temperature не None
observed_at установлен
```

Результат такого smoke test не становится unit-test assertion.

---

# 38. Security

В EPIC-04:

```text
секретов нет
```

поскольку Open-Meteo free API не использует key.

Но сохраняется правило:

```text
никаких credentials в Git
```

Если позднее появится API key:

```text
.env
```

и никогда:

```text
source code
```

---

# 39. Attribution

Open-Meteo требует attribution для распространяемых данных в рамках CC BY 4.0. :contentReference[oaicite:7]{index=7}

Поэтому в будущий пользовательский UI необходимо будет добавить указание источника погодных данных:

```text
Weather data: Open-Meteo
```

Ссылка/формат attribution будут оформлены на UI-этапе.

В EPIC-04 достаточно:

- зафиксировать requirement;
- добавить это в README/integration documentation при необходимости.

---

# 40. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-04-01 | Open-Meteo выбран как Weather Provider |
| AC-04-02 | WeatherClient реализован |
| AC-04-03 | WeatherAdapter реализован |
| AC-04-04 | WeatherService реализован |
| AC-04-05 | используется `Location.latitude` |
| AC-04-06 | используется `Location.longitude` |
| AC-04-07 | temperature mapping работает |
| AC-04-08 | humidity mapping работает |
| AC-04-09 | precipitation mapping работает |
| AC-04-10 | wind speed mapping работает |
| AC-04-11 | soil temperature mapping работает |
| AC-04-12 | observed_at mapping работает |
| AC-04-13 | wind приходит в m/s |
| AC-04-14 | precipitation приходит в mm |
| AC-04-15 | temperature приходит в °C |
| AC-04-16 | timezone=auto используется |
| AC-04-17 | missing values становятся `None` |
| AC-04-18 | zero не превращается в `None` |
| AC-04-19 | timeout настроен |
| AC-04-20 | timeout корректно обрабатывается |
| AC-04-21 | connection errors обрабатываются |
| AC-04-22 | HTTP errors обрабатываются |
| AC-04-23 | invalid JSON обрабатывается |
| AC-04-24 | invalid payload обрабатывается |
| AC-04-25 | unit tests не используют интернет |
| AC-04-26 | Service не знает структуру Open-Meteo JSON |
| AC-04-27 | Adapter не выполняет HTTP |
| AC-04-28 | Client не создаёт WeatherData |
| AC-04-29 | Domain не зависит от Open-Meteo |
| AC-04-30 | regression EPIC-01–03 проходит |

---

# 41. Architecture Review Checklist

Перед PR:

- [ ] Domain не импортирует `requests`;
- [ ] Domain не знает Open-Meteo;
- [ ] `WeatherClient` не создаёт `WeatherData`;
- [ ] `WeatherAdapter` не делает HTTP;
- [ ] `WeatherService` не анализирует JSON;
- [ ] Controller не добавлен без необходимости;
- [ ] SQLite не используется для WeatherData;
- [ ] timeout присутствует;
- [ ] API URL находится в config;
- [ ] отсутствует фиктивный API key;
- [ ] HTTP errors преобразуются в application-specific exceptions;
- [ ] missing values не преобразуются в zero;
- [ ] unit tests полностью deterministic;
- [ ] unit tests не требуют сети;
- [ ] Risk Engine не появился преждевременно;
- [ ] geocoding не появился преждевременно;
- [ ] attribution requirement зафиксирован.

---

# 42. PR Checklist

## Infrastructure

- [ ] `requests`;
- [ ] weather config;
- [ ] WeatherClient;
- [ ] integration exceptions.

## Mapping

- [ ] WeatherAdapter;
- [ ] complete payload;
- [ ] missing values;
- [ ] zero values;
- [ ] observed_at.

## Application

- [ ] WeatherService.

## Tests

- [ ] Client tests;
- [ ] Client error tests;
- [ ] Adapter tests;
- [ ] Service tests;
- [ ] full regression;
- [ ] manual smoke.

## Architecture

- [ ] Open-Meteo isolated inside integration layer;
- [ ] no Weather API dependency in Domain;
- [ ] no Risk calculation;
- [ ] no real HTTP in automated tests.

---

# 43. Definition of Done

EPIC-04 считается завершённым:

```text
Open-Meteo contract
        +
Weather Configuration
        +
WeatherClient
        +
Integration Exceptions
        +
WeatherAdapter
        +
WeatherService
        +
WeatherData Mapping
        +
Missing Data Handling
        +
Timeout Handling
        +
HTTP Error Handling
        +
Unit Tests without Internet
        +
Manual Smoke Test
        +
Regression EPIC-01–03
        +
Architecture Review
        ↓
READY FOR PR
```

---

# 44. После EPIC-04

После merge:

```text
EPIC-01 — Technical Foundation
        +
EPIC-02 — Domain Core
        +
EPIC-03 — Threat Catalog
        +
EPIC-04 — Weather Integration
```

И только после этого переходим к следующему этапу, где погодные данные смогут использоваться предметной логикой оценки риска.

Weather Integration сама:

```text
НЕ рассчитывает RiskLevel
НЕ определяет активность Threat
НЕ решает, достаточно ли данных для конкретного вида
```

Она отвечает только за:

```text
получить
→ проверить
→ преобразовать
→ вернуть WeatherData
```
