migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

run:
	python manage.py runserver

superuser:
	python manage.py createsuperuser