from wtforms import DateField, Form, SelectField, TextAreaField
from wtforms import IntegerField, StringField, PasswordField
from wtforms import EmailField 
from wtforms import validators 
from wtforms import Form, StringField, RadioField, SelectMultipleField, IntegerField, validators
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import DataRequired, NumberRange, ValidationError

def al_menos_un_ingrediente(form, field):
    if not field.data or len(field.data) == 0:
        raise ValidationError("Seleccione al menos un ingrediente")

class UserForm(Form):
    
    id=IntegerField("id")
    nombre=StringField("Nombre",[
        validators.DataRequired(message="Ingresa el nombre del cliente"),
        
        ])
    
    direccion =StringField("Dirección",[
        validators.DataRequired(message="La dirección es requerida"),
        ])
    telefono=StringField("Teléfono", [
        validators.DataRequired(message="Ingresa el número teléfono"),
        validators.length(min=10, max=10, message="Ingrese un número de teléfono válido")
        ])
    
    tamaño = RadioField('Tamaño Pizza', 
                        choices=[('Chica', 'Chica $40'),
                                 ('Mediana', 'Mediana $80'),
                                 ('Grande', 'Grande $120')],
                        validators=[DataRequired(message="Seleccione un tamaño")])
    
    ingredientes = SelectMultipleField(
    'Ingredientes',
    choices=[('Jamon', 'Jamón $10'), 
             ('Piña', 'Piña $10'), 
             ('Champiñones', 'Champiñones $10')],
    option_widget=CheckboxInput(),
    widget=ListWidget(prefix_label=False),
    validators=[al_menos_un_ingrediente]  
    )
    
    numeroPizzas = IntegerField('Num. de Pizzas', 
                                validators=[DataRequired(message="Ingrese la cantidad de pizzas"),
                                            NumberRange(min=1, message="Debe ser al menos 1")])
 
    fecha_pedido = DateField(
    "Fecha del pedido",
    format='%Y-%m-%d',
    validators=[DataRequired(message="Seleccione la fecha del pedido")]
)