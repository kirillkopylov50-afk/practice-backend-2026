$content = @"
# API Endpoints Documentation

## Base URL
http://localhost:5000/api

## Authentication
Все защищённые эндпоинты требуют заголовок:
Authorization: Bearer <JWT_TOKEN>

---

## Auth (Аутентификация)

### POST /auth/register
Регистрация нового пользователя.
- Тело: { "email": "...", "password": "...", "full_name": "...", "role": "user" }
- Ответ: 201 Created — { "user_id": 1, "token": "..." }
- Ошибки: 400 (невалидные данные), 409 (email занят)

### POST /auth/login
Вход в систему.
- Тело: { "email": "...", "password": "..." }
- Ответ: 200 OK — { "token": "...", "user": {...} }
- Ошибки: 401 Unauthorized

---

##  Resources (Рабочие места)

### GET /resources
Список всех ресурсов с фильтрацией.
- Параметры: ?type=desk&floor=2&capacity=1
- Ответ: 200 OK — [ {...}, {...} ]
- Доступ: Авторизованный пользователь

### GET /resources/{id}
Детали конкретного ресурса.
- Ответ: 200 OK — { "id": 1, "name": "...", "avg_rating": 4.5 }
- Ошибки: 404 Not Found

### POST /resources
Создать новый ресурс.
- Доступ: Только Admin
- Тело: { "name": "...", "type": "cabin", "capacity": 4, "floor": 3 }
- Ответ: 201 Created
- Ошибки: 403 Forbidden (не админ)

### PUT /resources/{id}
Обновить ресурс.
- Доступ: Только Admin
- Ответ: 200 OK

### DELETE /resources/{id}
Удалить ресурс.
- Доступ: Только Admin
- Ответ: 204 No Content

---

## Bookings (Бронирования)

### GET /bookings
Список бронирований.
- Логика: User видит свои, Admin видит все.
- Параметры: ?status=active&start_date=2026-04-01
- Ответ: 200 OK — [ {...} ]

### POST /bookings
Создать бронирование.
- Тело: { "resource_id": 1, "start_time": "2026-04-01T10:00:00", "end_time": "2026-04-01T12:00:00" }
- Валидация: Проверка на пересечение времени!
- Ответ: 201 Created
- Ошибки: 409 Conflict (время занято), 400 Bad Request

### DELETE /bookings/{id}
Отменить бронирование.
- Логика: User отменяет своё, Admin — любое.
- Ответ: 204 No Content
- Ошибки: 403 Forbidden

---

## Schedule (Расписание)

### GET /resources/{id}/schedule
Расписание ресурса на дату.
- Параметры: ?date=2026-04-01 (обязательно)
- Ответ: 200 OK — { "resource_id": 1, "date": "...", "slots": [...] }

---

## Reviews (Отзывы)

### POST /reviews
Оставить отзыв.
- Тело: { "booking_id": 1, "rating": 5, "comment": "..." }
- Валидация: Бронь должна быть завершена (end_time < now).
- Ответ: 201 Created
- Ошибки: 400 (бронь активна), 409 (уже есть отзыв)

### GET /resources/{id}/reviews
Отзывы о ресурсе.
- Ответ: 200 OK — [ {...} ]

---

## Коды ответов

| Код | Значение | Описание |
|-----|----------|----------|
| 200 | OK | Успех |
| 201 | Created | Создано |
| 204 | No Content | Успешно удалено |
| 400 | Bad Request | Ошибка данных |
| 401 | Unauthorized | Нет токена |
| 403 | Forbidden | Нет прав |
| 404 | Not Found | Не найдено |
| 409 | Conflict | Конфликт (занято) |
"@

Set-Content -Path "docs/api-endpoints.md" -Value $content -Encoding UTF8