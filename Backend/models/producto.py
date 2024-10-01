class Producto:
    def __init__(self, id, nombre, cantidad, subtotal):
        self.id = id
        self.nombre = nombre
        self.cantidad = cantidad
        self.subtotal = subtotal
    
    def getId(self):
        return self.id
    
    def getNombre(self):
        return self.nombre
    
    def getCantidad(self):
        return self.cantidad
    
    def getSubtotal(self):
        return self.subtotal
    
    def setId(self, id):
        self.id = id
    
    def setNombre(self, nombre):
        self.nombre = nombre

    def setCantidad(self, cantidad):
        self.cantidad = cantidad

    def setSubtotal(self, subtotal):
        self.subtotal = subtotal
    