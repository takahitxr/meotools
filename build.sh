#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Convert static asset files
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate --verbosity 3  # マイグレーションの詳細なログを出力
echo "Migrations completed."

gunicorn google_question.asgi:application -k uvicorn.workers.UvicornWorker