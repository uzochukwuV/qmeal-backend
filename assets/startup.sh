#!/bin/bash
set -e
#!/bin/bash
set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting application with Uvicorn worker..."
gunicorn --bind 0.0.0.0:8000 --workers 2 --worker-class uvicorn.workers.UvicornWorker --timeout 120 server:app