FROM odoo:17.0

LABEL maintainer="your-email@example.com"

# Cambiar a usuario root para instalar dependencias
USER root

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    python3-pip \
    build-essential \
    python3-dev \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Actualizar pip e instalar las dependencias una por una
RUN pip3 install --no-cache-dir --upgrade pip

# Instalar cada dependencia por separado para mejor control de errores
RUN pip3 install --no-cache-dir Pillow==10.1.0
RUN pip3 install --no-cache-dir requests==2.31.0
RUN pip3 install --no-cache-dir --ignore-installed PyPDF2==3.0.1
RUN pip3 install --no-cache-dir fitz
RUN pip3 install --no-cache-dir PyMuPDF==1.23.8
RUN pip3 install --no-cache-dir openai==1.12.0

# Verificar cada instalación por separado
RUN python3 -c "import PIL" && \
    python3 -c "import requests" && \
    python3 -c "import PyPDF2" && \
    python3 -c "import fitz" && \
    python3 -c "import openai" && \
    echo "All dependencies installed successfully"

# Copia el archivo de configuración en la imagen
COPY ./odoo.conf /etc/odoo/

# Crea un directorio para los addons personalizados si no existe
RUN mkdir -p /mnt/extra-addons

# Copia los addons personalizados en el directorio de la imagen
COPY --chown=odoo:odoo ./custom_addons /mnt/extra-addons

# Volver al usuario odoo para mayor seguridad
USER odoo

# Expone el puerto 8069
EXPOSE 8069

CMD ["odoo"]