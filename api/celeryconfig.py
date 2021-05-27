import os

result_backend = "mongodb"

mongodb_backend_settings = {
    "host": os.getenv('CELERY_BACKEND', "127.0.0.1"),
    "port": 27017,
    "database": "orxa_jobs", 
    "taskmeta_collection": "orxa_taskmeta_collection",
}

