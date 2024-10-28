FROM python:latest

WORKDIR /ORDEMDESERVICO

# Copia o arquivo requirements.txt e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todos os arquivos para o contêiner
COPY . .

# Expõe a porta 8000 para a aplicação FastAPI
EXPOSE 8000

# Comando para iniciar o servidor
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
