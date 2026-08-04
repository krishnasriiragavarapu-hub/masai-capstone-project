FROM python:3.10-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn pydantic chromadb sentence-transformers
COPY . /app
EXPOSE 7860
CMD ["uvicorn", "main :app", "--host","0.0.0.0", "--port", "7860"]
