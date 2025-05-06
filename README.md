# nbrbAPI

branch app-docker:
  - Создайте папку mkdir examplefolder и перейдите cd examplefolder
  - Скопируйте в папку ветку app-docker git clone -b app-docker https://github.com/PoltosSVA/nbrbAPI.git затем cd nbrbAPI
  - Создайте .env файл echo -e "POSTGRES_DB=mydb\nPOSTGRES_USER=myuser\nPOSTGRES_PASSWORD=mypassword\nPOSTGRES_HOST=db\nPOSTGRES_PORT=5432" > .env
  - docker compose up
  - В браузере перейдите по http://localhost:8000/
  - docker compose down --volumes остановит и удалит контейнеры, а также удалит неименованный volume
