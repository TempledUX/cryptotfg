import random

#Parámetros de la curva
a = 7
b = 3
fp = 13
curva = '(y**2)%(fp) == (x**3+a*x+b)%(fp)'

def egcd(a, b):
    """
    Algoritmo de euclides extendido
    """
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    """
    Calcula el inverso de a modulo m
    """
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('El inverso no existe.')
    else:
        return x % m

def sumarPuntos(p,q):
    """
    Calcula la suma de dos puntos sobre cierta curva elíptica expresados en coordenadas
    """
    if q[0]-p[0] < 0:
        lamb = (q[1]-p[1])*modinv(q[0]-p[0]+fp,fp)
    elif q[0]-p[0] == 0:
        return (0,0)
    else:
        lamb = (q[1]-p[1])*modinv(q[0]-p[0],fp)
    #lamb = lamb % fp
    x = (lamb**2 - p[0] - q[0])%fp
    y = (lamb*(p[0]-x)-p[1])%fp
    return (x,y)

def duplicarPunto(p):
    """
    Calcula la suma de un punto consigo mismo expresado en coordenadas
    """
    if 2*p[1] < 0:
        lamb = (3*(p[0]**2)+a)*modinv(2*p[1]+fp,fp)
    else:
        lamb = (3*(p[0]**2)+a)*modinv(2*p[1],fp)
    #lamb = lamb % fp
    x = (lamb**2 - 2*p[0])%fp
    y = (lamb*(p[0]-x)-p[1])%fp
    return (x,y)

def multiplicarPunto(p,k):
    """
    Calcula la multiplicación de un punto k*P
    """
    k = k%fp
    if k == 0:
        return (0,0)
    for i in range(k-1):
        p = duplicarPunto(p)
    return p

class Punto:
    """
    Clase que modela los puntos de la curva como objetos matemáticos
    """
    def __init__(self,cords):
        self.cords = cords

    def __add__(self, q):
        if self.cords == (0,0): return q
        if q.cords == (0,0): return self
        if q.cords == self.cords: return Punto(duplicarPunto(self.cords))
        return Punto(sumarPuntos(self.cords,q.cords))

    def __mul__(self,k):
        if self.cords == (0,0):
            return self
        return Punto(multiplicarPunto(self.cords,k))

    def __rmul__(self,k):
        if self.cords == (0,0):
            return self
        return Punto(multiplicarPunto(self.cords,k))

    def inverso(self):
        """
        Calcula el punto inverso
        """
        x = self.cords[0]
        for y in [p.cords[1] for p in puntos]:
            if eval(curva) and y != self.cords[1]:
                return Punto((x,y))
        raise Exception("No se puede encontrar el inverso.")

def computarPuntos(fp,a,b):
    """
    Calcula los puntos racionales de una curva elíptica dada en forma de Weierstrass reducida sobre un cuerpo primo Fp
    curva = {y^2 = x^3 + ax + b}
    """
    field = [x for x in range(fp)]
    points = []
    for x in field:
        for y in field:
            if eval(curva):
                points.append(Punto((x,y)))
    return points

def cifrar(base,punto,pubkey):
    """
    Función de cifrado según ElGamal
    base -> punto generador elegido
    punto -> punto a cifrar
    pubkey -> clave pública del receptor
    Devuelve una tupla de datos (x,y)
    """
    print("Cifrando punto: {}".format(punto.cords))
    k = random.randint(2,fp-3)
    print("Parámetros de cifrado: k = {}, pubkey={}".format(k,pubkey.cords))
    x = k*base
    z = k*pubkey
    y = punto + z
    print("Datos cifrados: {}".format((x.cords,y.cords)))
    return (x,y)

def descifrar(data,privkey):
    """
    Función de descifrado según ElGamal
    data=(x,y) -> pareja de datos para el descifrado
    privkey -> clave privada del receptor
    Devuelve una tupla de datos (x,y) (punto descifrado)
    """
    q = privkey*data[0]
    z = q.inverso()
    return data[1] + z

descodificar = {(0,4):'m',(0,9):'e',(2,5):'n',(2,8):'s',(3,5):'a',(3,8):'j',
    (4,2):'x',(4,11):'l',(6,1):'k',(6,12):'w',(8,5):'r',(8,8):'t',(0,0):'y'}
codificar = {'m':(0,4),'e':(0,9),'n':(2,5),'s':(2,8),'a':(3,5),'j':(3,8),
    'x':(4,2),'l':(4,11),'k':(6,1),'w':(6,12),'r':(8,5),'t':(8,8),'y':(0,0)}

puntos = computarPuntos(fp,a,b)
puntos.insert(0,Punto((0,0)))

if __name__ == "__main__":
    #Secuencia principal de órdenes
    mensaje = "mensaje"
    print("Puntos de la curva: {}".format([p.cords for p in puntos]))
    g = Punto((0,4))
    pb = Punto((6,12))
    kb = 11
    print("Punto generador G = {}".format(g.cords))
    geng = [Punto((0,0)),g]
    for k in range(fp):
        if k==0 or k==1: continue
        geng.append(k*g)
    print("Puntos generados por G: {}".format([p.cords for p in geng]))
    print("\nCifrado:")
    data = []
    for char in mensaje:
        datablob = cifrar(g,Punto(codificar[char]),pb)
        data.append(datablob)
    print("Enviamos los datos a B y desciframos...\n")
    desmsg = []
    for datablob in data:
        pchar = descifrar(datablob,kb)
        desmsg.append(descodificar[pchar.cords])
    print("Mensaje descifrado: {}".format(''.join(desmsg)))