from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('carga/', views.carga, name='carga'),
    path('cargaxml/', views.cargarXML, name='cargaxml'),
    path('cargarxml/', views.procesarXML, name='cargarxml'),
    path('closemessages1/', views.cerrarMensajesCarga, name='closemessages1'),
    path('ventas/', views.verTablaVentas, name='ventas'),
    path('ventasmensuales/', views.verVentasMensuales, name='ventaspormes'),
    path('procesarventas/', views.procesarVentas, name='procesarventas'),
    path('procesarventa/', views.procesarVenta, name='procesarventa'),
    path('closemessages2/', views.cerrarMensajesProcesar, name='closemessages2'),
    path('verpdf/', views.verPdf, name='verpdf')
]