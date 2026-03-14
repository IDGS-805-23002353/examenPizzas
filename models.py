from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class Pizzas(db.Model):
    __tablename__='pizzas'
    
    id = db.Column(db.Integer, primary_key=True)
    tamaño = db.Column(db.String(20))
    ingredientes = db.Column(db.String(200))
    precio = db.Column(db.Numeric(8,2))
    
    pedidos = db.relationship(
        'Pedidos',
        secondary='detalle_pedido',
        back_populates='pizzas'
    )
    
class Clientes(db.Model):
    __tablename__='clientes'
    id=db.Column(db.Integer, primary_key=True)
    nombre=db.Column(db.String(100))
    direccion=db.Column(db.String(200))
    telefono=db.Column(db.String(20))
    
    pedidos = db.relationship(
        'Pedidos', 
        back_populates='cliente')
    
    
class Detalle_pedido(db.Model):
    __tablename__ = 'detalle_pedido'
    id = db.Column(db.Integer, primary_key=True)
    
    id_pedido = db.Column(
        db.Integer,
        db.ForeignKey('pedidos.id'),
        nullable=False
    )
      
    id_pizza = db.Column(
        db.Integer,
        db.ForeignKey('pizzas.id'),
        nullable=False
    )
    
    cantidad = db.Column(db.Integer, default=1)
    
  
class Pedidos(db.Model):
    __tablename__='pedidos'
    id = db.Column(db.Integer, primary_key=True)

    
    id_cliente = db.Column(
        db.Integer,
        db.ForeignKey('clientes.id'),
        nullable=False
    )
    
    fecha_pedido = db.Column(
        db.DateTime     
    )
    
    total = db.Column(db.Numeric(10,2))
       
    
    cliente = db.relationship(
        "Clientes",
        back_populates="pedidos"
    )
    
    pizzas = db.relationship(
        'Pizzas', 
        secondary='detalle_pedido', 
        back_populates='pedidos')



    
  


