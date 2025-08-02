FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy the entrypoint script
COPY entrypoint.sh /app/entrypoint.sh

# Make it executable
RUN chmod +x /app/entrypoint.sh

WORKDIR /app

COPY requirements-docker.txt .
RUN pip install --upgrade pip && pip install -v -r requirements-docker.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "alx_project_nexus.wsgi:application", "--bind", "0.0.0.0:8000"]