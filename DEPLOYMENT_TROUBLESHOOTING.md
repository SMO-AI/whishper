# Инструкция по настройке конфигурации для Coolify и Traefik

Эта инструкция описывает критически важные аспекты настройки `docker-compose.yaml` для корректной работы приложения в инфраструктуре Coolify с балансировщиком Traefik. Нарушение этих правил может привести к ошибкам 503 (Service Unavailable) или проблемам с SSL.

## 1. Точки входа (Entrypoints) в Traefik

Одной из самых частых проблем при переезде на Coolify (особенно бета-версий 4.x) является смена названий стандартных точек входа.

### Проблема
Стандартный Traefik использует `web` для HTTP и `websecure` для HTTPS.
Однако, Coolify часто переопределяет их как `http` и `https`.
Использование старых названий (`web`/`websecure`) приводит к ошибкам вида:
`ERR EntryPoint doesn't exist entryPointName=websecure`

### Правильная конфигурация (Labels)
В `docker-compose.yaml` в секции `services -> scriptus-app -> labels` используйте следующие названия:

```yaml
    labels:
      - "coolify.managed=true"
      - "traefik.enable=true"
      
      # === HTTPS Router ===
      - "traefik.http.routers.scriptus-app.rule=Host(`scriptus.online`) || Host(`www.scriptus.online`)"
      # Используем точку входа 'https' (вместо websecure)
      - "traefik.http.routers.scriptus-app.entrypoints=https"
      - "traefik.http.routers.scriptus-app.priority=10000"
      - "traefik.http.routers.scriptus-app.tls=true"
      - "traefik.http.routers.scriptus-app.tls.certresolver=letsencrypt"

      # === HTTP Router (Redirect) ===
      - "traefik.http.routers.scriptus-app-http.rule=Host(`scriptus.online`) || Host(`www.scriptus.online`)"
      # Используем точку входа 'http' (вместо web)
      - "traefik.http.routers.scriptus-app-http.entrypoints=http"
      - "traefik.http.routers.scriptus-app-http.priority=10000"
      
      # === Port ===
      - "traefik.http.services.scriptus-app.loadbalancer.server.port=80"
```

## 2. Healthcheck (Проверка здоровья)

Приложение является "тяжелым" (в одном контейнере запускаются Nginx, Node.js, Go Backend, Python Transcription). Стандартное время запуска может превышать 15-30 секунд.

Если Traefik не получает успешный ответ от Healthcheck, он помечает сервис как "мертвый" (503 Service Unavailable).

### Оптимальная конфигурация
В `docker-compose.yaml` установите следующие параметры:

```yaml
    healthcheck:
      # Используем curl с флагом -4 (IPv4 only) и fail-silent
      test: [ "CMD-SHELL", "curl -4 -f -s -o /dev/null http://127.0.0.1/health-check || exit 1" ]
      interval: 5s       # Проверять часто
      timeout: 5s        # Тайм-аут запроса
      retries: 10        # Количество попыток (10 * 5s = 50s дополнительного ожидания)
      start_period: 60s  # Дать приложению целую минуту на первый запуск без проверок!
```

**Почему `start_period: 60s` важен?**
Docker пропустит все неудачные проверки здоровья в течение первой минуты. Это критично при "холодном" старте с загрузкой AI-моделей.

## 3. Внутренняя связь сервисов

Чтобы избежать циклических зависимостей внутри контейнера, сервисы должны общаться напрямую по localhost, минуя Nginx там, где это возможно.

В `docker-compose.yaml`:
```yaml
    environment:
      # Прямое указание на порт Go-сервера (8080) внутри контейнера
      PUBLIC_INTERNAL_API_HOST: "http://127.0.0.1:8080"
```
Это исключает ситуацию, когда Node.js пытается достучаться до Backend через Nginx, который еще не готов.

## Шпаргалка для отладки

Если сайт не работает после деплоя, выполните диагностику на сервере:

1. **Проверка статуса контейнера:**
   `docker ps | grep scriptus`
   *Должен быть статус `(healthy)`. Если `(unhealthy)` или `(starting)` — ждите.*

2. **Проверка логов прокси (Traefik):**
   `docker logs --tail 50 coolify-proxy`
   *Ищите ошибки `EntryPoint doesn't exist` или `Unable to obtain ACME certificate`.*

3. **Локальный запрос внутри сервера:**
   `curl -v http://127.0.0.1/health-check`
   *Должен вернуть `200 OK`.*
