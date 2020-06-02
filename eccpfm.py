import random
from ecpy.curves import WeierstrassCurve, Point

#Parámetros de la curva
a = 7
b = 3
fp = 13
curva_exp = '(y**2)%(fp) == (x**3+a*x+b)%(fp)'
curva = WeierstrassCurve({'name':'curva', 'type':'weierstrass', 'size':1000, 'a':a, 'b':b, 'field':fp, 'generator':(0,4), 'order':fp, 'cofactor':1})

def cords(punto):
    if punto == Point.infinity():
        return (0,0)
    return (punto.x, punto.y)

def computarPuntos(fp,a,b):
    """
    Calcula los puntos racionales de una curva elíptica dada en forma de Weierstrass reducida sobre un cuerpo primo Fp
    curva = {y^2 = x^3 + ax + b}
    """
    field = [x for x in range(fp)]
    points = []
    for x in field:
        for y in field:
            if eval(curva_exp):
                points.append(Point(x,y,curva))
    return points

def cifrar(base,punto,pubkey):
    """
    Función de cifrado según ElGamal
    base -> punto generador elegido
    punto -> punto a cifrar
    pubkey -> clave pública del receptor
    Devuelve una tupla de datos (x,y)
    """
    print("Cifrando punto: {}".format(cords(punto)))
    k = random.randint(2,fp-3)
    print("Parámetros de cifrado: k = {}, pubkey={}".format(k,cords(pubkey)))
    x = k*base
    z = k*pubkey
    y = punto + z
    print("Datos cifrados: {}".format((cords(x),cords(y))))
    return (x,y)

def descifrar(data,privkey):
    """
    Función de descifrado según ElGamal
    data=(x,y) -> pareja de datos para el descifrado
    privkey -> clave privada del receptor
    Devuelve una tupla de datos (x,y) (punto descifrado)
    """
    q = privkey*data[0]
    z = q.neg()
    return data[1] + z

descodificar = {(0,4):'m',(0,9):'e',(2,5):'n',(2,8):'s',(3,5):'a',(3,8):'j',
    (4,2):'x',(4,11):'l',(6,1):'k',(6,12):'w',(8,5):'r',(8,8):'t',(0,0):'y'}
codificar = {'m':(0,4),'e':(0,9),'n':(2,5),'s':(2,8),'a':(3,5),'j':(3,8),
    'x':(4,2),'l':(4,11),'k':(6,1),'w':(6,12),'r':(8,5),'t':(8,8),'y':(0,0)}

puntos = computarPuntos(fp,a,b)
puntos.insert(0,Point.infinity())

if __name__ == "__main__":
    #Secuencia principal de órdenes
    mensaje = "mensaje"
    print("Puntos de la curva: {}".format([cords(p) for p in puntos]))
    g = Point(0,4,curva)
    kb = 11
    pb = 11*g
    print("Punto generador G = {}".format(cords(g)))
    geng = [Point.infinity(),g]
    for k in range(fp):
        if k==0 or k==1: continue
        geng.append(k*g)
    print("Puntos generados por G: {}".format([cords(p) for p in geng]))
    print("\nCifrado:")
    data = []
    for char in mensaje:
        datablob = cifrar(g,Point(*codificar[char],curva),pb)
        data.append(datablob)
    print("Enviamos los datos a B y desciframos...\n")
    desmsg = []
    for datablob in data:
        pchar = descifrar(datablob,kb)
        desmsg.append(descodificar[cords(pchar)])
    print("Mensaje descifrado: {}".format(''.join(desmsg)))