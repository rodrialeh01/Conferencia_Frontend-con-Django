import requests
from django.shortcuts import render

from .forms import FileForm, InputTextAreaForm

endpoint = 'http://localhost:5000/'
# Create your views here.
def index(request):
    return render(request, 'index.html')

def main(request):
    return render(request, 'main.html')

def carga(request):
    return render(request, 'carga.html')

contexto = {
    'contenido_archivo':None,
    'binario_xml':None,
    'mensaje_error': None,
    'mensaje_exito': None,
    'salida_procesada': None
}

def cargarXML(request):
    try:
        if request.method == 'POST':
            #obtenemos el formulario
            form = FileForm(request.POST, request.FILES)
            #verificamos si es valido
            if form.is_valid():
                #obtenemos el archivo
                archivo = request.FILES['file']
                #leemos el archivo
                contenido = archivo.read()
                #decodificamos el archivo a utf-8
                contenido_xml = contenido.decode('utf-8')
                #guardamos el contenido en el contexto
                contexto['contenido_archivo'] = contenido_xml
                contexto['binario_xml'] = contenido
                #enviamos el archivo al servidor
                contexto['mensaje_exito'] = 'Archivo cargado al sistema'
                return render(request, 'carga.html', contexto)
    except:
        contexto['mensaje_error'] = 'Error al cargar el archivo'
        return render(request, 'carga.html', contexto)
    
def procesarXML(request):
    try:
        if request.method == 'POST':
            #obtenemos el archivo
            archivo = contexto['binario_xml']
            if archivo is None:
                return render(request, 'carga.html')
            #enviamos el archivo al servidor
            response = requests.post(endpoint + 'venta/cargar', data=archivo)
            #obtenemos la respuesta en formato json
            respuesta = response.json()
            #guardamos la respuesta en el contexto
            print(respuesta['mensaje'])
            #limpiamos el contexto
            contexto['contenido_archivo'] = None
            contexto['binario_xml'] = None
            contexto['mensaje_exito'] = 'Ventas procesadas correctamente en el sistema'
            return render(request, 'carga.html', contexto)
    except:
        contexto['mensaje_error'] = 'Error al procesar el archivo en el servidor'
        return render(request, 'carga.html')

def cerrarMensajesCarga(request):
    contexto['mensaje_error'] = None
    contexto['mensaje_exito'] = None
    return render(request, 'carga.html', contexto)

def verTablaVentas(request):
    ctx = {
        'ventas': None
    }
    response = requests.get(endpoint + 'venta/ventas')
    data = response.json()
    if response.status_code == 200:
        ctx['ventas'] = data
    return render(request, 'ventas.html', ctx)

def verVentasMensuales(request):
    return render(request, 'ventaspormes.html')

def procesarVentas(request):
    return render(request, 'procesarventa.html')

def procesarVenta(request):
    contenido_textarea_entrada = ''
    try:
        if request.method == 'POST':
            form = InputTextAreaForm(request.POST)
            if form.is_valid():
                texto = form.cleaned_data
                contenido_textarea_entrada = texto['entrada']
                if contenido_textarea_entrada == '':
                    contexto['mensaje_error'] = 'No se ha ingresado un XML de entrada'
                    return render(request, 'procesarventa.html', contexto)
                #codificamos el mensaje de entrada
                venta_entrada = contenido_textarea_entrada.encode('utf-8')
                #enviamos el mensaje al servidor
                response = requests.post(endpoint + 'venta/procesar', data=venta_entrada)
                #obtenemos la respuesta en formato json
                respuesta = response.json()
                #guardamos la respuesta en el contexto
                contexto['mensaje_exito'] = 'Tu venta fue procesada correctamente!'
                #seteamos el valor de respuesta del textarea
                contexto['salida_procesada'] = respuesta['xml']
            return render(request, 'procesarventa.html', contexto)
        else:
            contexto['mensaje_error'] = 'No se ha ingresado un XML de entrada'
            return render(request, 'procesarventa.html', contexto)
    except:
        contexto['mensaje_error'] = 'No se pudo procesar tu venta, revisa correctamente tu XML de entrada'
        return render(request, 'procesarventa.html', contexto)

def cerrarMensajesProcesar(request):
    contexto['mensaje_error'] = None
    contexto['mensaje_exito'] = None
    return render(request, 'procesarventa.html', contexto)

def verPdf(request):
    return render(request, 'verpdf.html')