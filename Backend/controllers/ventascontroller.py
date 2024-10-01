import os
from collections import defaultdict
from datetime import datetime
from xml.etree import ElementTree as ET

from flask import Blueprint, jsonify, request
from models.cliente import Cliente
from models.producto import Producto
from models.productos_enums import idProductos
from models.venta import Venta

BlueprintVenta = Blueprint('venta', __name__)

'''
Endpoint: http://{IP O LOCALHOST}:PUERTO/venta/cargar

Este endpoint se encarga de cargar las ventas que se encuentran en un xml
que se envía por el body

El xml debe tener la siguiente estructura:
- <ventas>
    - <venta>
        - <fecha_hora>dd/mm/yyyy hh:mm:ss</fecha_hora>
        - <cliente>
            - <nombre>nombre_cliente</nombre>
            - <nit>nit_cliente</nit>
        - <compras>
            - <producto>
                - <nombre_producto>nombre_producto</nombre_producto>
                - <cantidad>cantidad</cantidad>
                - <subtotal>subtotal</subtotal>
            - <producto>
                - <nombre_producto>nombre_producto</nombre_producto>
                - <cantidad>cantidad</cantidad>
                - <subtotal>subtotal</subtotal>
            - <producto>
            ...
        - <compras>
    ...

Si el xml no tiene la estructura correcta, se enviará un mensaje de error

Al cargar, se mantendrá una persistencia en el archivo database/ventas.xml
'''
@BlueprintVenta.route('/venta/cargar', methods=['POST'])
def cargarVentas():
    ventas = precargarXML()
    try:
        # Lee el xml que obtiene de entrada
        xml_entrada = request.data.decode('utf-8')
        if xml_entrada == '':
            return jsonify({
                'mensaje': 'No se ha enviado un xml',
                'status': 400
            }),400
        # Parsea el xml al Element Tree
        root = ET.fromstring(xml_entrada)
        #recorremos el root de ventas
        contador_ventas = len(ventas)
        for venta in root:
            fecha = ''
            hora = ''
            cliente = None
            productos = []
            #recorremos las etiquetas de la venta
            for elemento in venta:
                if elemento.tag == 'fecha_hora':
                    fecha_hora = elemento.text
                    formato = "%d/%m/%Y %H:%M:%S"
                    fecha_hora_obj = datetime.strptime(fecha_hora, formato)

                    fecha = fecha_hora_obj.date()
                    hora = fecha_hora_obj.time()
                if elemento.tag == 'cliente':
                    nombre = ''
                    nit = ''
                    for cliente in elemento:
                        if cliente.tag == 'nombre':
                            nombre = cliente.text
                        if cliente.tag == 'nit':
                            nit = cliente.text
                    cliente = Cliente(nombre, nit)
                if elemento.tag == 'compras':
                    for compras in elemento:
                        nombre_producto = ''
                        id_producto = -1
                        cantidad = 0
                        subtotal = 0
                        for producto in compras:
                            if producto.tag == 'nombre_producto':
                                nombre_producto = producto.text
                                id_producto = idProductos[nombre_producto.replace(" ", "_").upper().replace("Á","A").replace("É","E").replace("Í","I").replace("Ó","O").replace("Ú","U")].value
                            if producto.tag == 'cantidad':
                                cantidad = int(producto.text)
                            if producto.tag == 'subtotal':
                                subtotal = float(producto.text)
                        nuevo_producto = Producto(id_producto, nombre_producto, cantidad, subtotal)
                        productos.append(nuevo_producto)
            nueva_venta = Venta(contador_ventas, fecha, hora, cliente)
            nueva_venta.setProductos(productos)
            ventas.append(nueva_venta)
            contador_ventas += 1
        # Guardamos la lista de ventas en el archivo xml
        crearXML(ventas)
        return jsonify({
            'mensaje': 'Ventas cargadas',
            'status': 200
        }),200
    except KeyError as e:
        return jsonify({
            'mensaje': str(e),
            'status': 500
        }),500

'''
Endpoint: http://{IP O LOCALHOST}:PUERTO/venta/procesar

Este endpoint se encarga de que entra 1 venta y se agregue a
la persistencia de nuestra base de datos en XML

El xml debe tener la siguiente estructura:

- <venta>
    - <fecha_hora>dd/mm/yyyy hh:mm:ss</fecha_hora>
    - <cliente>
        - <nombre>nombre_cliente</nombre>
        - <nit>nit_cliente</nit>
    - <compras>
        - <producto>
            - <nombre_producto>nombre_producto</nombre_producto>
            - <cantidad>cantidad</cantidad>
            - <subtotal>subtotal</subtotal>
        - <producto>
            - <nombre_producto>nombre_producto</nombre_producto>
            - <cantidad>cantidad</cantidad>
            - <subtotal>subtotal</subtotal>
        - <producto>
        ...

Si el xml no tiene la estructura correcta, se enviará un mensaje de error

Al cargar, se mantendrá una persistencia en el archivo database/ventas.xml

Tambien retornará un XML, en donde muestre el total de la compra
'''

@BlueprintVenta.route('/venta/procesar', methods=['POST'])
def procesarVenta():
    ventas = precargarXML()
    try:
        xml_entrada = request.data.decode('utf-8')
        if xml_entrada == '':
            return jsonify({
                'mensaje': 'No se ha enviado un xml',
                'status': 400
            }),400
        root = ET.fromstring(xml_entrada)
        contador_ventas = len(ventas)
        fecha = ''
        hora = ''
        cliente = None
        productos = []
        for elemento in root:
            if elemento.tag == 'fecha_hora':
                fecha_hora = elemento.text
                formato = "%d/%m/%Y %H:%M:%S"
                fecha_hora_obj = datetime.strptime(fecha_hora, formato)

                fecha = fecha_hora_obj.date()
                hora = fecha_hora_obj.time()
            if elemento.tag == 'cliente':
                nombre = ''
                nit = ''
                for cliente in elemento:
                    if cliente.tag == 'nombre':
                        nombre = cliente.text
                    if cliente.tag == 'nit':
                        nit = cliente.text
                cliente = Cliente(nombre, nit)
            if elemento.tag == 'compras':
                for compras in elemento:
                    nombre_producto = ''
                    id_producto = -1
                    cantidad = 0
                    subtotal = 0
                    for producto in compras:
                        if producto.tag == 'nombre_producto':
                            nombre_producto = producto.text
                            id_producto = idProductos[nombre_producto.replace(" ", "_").upper().replace("Á","A").replace("É","E").replace("Í","I").replace("Ó","O").replace("Ú","U")].value
                        if producto.tag == 'cantidad':
                            cantidad = int(producto.text)
                        if producto.tag == 'subtotal':
                            subtotal = float(producto.text)
                    nuevo_producto = Producto(id_producto, nombre_producto, cantidad, subtotal)
                    productos.append(nuevo_producto)
        nueva_venta = Venta(contador_ventas, fecha, hora, cliente)
        nueva_venta.setProductos(productos)
        ventas.append(nueva_venta)
        total_nueva_venta = 0
        for producto in nueva_venta.getProductos():
            total_nueva_venta += producto.subtotal
        crearXML(ventas)
        xml_salida = '''<compra>
    <nombre>'''+nueva_venta.cliente.nombre+'''</nombre>
    <nit>'''+nueva_venta.cliente.nit+'''</nit>
    <fecha>'''+str(nueva_venta.fecha)+'''</fecha>
    <hora>'''+str(nueva_venta.hora)+'''</hora>
    <total>'''+str(total_nueva_venta)+'''</total>
</compra>
'''
        return jsonify({
            'mensaje': 'Venta procesada',
            'xml': xml_salida,
            'status': 200
        }),200
    except:
        return jsonify({
            'mensaje': 'Error al leer el xml',
            'status': 500
        }),500

'''
Endpoint: http://{IP O LOCALHOST}:PUERTO/venta/ventas

Este endpoint se encarga de mostrar todas las ventas cargadas
y mostrarlas en un JSON de salida
'''

@BlueprintVenta.route('/venta/ventas', methods=['GET'])
def obtenerVentas():
    ventas = precargarXML()
    ventas_json = []
    for venta in ventas:
        productos = []
        for producto in venta.getProductos():
            productos.append({
                'id': producto.getId(),
                'nombre': producto.getNombre(),
                'cantidad': producto.getCantidad(),
                'subtotal': producto.getSubtotal()
            })
        ventas_json.append({
            'id': venta.getId(),
            'fecha': str(venta.getFecha()),
            'hora': str(venta.getHora()),
            'cliente': {
                'nombre': venta.getCliente().nombre,
                'nit': venta.getCliente().nit
            },
            'productos': productos
        })
    return jsonify(ventas_json)

'''
Endpoint: http://{IP O LOCALHOST}:PUERTO/venta/mensual

Este endpoint se encarga de mostrar la cantidad generada
por mes
'''

@BlueprintVenta.route('/venta/mensual', methods=['GET'])
def ventasPorMes():
    ventas = precargarXML()
    total_por_mes = defaultdict(float)

    for venta in ventas:
        mes = venta.getFecha().strftime("%m")  # Obtener el mes como número
        total_venta = sum(producto.getSubtotal() for producto in venta.getProductos())  # Calcular el total de la venta

        total_por_mes[mes] += total_venta

    nombres_meses = {
        '01': 'enero',
        '02': 'febrero',
        '03': 'marzo',
        '04': 'abril',
        '05': 'mayo',
        '06': 'junio',
        '07': 'julio',
        '08': 'agosto',
        '09': 'septiembre',
        '10': 'octubre',
        '11': 'noviembre',
        '12': 'diciembre'
    }

    totales_ordenados = sorted(total_por_mes.items(), key=lambda x: x[1], reverse=True)

    resultados = []
    for mes, total in totales_ordenados:
        json_total_mes = {
            'mes': nombres_meses[mes],
            'total': total
        }
        resultados.append(json_total_mes)

    return jsonify(resultados)

'''
Como nos encargamos de que cada vez que cargue, se elimine el archivo
Entonces esta función se encarga de crear el XML, en base a la lista
que nosotros enviamos

Ruta donde se guarda:

database/ventas.xml
'''
def crearXML(ventas):
    # Si existe el archivo, lo eliminamos
    if os.path.exists('database/ventas.xml'):
        os.remove('database/ventas.xml')
    tree = ET.Element('ventas')
    for venta in ventas:
        venta_xml = ET.SubElement(tree, 'venta')
        fecha = ET.SubElement(venta_xml, 'fecha')
        fecha.text = str(venta.getFecha())
        hora = ET.SubElement(venta_xml, 'hora')
        hora.text = str(venta.getHora())
        cliente = ET.SubElement(venta_xml, 'cliente')
        nombre = ET.SubElement(cliente, 'nombre')
        nombre.text = venta.getCliente().nombre
        nit = ET.SubElement(cliente, 'nit')
        nit.text = venta.getCliente().nit
        compras = ET.SubElement(venta_xml, 'compras')
        for producto in venta.getProductos():
            producto_xml = ET.SubElement(compras, 'producto')
            nombre_producto = ET.SubElement(producto_xml, 'nombre_producto')
            nombre_producto.text = producto.getNombre()
            cantidad = ET.SubElement(producto_xml, 'cantidad')
            cantidad.text = str(producto.getCantidad())
            subtotal = ET.SubElement(producto_xml, 'subtotal')
            subtotal.text = str(producto.getSubtotal())
    tree = ET.ElementTree(tree)
    ET.indent(tree, space='\t', level=0)
    tree.write('database/ventas.xml', encoding='utf-8', xml_declaration=True)

'''
Esta función se encarga de leer el xml de persistencia que se encuentra en:
database/ventas.xml

Posteriormente de leerlo, crea los objetos correspondientes

Y por ultimo lo guarda en una lista de ventas para retornar

Si en dado caso el archivo no existe, envía una lista vacía
'''
def precargarXML():
    ventas = []
    if os.path.exists('database/ventas.xml'):
        tree = ET.parse('database/ventas.xml')
        root = tree.getroot()
        contador_ventas = 0
        for venta in root:
            fecha = ''
            hora = ''
            cliente = None
            productos = []
            for elemento in venta:
                if elemento.tag == 'fecha':
                    fecha = datetime.strptime(elemento.text, "%Y-%m-%d").date()
                if elemento.tag == 'hora':
                    hora = datetime.strptime(elemento.text, "%H:%M:%S").time()
                if elemento.tag == 'cliente':
                    nombre = ''
                    nit = ''
                    for cliente in elemento:
                        if cliente.tag == 'nombre':
                            nombre = cliente.text
                        if cliente.tag == 'nit':
                            nit = cliente.text
                    cliente = Cliente(nombre, nit)
                if elemento.tag == 'compras':
                    for compras in elemento:
                        nombre_producto = ''
                        cantidad = 0
                        subtotal = 0
                        id_producto = -1
                        for producto in compras:
                            if producto.tag == 'nombre_producto':
                                nombre_producto = producto.text
                                id_producto = idProductos[nombre_producto.replace(" ", "_").upper().replace("Á","A").replace("É","E").replace("Í","I").replace("Ó","O").replace("Ú","U")].value
                            if producto.tag == 'cantidad':
                                cantidad = int(producto.text)
                            if producto.tag == 'subtotal':
                                subtotal = float(producto.text)
                        nuevo_producto = Producto(id_producto, nombre_producto, cantidad, subtotal)
                        productos.append(nuevo_producto)
            nueva_venta = Venta(contador_ventas, fecha, hora, cliente)
            nueva_venta.setProductos(productos)
            ventas.append(nueva_venta)
            contador_ventas += 1
    return ventas
