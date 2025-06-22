#!/bin/sh

# Recolhe todos os ficheiros estáticos para a pasta STATIC_ROOT
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Aplica as migrações da base de dados
echo "Applying database migrations..."
python manage.py migrate

# Inicia o servidor Gunicorn
# O comando 'exec' é importante para que o Gunicorn se torne o processo principal (PID 1)
# e possa receber sinais do Docker para um encerramento gracioso.
echo "Starting Gunicorn..."
exec gunicorn ticket_project.wsgi:application --bind 0.0.0.0:8000