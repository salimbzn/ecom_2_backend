@echo off

echo Running migrations and starting Django server...
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

echo Done!
pause  
