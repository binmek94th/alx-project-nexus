FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements-docker.txt .
RUN pip install --upgrade pip && pip install -v -r requirements-docker.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["uvicorn", "alx_project_nexus.wsgi:application", "--host 0.0.0.0" "--port 8000"]