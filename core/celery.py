import os
from celery import Celery
from kombu import Queue

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Filas
app.conf.task_queues = (
    Queue("fila_rapida", routing_key="rapida.#"),
    Queue("fila_pesada", routing_key="pesada.#"),
    Queue("fila_media", routing_key="media.#"),
)

# Defaults 
app.conf.task_default_queue = "fila_rapida"
app.conf.task_default_exchange = "default"
app.conf.task_default_routing_key = "rapida.default"

# Rotas
app.conf.task_routes = { 
    "smartcard.tasks.processar_xls": {"queue": "fila_pesada"},
    "smartcard.tasks.tentar_vincular_user_auth": {"queue": "fila_rapida"},
    "smartcard.tasks.tentar_vincular_por_nome": {"queue": "fila_media"},
}