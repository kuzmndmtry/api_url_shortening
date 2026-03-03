# api_url_shortening
Домашнее задание: API-сервис сокращения ссылок.
# Описание API
### POST /links/shorten 
создает короткую ссылку: создает короткую ссылку, создает кастомную ссылку при передаче поля в теле запроса, если пользователь не авторизован создает ссылку со сроком жихни 30 дней, есть возможность указать время жизни самостоятельно.  
Истекшие ссылки удаляются автоматически.  
### GET /links/{short_code}
перенаправляет на оригинальный URL, обновляет счетчик переходов, кэширует ссылку, чистит кэш по ссылке, при вызову выставляет срок жизни в 30 дней. по истечении удаляется. 

### DELETE /links/{short_code}
удаляет запись о созданной ссылки из таблицы links. Доступна только для автозированного пользователя. 

### PUT /links/{short_code}
обновляет короткий код ссылки. чистит кэш по старому значению.  Доступна только для автозированного пользователя. 

### GET /links/{short_code}/stats 
отображает оригинальный URL, возвращает дату создания, количество переходов, дату последнего использовани.

### GET /links/search?original_url={url}
возвращает информацию по ссылке. Доступна только для автозированного пользователя. 

### POST /auth/register
всего лишь иммитация регистрациии

# Примеры запросов
### POST /links/shorten 
с передачей кастомной ссылки
```json
{
  "original_url": "https://example.com/",
  "custom_alias": "string",
  "expires_at": "2026-03-03T12:50:07.877Z"
}
```
без кастомной ссылки
```json
{
  "original_url": "https://example.com/",
  "expires_at": "2026-03-03T12:50:07.877Z"
}
```
без expires_at
```json
{
  "original_url": "https://example.com/",
  "expires_at": "2026-03-03T12:50:07.877Z"
}
```
Response body 200
```
{
  "short_code": "string"
}
```
Response body 400
```
{
  "detail": "alias alredy exists"
}
```
### GET /links/{short_code}
```
http://localhost:9999/links/493vvt
```
200 OK  
```
{
  "original_url": "https://example.com/"
}
```
### DELETE /links/{short_code}
```
curl -X 'DELETE' \
  'http://localhost:9999/links/493vvt' \
  -H 'accept: application/json' \
  -H 'X-User-ID: 1'
  ```
  200 OK
   ```
{
  "detail": "success!"
}
 ```

### PUT /links/{short_code}
 ```
curl -X 'PUT' \
  'http://localhost:9999/links/kpy0kZ' \
  -H 'accept: application/json' \
  -H 'X-User-ID: 1'
 ```
200 OK
  ```
  {
  "short_code": "xbO4fy"
}
 ```

### GET /links/{short_code}/stats 
 ```
http://localhost:9999/links/xbO4fy/stats
 ```
200 ok
 ```
{
  "original_url": "https://example.com/",
  "created_date": "2026-03-03T13:06:32.287217+00:00",
  "count_clicks": 0,
  "date_last_click": null
}
 ```

### GET /links/search?original_url={url}
```
http://localhost:9999/links/search?original_url=https%3A%2F%2Fexample.com%2F
```
Response body 200 
```
{
  "original_url": "https://example.com/",
  "short_code": "493vvt",
  "created_date": "2026-03-03T13:01:22.692312+00:00",
  "count_clicks": 0,
  "date_last_click": null
}
```
Error: Not Found 404
```
{
  "detail": "not found"
}
```
### POST /auth/register
Response body
```json
{
  "username": "test",
  "password": "test"
}
```
Successful Response 200 
``` 
{
  "id": 1,
  "username": "test"
}
```
Error: Bad Request 400
``` 
{
  "detail": "Username already registered"
}

```

# Инструкцию по запуску
# Описание БД.
### USERS
* id
* username - логин
* password - пароль
### USERS
* id  - ид записи
* original_url - оригинальная ссылка
* short_code  - короткий код
* owner_id - ид пользователя, связь с user.id
* created_date - дата создания
* expires_at - срок жизни ссылки, после истечения удаляется
* count_clicks - кол-во переходов
* date_last_click - дата последнего перехода

