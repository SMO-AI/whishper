# Руководство по решению ошибки 404 (Not Found) после деплоя

Эта ошибка («Not Found. The requested URL was not found on the server...») возникает, когда **Traefik** (маршрутизатор Coolify) ошибочно направляет трафик на контейнер `translate` (LibreTranslate) вместо основного контейнера `whishper` (Nginx).

## Причина
Контейнер `translate` использует Python/Gunicorn, который выдает именно такое текстовое сообщение об ошибке. Трафик уходит туда, потому что оба контейнера находятся в одном стеке, и Traefik иногда выбирает первый попавшийся контейнер с открытым портом, если маршрутизация не прописана жестко.

## Решение (Шаги для исправления раз и навсегда)

### 1. Конфигурация Docker Compose
Убедитесь, что в файле `docker-compose.yaml` для сервиса `whishper` прописаны следующие метки (labels). Они принудительно говорят Traefik, что этот домен принадлежит этому контейнеру и должен идти на порт 80:

```yaml
    labels:
      - "coolify.managed=true"
      - "traefik.enable=true"
      # Привязываем домены к роутеру 'whishper-main'
      - "traefik.http.routers.whishper-main.rule=Host(`scriptus.online`) || Host(`www.scriptus.online`)"
      - "traefik.http.routers.whishper-main.entrypoints=web,websecure"
      - "traefik.http.routers.whishper-main.tls=true"
      - "traefik.http.routers.whishper-main.tls.certresolver=letsencrypt"
      # Ставим высокий приоритет (важно!), чтобы Whishper выигрывал у других сервисов
      - "traefik.http.routers.whishper-main.priority=10000"
      # Явно указываем внутренний порт контейнера
      - "traefik.http.services.whishper-main.loadbalancer.server.port=80"
```

Для всех остальных сервисов (`mongo`, `translate`) **ОБЯЗАТЕЛЬНО** должно быть:
```yaml
    labels:
      - "coolify.managed=true"
      - "traefik.enable=false" # Это исключает их из внешней маршрутизации
```

### 2. Настройки в панели Coolify (UI)
Иногда Coolify переопределяет настройки из файла. Проверьте следующее:
1.  **Service -> Whisper -> Settings**:
    *   В поле **Domains** должно быть: `https://scriptus.online`
    *   **Container Port**: Обязательно укажите `80`. Если там пусто или стоит другой порт, Coolify может выбрать порт переводчика (5000).
2.  **Health-checks**:
    *   Убедитесь, что проверка работоспособности (Health-check) проходит успешно для порта 80. Если контейнер считается «больным», Traefik перестанет слать на него трафик и переключится на другой доступный контейнер.

### 3. Порты в Dockerfile
В `Dockerfile` должна быть только одна инструкция EXPOSE:
```dockerfile
EXPOSE 80
```
(Порты 3000, 8080 и 5000 не должны быть открыты наружу, так как они обрабатываются Nginx внутри контейнера).

## Как проверить, что всё работает правильно?
Я добавил специальный заголовок в Nginx. Откройте сайт, нажмите **F12 -> Network**, выберите главный запрос и найдите в **Response Headers**:
*   `X-Served-By: Whishper-Nginx` — если этот заголовок есть, значит запрос дошел до нужного места.
*   `Server: gunicorn` — если вы видите это, значит вы всё еще попадаете на переводчик (ошибка!).

## Если ошибка повторилась
Если вы нажали "Redeploy" и снова видите 404:
1.  Зайдите в Coolify, выключите сервис (Stop).
2.  Удалите домен из настроек и добавьте его заново, указав порт `80`.
3.  Нажмите Deploy.
