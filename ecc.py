import ecpy.curves as curves
import json
from os import path
from os import system
import secrets

tabla_UnicodeToPoint = {}
tabla_PointToUnicode = {}

def unicodechain(msg):
    """
    Convierte una cadena a una secuencia de code points (Unicode)
    """
    return [ord(char) for char in msg]

def recoverstr(encoded):
    """
    Recibe una secuencia de code points y reconstruye una cadena
    """
    return ''.join([chr(data) for data in encoded])

def generarTablas(curve):
    """
    Genera una tabla de correspondencias entre los primeros 9999 caracteres Unicode y las coordenadas comprimidas de puntos de la curva.
    Posteriormente guarda la tabla en un archivo json.
    """
    UtP = {}
    PtU = {}
    for i in range(10000):
        if i == 0 or i == 1: continue
        print(i)
        p = i*curve.generator
        cp = curve.encode_point(p)
        PtU[str(cp)] = i
        UtP[i] = cp
    print("Tablas completadas. Guardando archivos...")
    with open('tabla_UtP.json','w') as f:
        json.dump(UtP,f)
    with open('tabla_PtU.json','w') as f:
        json.dump(PtU,f)

def transfer_to_curve(msg,curve):
    """
    Transfiere un mensaje a puntos de la curva
    """
    unichain = unicodechain(msg)
    return [curve.decode_point(tabla_UnicodeToPoint[str(code)]) for code in unichain]

def release_from_curve(points,curve):
    """
    Devuelve puntos de la curva al mensaje original
    """
    unichain = []
    for p in points:
        try:
            code = tabla_PointToUnicode[str(cv.encode_point(p))]
        except KeyError:
            print("Hay un punto que no tiene correspondencia con ningún caracter unicode. Abortando...")
            return
        unichain.append(code)
    return recoverstr(unichain)

def cipher(point,curve,pk):
    """
    Función de cifrado según ElGamal
    point -> punto a cifrar
    curve -> curva sobre la que se realiza el cifrado
    pk -> clave pública del receptor 
    Devuelve una tupla de datos (x,y) (Puntos de la curva)
    """
    k = 0
    while k < 2:
        k = secrets.randbelow(curve.order-2)
    x = k*curve.generator
    z = k*pk
    y = point + z
    return (x,y)

def decipher(data,privkey):
    """
    Función de descifrado según ElGamal
    data=(x,y) -> pareja de datos para el descifrado
    privkey -> clave privada del receptor
    Devuelve el punto descifrado
    """
    q = privkey*data[0]
    z = q.neg()
    return data[1] + z

#Curva elíptica sobre la que realizamos el cifrado
cv = curves.Curve.get_curve('secp256k1')

#Comprobamos si existen las tablas y en caso contrario las generamos
if not (path.exists('tabla_UtP.json') and path.exists('tabla_PtU.json')):
    input("No se han detectado las tablas de correspondencia. Pulse enter para generar ambas...")
    generarTablas(cv)

#Recuperamos las tablas de correspondecias Unicode <--> Puntos de la curva
with open('tabla_UtP.json','r') as f:
    tabla_UnicodeToPoint = json.load(f)
with open('tabla_PtU.json','r') as f:
    tabla_PointToUnicode = json.load(f)

#Menú principal
while True:
    system('cls')
    print("ECC - Curva de cifrado: secp256k1")
    print("-"*50)
    print("1) Cifrar mensaje")
    print("2) Descifrar mensaje")
    print("3) Salir")
    print("")
    ch = input("Elige una opción: ")
    if ch == '1':
        #Sesión de cifrado
        #Inicializar clave pública
        while True:
            ch = input("Proporcionar clave pública (p) o aleatoria (a)?: ")
            if ch == 'p':
                while True:
                    x = input("Coordenada x del punto en hexadecimal: ")
                    y = input("Coordenada y del punto en hexadecimal: ")
                    try:
                        pubk = curves.Point(int(x,16),int(y,16),cv)
                    except curves.ECPyException:
                        print("Las coordenadas introducidas no se corresponden con",
                            "ningún punto de la curva. Vuelve a intentarlo... \n")
                    else:
                        break
                break
            elif ch == 'a':
                h = secrets.randbelow(cv.order)
                print("Se inicializará una clave pública aleatoria.",
                    "La clave privada asociada es: {}".format(h))
                pubk = h*cv.generator
                print("Clave pública generada en coordenadas:",
                    f" ({hex(pubk.x)},{hex(pubk.y)})")
                break
            else:
                print("Tienes que elegir una opción entre 'p' o 'a'. Vuelve a intentarlo...")

        msg = input("\nIntroduce el mensaje para cifrar: ")
        print("Cifrando...")
        puntos = transfer_to_curve(msg,cv)
        puntos_encriptados = [cipher(punto,cv,pubk) for punto in puntos]
        #Guardar datos
        with open('data.enc','w') as f:
            puntos_comprimidos = [(cv.encode_point(datos[0]),cv.encode_point(datos[1]))
                for datos in puntos_encriptados]
            datos = json.dumps(puntos_comprimidos)
            f.write(datos)
        print("Se han guardado los datos cifrados en el archivo data.enc")
        input("Pulsa enter para regresar al menu principal...")
    elif ch == '2':
        #Sesión de cifrado
        #Inicialización clave privada
        while True:
            privk = input("Introduce la clave privada: ")
            try:
                privk = int(privk)
            except ValueError:
                print("La clave privada tiene que ser un número entero. Vuelve a intentarlo...")
                continue
            if privk > cv.order:
                print("La clave privada excede el orden de la curva. Vuelve a intentarlo...")
            else: break
        #Proporcionar datos encriptados
        while True:
            path = input("Introduce el nombre del archivo" + 
                " que contiene los datos encriptados: ")
            try:
                f = open(path,'r')
            except FileNotFoundError:
                print("No se ha encontrado el archivo. Vuelve a intentarlo...")
            else:
                break
        encoded_data = json.loads(f.read())
        f.close()
        data = [(cv.decode_point(datos[0]),cv.decode_point(datos[1])) for datos in encoded_data]
        puntos_originales = [decipher(datos,privk) for datos in data]
        msg_original = release_from_curve(puntos_originales,cv)
        print("Mensaje descifrado: {}".format(msg_original))
        input("Pulsa enter para regresar al menu principal...")
    elif ch == '3':
        break
    else:
        input("No se ha reconocido ninguna opción válida. Vuelve a intentarlo...")