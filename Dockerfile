
# Imagen base
FROM python:3.10

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiar dependencias primero (optimiza build)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el backend
COPY . .
# Exponer puerto
EXPOSE 5000

# Comando para ejecutar la app
CMD ["python", "backend/app.py"]