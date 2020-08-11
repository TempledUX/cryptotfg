# cryptotfg
Scripts de código Python que describen los programas desarrollados durante mi investigación y realización del TFG. A continuación se detallan los objetivos y funcionamiento de cada uno de ellos:

### eccpf
Implementación de un protocolo de cifrado/descifrado de datos (ElGamal) sobre una curva elíptica extremadamente sencilla, su objetivo es mostrar como se lleva a cabo el proceso de cifrado de la información sobre una curva elíptica cualquiera.

### ecc
Implementa el mismo protocolo de cifrado/descifrado anterior pero sobre una curva elíptica segura (secp256k1), el script genera así mismo una tabla de correspondencias Unicode para soportar el intercambio de información entre los datos y los puntos de la curva.

### cryptoGPS
Describe de manera práctica el protocolo *cryptoGPS* que permite la autenticación de un satélite por parte de un usuario terrestre.
