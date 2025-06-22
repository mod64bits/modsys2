# Usar uma imagem oficial do Python
FROM python:3.12-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Definir o diretório de trabalho dentro do contentor
WORKDIR /app

# Instalar dependências do sistema, se necessário
# RUN apt-get update && apt-get install -y ...

# Copiar o ficheiro de requisitos e instalar as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código do projeto
COPY . .

# Copiar o script de entrypoint e dar-lhe permissões de execução
COPY ./entrypoint.sh .
RUN chmod +x /app/entrypoint.sh

# A porta que o Gunicorn irá usar já é exposta no docker-compose
# O CMD é substituído pelo entrypoint

# Definir o entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
