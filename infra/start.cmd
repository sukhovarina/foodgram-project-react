docker-compose down
docker-compose up -d --build
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --no-input
docker-compose exec web python manage.py load_ingredients
docker-compose exec web python manage.py load_tags