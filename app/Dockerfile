FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencies first, so this layer is cached until requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY train.py main.py ./
# Train inside the image so the model matches the pinned scikit-learn version
RUN python train.py

# Run as a non-root user
RUN useradd --uid 10001 --no-create-home appuser && chown -R appuser /app
USER 10001

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
