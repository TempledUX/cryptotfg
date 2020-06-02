import hashlib
import hmac
import random
from ecpy.curves import Point, WeierstrassCurve
from eccpf import descodificar

def sha256(mensaje):
    """
    Devuelve el hash según la función sha256 de un
    mensaje representado por una cadena de caracteres
    """
    try:
        mensaje = mensaje.encode('utf-8')
        return hashlib.sha256(mensaje).hexdigest()
    except AttributeError:
        print("Ocurrió un error al calcular el hash.")

def hmac_sha256(clave, mensaje):
    """
    Devuelve el HMAC basado en sha256 de cierto mensaje
    utilizando la clave especificada
    """
    try:
        clave = clave.encode('utf-8')
    except AttributeError:
        pass
    try:
        mensaje = mensaje.encode('utf-8')
    except AttributeError:
        print("Ocurrió un error al calcular el HMAC del mensaje proporcionado.")
        return
    return hmac.new(bytes(clave), mensaje, hashlib.sha256).hexdigest()

def cords(punto):
    return (punto.x, punto.y)

clave = 1011
curva = WeierstrassCurve({'name':'curva', 'type':'weierstrass', 'size':1000, 'a':7, 'b':3, 'field':13, 'generator':(0,4), 'order':13, 'cofactor':1})
P = Point(0,4,curva)

print("Cálculo de los cupones:")
cupones = []
for i in [5,19]:
    print()
    fki = hmac_sha256(clave, str(i))
    fki = int(fki, base=16)
    print(f'Resultado de la función pseudoaleatoria = {fki}')
    np = fki * P
    print(f'Coordenadas del nuevo punto = {cords(np)}')
    cod = descodificar[cords(np)]
    print(f'Descodificación del nuevo punto = {cod}')
    digest = sha256(cod)
    print(f'Valor del cupón = {digest}')
    cupones.append(digest)
print()

x1 = cupones[0]
s = 6
delta = 4
V = -s*P
print(f'Clave pública del satélite: {cords(V)}')

#Describimos a continuación el proceso del protocolo cryptoGPS:

##1
#El satélite envía el cupón x1 al usuario terrestre.

##2
#El usuario terrestre recibe el cupón y 
#genera un número aleatorio 0 <= c <= 2^delta - 1.
c = random.randint(0,2**delta-1)
print(f'c = {c}')

##3
#El satélite recibe c, comprueba su tamaño y realiza el siguiente cálculo:
ri = hmac_sha256(clave, str(5))
ri = int(ri, base=16)
y = ri + s*c
#El satélite envía el valor y al usuario terrestre.

##4
#El usuario terrestre comprueba la identidad del satélite
#realizando lo siguiente:
new_point = y*P + c*V
msg = descodificar[cords(new_point)]
test = sha256(msg)
if test == x1:
    print("Identidad verificada.")
else:
    print("La identidad no se puede verificar.")