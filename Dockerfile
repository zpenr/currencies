FROM python:3.12-alpine
WORKDIR /project
COPY . .
CMD ["python", "main.py"]