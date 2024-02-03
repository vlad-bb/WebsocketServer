# Робота з Docker

1. Створення image
   ```docker build . -t antonbabenko1983/hw_05_linux:0.0.1```
2. Завантаження image в docker hub
   ```docker push antonbabenko1983/hw_05_linux:0.0.1```
3. Скачування image з docker hub на linux server
   ```docker pull antonbabenko1983/hw_05_linux:0.0.1```
4. Запускаємо docker контейнер на сервері
   ```docker run --name hw5_serg -p 8080:8080 antonbabenko1983/hw_05_linux:0.0.1```
