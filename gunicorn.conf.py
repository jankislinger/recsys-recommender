import os

bind = os.getenv("BIND", "0.0.0.0:8000")
workers = 1  # to share the updated set of items
worker_class = "uvicorn.workers.UvicornWorker"
threads = int(os.getenv("THREADS", "1"))

# Sensible defaults; adjust as needed
timeout = int(os.getenv("TIMEOUT", "30"))
graceful_timeout = int(os.getenv("GRACEFUL_TIMEOUT", "30"))
keepalive = int(os.getenv("KEEPALIVE", "5"))
loglevel = os.getenv("LOGLEVEL", "info")
accesslog = "-"  # stdout
errorlog = "-"  # stderr
