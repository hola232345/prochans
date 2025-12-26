Prochans - Selección de Proxies SOCKS Anónimos

Este script permite descargar, filtrar y probar proxies SOCKS4 y SOCKS5 de manera automática, priorizando los que sean anónimos y estén ubicados en Norteamérica (EE. UU. y Canadá). Además, mide la latencia de cada proxy para seleccionar los más rápidos.

Cómo funciona

Fuentes de proxies
El script define listas de URLs que contienen proxies SOCKS4 y SOCKS5. Se descargan todas las direcciones y se filtran para eliminar duplicados.

Filtrado geográfico
Se consulta la API http://ip-api.com/json/ para determinar el país del proxy. Solo se permiten proxies de EE. UU. y Canadá.

Verificación de anonimato
Cada proxy se prueba para determinar si es anónimo. Esto se hace estableciendo el proxy con la librería socks y verificando la dirección IP de salida mediante https://api.ipify.org.

Medición de latencia
Se realiza un test de conexión rápida a 1.1.1.1 para medir el tiempo de respuesta del proxy en milisegundos. Esto permite ordenar los proxies según rapidez.

Selección de proxies
Se mezclan todas las listas de proxies y se prueban uno a uno hasta encontrar los 5 proxies anónimos más rápidos. Se muestra un resumen final ordenado por latencia.

Uso

Ejecuta el script directamente en Linux o cualquier sistema compatible con Python:

python prochans.py


El script imprimirá información en la terminal, resaltando los proxies válidos en color verde:

[OK] SOCKS5 123.45.67.89:1080 | US | 250.34 ms


Al final, mostrará un listado con los 5 mejores proxies anónimos.

Requisitos

Python 3.x

Librerías: requests, socks
Puedes instalarlas con:

pip install requests pysocks

Notas

Se deshabilita temporalmente el socket original para poder enrutar el tráfico a través de los proxies.

El script está pensado para uso ético y pruebas de conectividad. No se recomienda su uso para fines maliciosos.

Solo se usan proxies de EE. UU. y Canadá, pero puedes modificar ALLOWED_COUNTRIES para otros países.
