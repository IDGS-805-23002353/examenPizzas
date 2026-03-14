
from flask import Flask, render_template, request, redirect, url_for, session
from flask import flash
from flask_wtf import form
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from sqlalchemy import text
from config import DevelopmentConfig
from models import Detalle_pedido, Pedidos, Pizzas, Clientes, db
import forms
from datetime import datetime



app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
db.init_app(app)
migrate = Migrate(app, db)
csrf=CSRFProtect(app)
app.secret_key = 'Clave secreta' 



@app.errorhandler(404)
def page_not_fount(e):
    return render_template("404.html"),404



@app.route('/', methods=['GET', 'POST'])
def index():
    form = forms.UserForm(request.form)
    titulo_ventas = "Ventas del día de hoy"
    hoy = datetime.today().date()

    ventas = Pedidos.query.filter(
        db.func.date(Pedidos.fecha_pedido) == hoy
    ).all()

    total_dia = sum([float(venta.total) for venta in ventas])

    if 'carrito' not in session:
        session['carrito'] = []

    if request.method == 'POST' and form.validate():
        session['fecha_pedido'] = form.fecha_pedido.data
        precios = {'Chica': 40, 'Mediana': 80, 'Grande': 120}
        precio_base = precios.get(form.tamaño.data, 0)
        costo_ingredientes = len(form.ingredientes.data) * 10
        subtotal = (precio_base + costo_ingredientes) * form.numeroPizzas.data

        nueva_pizza = {
            'tamaño': form.tamaño.data,
            'ingredientes': ", ".join(form.ingredientes.data),
            'cantidad': form.numeroPizzas.data,
            'subtotal': float(subtotal)
        }
        
        carrito = session['carrito']
        carrito.append(nueva_pizza)
        session['carrito'] = carrito

        session['cliente_data'] = {
        'nombre': form.nombre.data,
        'direccion': form.direccion.data,
        'telefono': form.telefono.data
        
}
   
        flash("Pizza agregada al carrito", "success")
    total_venta = sum(item['subtotal'] for item in session['carrito'])
   

    return render_template("index.html", form=form, carrito=session['carrito'], total_venta=total_venta, ventas=ventas,titulo_ventas=titulo_ventas, total_dia=total_dia)


@app.route('/quitar', methods=['POST'])
def quitar_item():
    carrito = session.get('carrito', [])
    

    try:
        indice = int(request.form.get('indice', -1))  
    except ValueError:
        indice = -1  
    

    if 0 <= indice < len(carrito):
        carrito.pop(indice)
        session['carrito'] = carrito
        session.modified = True
    else:
        flash("No se seleccionó ningún registro válido para quitar", "warning")
    
    return redirect(url_for('index'))

@app.route('/terminar', methods=['POST'])
def terminar():
    carrito = session.get('carrito', [])
    if not carrito:
        flash("El carrito está vacío", "warning")
        return redirect(url_for('index'))

    total_final = sum(item['subtotal'] for item in carrito)
    cliente = session.get('cliente_data')
    fecha_pedido_raw = session.get('fecha_pedido')

    
    try:
        
        fecha_final = datetime.strptime(fecha_pedido_raw, '%a, %d %b %Y %H:%M:%S GMT')
    except (ValueError, TypeError):
        
        fecha_final = datetime.now()
    

    nuevo_c = Clientes(
        nombre=cliente['nombre'],
        direccion=cliente['direccion'],
        telefono=cliente['telefono']
    )
    db.session.add(nuevo_c)
    db.session.flush()

    nuevo_p = Pedidos(
        id_cliente=nuevo_c.id,
        total=total_final,
        fecha_pedido=fecha_final  
    )
    db.session.add(nuevo_p)
    db.session.flush()

    for item in carrito:
        pizza_db = Pizzas(
            tamaño=item['tamaño'],
            ingredientes=item['ingredientes'],
            precio=item['subtotal']
        )
        db.session.add(pizza_db)
        db.session.flush()

        db.session.add(
            Detalle_pedido(
                id_pedido=nuevo_p.id,
                id_pizza=pizza_db.id,
                cantidad=item['cantidad']
            )
        )

    db.session.commit()

    flash(f"¡Pedido procesado con éxito! Total a pagar: ${total_final}", "success")

    session.pop('carrito', None)
    session.pop('fecha_pedido', None)

    return redirect(url_for('index'))

@app.route('/consulta_dia', methods=['POST'])
def consulta_dia():
    form = forms.UserForm(request.form)
    dia_semana = request.form.get('dia_semana', '').strip().lower()
    
    if not dia_semana:
        flash("Debes ingresar un día de la semana", "warning")
        return redirect(url_for('index'))

    dias = ['lunes','martes','miércoles','jueves','viernes','sábado','domingo']
    if dia_semana not in dias:
        flash("Día de la semana inválido", "warning")
        return redirect(url_for('index'))

    
    dia_num_mysql = (dias.index(dia_semana) + 2) % 7
    if dia_num_mysql == 0:
        dia_num_mysql = 7 
        
    ventas = Pedidos.query.filter(
        text(f"DAYOFWEEK(fecha_pedido) = {dia_num_mysql}")
    ).all()

    total_dia = sum(v.total for v in ventas)
    titulo_ventas = f"Ventas del día {dia_semana.capitalize()}"
    flash(f"Visualizando ventas del día {dia_semana.capitalize()}", "success")

    return render_template(
        "index.html",
        form=form,
        ventas=ventas,
        titulo_ventas=titulo_ventas,
        total_dia=total_dia,
        carrito=session.get('carrito', [])
    )
    


@app.route('/consulta_mes', methods=['POST'])
def consulta_mes():
    form = forms.UserForm(request.form)

    nombre_mes = request.form.get('mes_texto', '').strip().lower()  
    if not nombre_mes:
        flash("Debes ingresar un mes para consultar las ventas", "warning")
        return redirect(url_for('index'))

    meses = [
        "enero","febrero","marzo","abril","mayo","junio",
        "julio","agosto","septiembre","octubre","noviembre","diciembre"
    ]

    if nombre_mes not in meses:
        flash("Nombre de mes inválido", "warning")
        return redirect(url_for('index'))

    numero_mes = meses.index(nombre_mes) + 1

    
    from sqlalchemy import extract
    ventas = Pedidos.query.filter(
        extract('month', Pedidos.fecha_pedido) == numero_mes
    ).all()

    total_mes = sum(v.total for v in ventas)
    titulo_ventas = f"Ventas del mes de {nombre_mes.capitalize()}"
    flash(f"Visualizando ventas del mes de  {nombre_mes.capitalize()}", "success")

    return render_template(
        "index.html",
        form=form,
        ventas=ventas,
        titulo_ventas=titulo_ventas,
        total_dia=total_mes,
        carrito=session.get('carrito', [])
    )
    
@app.route('/detalle/<int:id_pedido>')
def detalle(id_pedido):
    pedido_principal = Pedidos.query.get_or_404(id_pedido)

    detalles_pizzas = db.session.query(
        Pizzas.tamaño,
        Pizzas.ingredientes,
        Pizzas.precio,
        Detalle_pedido.cantidad 
    ).join(Detalle_pedido).filter(
        Detalle_pedido.id_pedido == id_pedido
    ).all()

    return render_template("detalle.html", pedido=pedido_principal, detalles=detalles_pizzas)

   
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
