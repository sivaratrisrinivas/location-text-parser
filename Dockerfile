FROM python:3.12-slim
WORKDIR /app
COPY locparse locparse
COPY evals evals
COPY data data
COPY web web
ENV PORT=8000
CMD ["python", "web/server.py"]
