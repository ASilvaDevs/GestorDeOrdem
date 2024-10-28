FROM python:latest

WORKDIR /ORDEMDESERVICO

# Copia o arquivo requirements.txt para o contêiner e instala os pacotes listados
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todos os arquivos para o diretório de trabalho no contêiner
COPY . .

# Expõe a porta para o servidor FastAPI
EXPOSE 8000

# Comando para iniciar o servidor
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
