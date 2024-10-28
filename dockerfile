FROM python:latest

WORKDIR /ORDEMDESERVICO

RUN pip install --no-cache-dir fastapi uvicorn

COPY . /ORDEMDESERVICO/

EXPOSE 8000


CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]