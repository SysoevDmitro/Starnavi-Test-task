from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'post_backend.settings')

# Создаем экземпляр приложения Celery
app = Celery('post_backend', )

# Загружаем конфигурацию Celery из настроек Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживаем задачи, определенные в каждом приложении Django
app.autodiscover_tasks()
