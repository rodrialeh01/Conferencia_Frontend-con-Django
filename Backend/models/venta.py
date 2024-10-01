class Venta:
    def __init__(self, id, fecha, hora, cliente):
        self.id = id
        self.fecha = fecha
        self.hora = hora
        self.cliente = cliente
        self.productos = []
    
    def getId(self):
        return self.id
    
    def getFecha(self):
        return self.fecha
    
    def getHora(self):
        return self.hora
    
    def getCliente(self):
        return self.cliente
    
    def getProductos(self):
        return self.productos
    
    def setId(self, id):
        self.id = id

    def setFecha(self, fecha):
        self.fecha = fecha

    def setHora(self, hora):
        self.hora = hora
    
    def setCliente(self, cliente):
        self.cliente = cliente
    
    def setProductos(self, productos):
        self.productos = productos
    
    def addProducto(self, producto):
        self.productos.append(producto)
    