FROM python:latest

# Define o diretório de trabalho
WORKDIR /ORDEMDESERVICO

# Copia o arquivo de dependências para o contêiner
COPY requirements.txt .

# Atualiza o pip e instala as dependências
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia o restante dos arquivos para o contêiner
COPY . .

# Expõe a porta 8000 para o servidor FastAPI
EXPOSE 8000

# Comando para iniciar o servidor
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
