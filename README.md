## Описание
Очень не хотелось делать 2 проекта, т.к. основная логика (изменение пинга) очень небольшая,
поэтому поптылася сделать все в рамках одного проекта, который конфигурируется нужными параметрами при запуске.
Детальнее можно посмотреть в docker-compose.yml.
Тесты хотел бы написать, но тут даже не на что :)
Для запуска необходимо запустить контейнеры docker-compose up --build, после этого отправить POST-запрос на 
digits-сервис (во время проверки я дергал прямо из документации Try it out - http://0.0.0.0:8081/docs#/default/partial_ping_post),
после этого запустится цепочка запросов, если первый же запрос не окажется невалдиным.
До этого с fastAPI не работал, не исключаю, что какие-то вещи сделаны не в его стиле.
## Отладка
Для отладки сложных случаев я бы добавил в каждый запрос UUID и timestamp запроса. UUID был бы сквозным идентификатором 
во всех API, timestamp позволил бы понять хронологию событий и скорость ответа/обработки запросов. При этом запрос 
логировал бы (как и сейчас) с нужной точностью, чтобы не переусердствовать.
В текущей реализации делать не стал, т.к. тестировал только один сеанс пинг-понгов, перемешивания разных запросов нет,
текущей детализации логов достаточно.