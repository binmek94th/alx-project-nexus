# 📧 Notifications Subapp

This Django sub-application handles **sending emails and notifications** using Celery, Redis, and Django templates. It provides a centralized service for sending various types of emails (e.g., welcome emails, password resets), rate-limits email sends per user, and supports asynchronous task processing via Celery.

---

## 📦 Features

- ✅ Asynchronous email sending via Celery
- ✅ Email templating with HTML and plain text fallback
- ✅ Rate limiting with Redis per user and email type
- ✅ Centralized email types and templates
- ✅ Validated inputs using DRF serializer

---

## 🧱 Folder Structure
- init.py
- email_services.py
- tasks.py
- serializers.py
- templates/
  - email/
    - welcome_email.html
    - password_reset_email.html
- urls.py
- views.py
- models.py

## 🛠 Dependencies

- Django
- Celery
- Redis
- Django REST Framework
- SMTP (configured with Gmail or any provider)

---

## ⚙️ Configuration

Add the following to your `settings.py`:

```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587  # or 465 if using SSL
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
EMAIL_USE_TLS = True

EMAIL_RATE_LIMIT_MAX = 5          # Max emails allowed in window
EMAIL_RATE_LIMIT_WINDOW = 300     # Time window in seconds (e.g. 5 minutes)
FRONTEND_URL = "https://your-frontend.com"
CELERY_BROKER_URL = "amqp://guest:guest@localhost:5672//"
```
```bash
# start rabbitmq
docker run -d --hostname rabbitmq --name rabbitmq -p 5672:5672

# Start Celery
celery -A your_project_name worker --loglevel=info
```

## 🛡️ Error Handling
- If the template is not found → Raises ValidationError

- If rate limit exceeded → Raises ValidationError

- SMTP errors are logged inside the task, allowing Celery retries or alerts