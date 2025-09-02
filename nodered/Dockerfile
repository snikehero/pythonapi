# nodered/Dockerfile
FROM nodered/node-red:latest

# Instalar nodos como usuario node-red (recomendado)
USER node-red
RUN npm install --unsafe-perm --no-update-notifier --no-fund --omit=dev \
    node-red-contrib-s7 \
    @mindconnect/node-red-contrib-mindconnect
