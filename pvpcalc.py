import sqlite3
from tkinter import *
from math import modf
from tkinter.font import BOLD
from tkinter import messagebox

root = Tk()

# fijar medidas de ventana
root.geometry('300x290')

# bloquear medidas ajustables
root.resizable(width=False, height=False)

# mantener en primer plano
root.wm_attributes("-topmost", 1)

# forzar la colocacion de logotipo
try:
    root.iconbitmap('logo.ico')
except:
    pass

# agregar titulo de la ventana
root.title("P.V.P. Calc.")

# crear la base de datos y la tabla de configuraciones
try:
    db = sqlite3.connect('dbpvp')
    cursor = db.cursor()
    cursor.execute('''
                   CREATE TABLE config (
                       id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       iva DECIMAL NOT NULL DEFAULT 0, 
                       req DECIMAL NOT NULL DEFAULT 0, 
                       profit DECIMAL NOT NULL DEFAULT 0, 
                       discount_in DECIMAL NOT NULL DEFAULT 0, 
                       discount_out DECIMAL NOT NULL DEFAULT 0, 
                       max_price DECIMAL NOT NULL DEFAULT 0, 
                       max_float DECIMAL NOT NULL DEFAULT 0, 
                       friendly_price DECIMAL NOT NULL DEFAULT 0, 
                       reduce_discount DECIMAL NOT NULL DEFAULT 0)
                    ''')
    db.commit()
    cursor.execute('''
                   INSERT INTO config (iva, req, profit, discount_in, discount_out,  max_price, max_float, friendly_price, reduce_discount) 
                   VALUES (21, 5.2, 100, 0, 0, 1000, 2, 1, 0)''')
    db.commit()
    db.close()
    #messagebox.showinfo('Conexion', 'La base de datos se creo correctamente!')
except sqlite3.OperationalError:
    #messagebox.showwarning('Conexion', 'La base de datos ya existe.')
    pass
        
# carga los datos de configuracion
def load_percent():
    db = sqlite3.connect('dbpvp')
    cursor = db.cursor()
    cursor.execute('SELECT * FROM config WHERE id = 1')
    db.commit()
    result = cursor.fetchone()
    config = {
        'iva' :             result[1],
        'req' :             result[2],
        'profit' :          result[3],
        'discount_in' :     result[4],
        'discount_out' :    result[5],
        'max_price' :       result[6],
        'max_float' :       result[7],
        'friendly_price' :  result[8],
        'reduce_discount' : result[9]
    }
    return config

# variables body
iva        = IntVar()
req        = IntVar()
iva_value  = StringVar()
req_value  = StringVar()
price_cost = StringVar(value='0.00')

# variables settings
profit          = IntVar()
discount_in     = IntVar()
discount_out    = IntVar()
max_price       = IntVar()
max_float       = IntVar()
friendly_price  = IntVar()
reduce_discount = IntVar()
config = load_percent()

# Recargar los datos necesarios
def refresh():
    global config
    config = load_percent()
    input = input_price.get()
    check_iva.config(text='IVA (' + str(config['iva']) + '%)')
    check_req.config(text='R.EQ. (' + str(config['req']) + '%)')
    iva_value.set(config['iva'])
    req_value.set(config['req'])
    calculate(input)
    
# actualizar los datos de la db
def update_percent():
    db = sqlite3.connect('dbpvp')
    cursor = db.cursor()
    percents = iva_value.get(), req_value.get(), profit.get(), discount_in.get(), discount_out.get()
    percents += max_price.get(), max_float.get(), friendly_price.get(), reduce_discount.get()
    cursor.execute('''
                   UPDATE config SET iva=?, req=?, profit=?, discount_in=?, discount_out=?, 
                                     max_price=?, max_float=?, friendly_price=?, reduce_discount=?  
                    WHERE id = 1''', percents)
    db.commit()
    db.close()
    refresh()
    show_body()

# Devuelve un valor mas amigable para los clientes    
def make_friendly_price(input):
     # redondear precios hast 3.99
    if input <= 0.5:
        price = 0.5
    elif input >= 0.51 and input <= 0.65:
        price = 0.65
    elif input >= 0.66 and input <= 0.75:
        price = 0.75
    elif input >= 0.76 and input <= 0.85:
        price = 0.85
    elif input >= 0.86 and input <= 0.9:
        price = 0.9
    elif input >= 0.91 and input <= 1:
        price = 1
    elif input >= 1.01 and input <= 1.1:
        price = 1.1
    elif input >= 1.11 and input <= 1.2:
        price = 1.2
    elif input >= 1.21 and input <= 1.25:
        price = 1.25
    elif input >= 1.26 and input <= 1.35:
        price = 1.35
    elif input >= 1.36 and input <= 1.5:
        price = 1.5
    elif input >= 1.51 and input <= 1.76:
        price = 1.75
    elif input >= 1.77 and input <= 2:
        price = 2
    elif input >= 2.01 and input <= 2.25:
        price = 2.25
    elif input >= 2.26 and input <= 2.5:
        price = 2.5
    elif input >= 2.51 and input <= 2.75:
        price = 2.75
    elif input >= 2.76 and input <= 2.99:
        price = 2.95
    elif input >= 3 and input <= 3.15:
        price = 3.15
    elif input >= 3.16 and input <= 3.35:
        price = 3.35
    elif input >= 3.36 and input <= 3.5:
        price = 3.5
    elif input >= 3.51 and input <= 3.75:
        price = 3.75
    elif input >= 3.76 and input <= 3.99:
        price = 3.95
    elif input >= 4:
        # ajusta los precios mayores de 4 
        differ, int_input = modf(input)
        differ = round(differ, 2)
        if differ <= 0.16 or differ == 1:
            price = int_input - 0.05
        elif differ >= 0.17 and differ <= 0.51:
            price = int_input + 0.5
        elif differ >= 0.52 and differ <= 0.76:
            price = int_input + 0.75
        elif differ >= 0.77 and differ <= 0.99:
            price = int_input + 0.95
    return price

# hace las operaciones matematicas    
def calculate(input):
    global config
    
    if input.isdigit() or '.' in input:
        
        # limitar el numero de puntos
        if input.count('.') > 1:
            return False
        
        try:
            input = float(input)
            
            # controlar decimales y precio maximo
            if len(str(input).split('.').pop()) > config['max_float'] or input > config['max_price']:
                return False
            
            # no calcular el 0
            if input == 0:
                return True
            
            # agregar el iva
            if iva.get() == 1:
                input = input + (input * (config['iva'] / 100))
            
            # agregar recargo de equivalencia    
            if req.get() == 1:
                input = input + (input * (config['req'] / 100))
            
            discount_in_discounted = input * (config['discount_in'] / 100)
            
            price_cost_discounted = input - discount_in_discounted
            
            # quitar el descuento de entrada
            if config['reduce_discount'] == 1:
                input = input - discount_in_discounted  
            
            # calcular el precio de venta    
            input = round(input + (input * (config['profit'] / 100)), config['max_float'])
            
            # redondear el importe a sumas mas amigables
            if config['friendly_price'] == 1:
                price = make_friendly_price(input)
            else:
                # precio tal qual resulta
                price = input
            
            # imprime los resultados
            price_cost.set(f"{price_cost_discounted:.2f}")     
            discount = price - ((price / 100 ) * config['discount_out'])     
            label_result.config(text=f"{price:.2f}")
            label_discount.config(text=f"{discount:.2f}")
            return True
        except:
            # no se puede calcular
            return False

    # aceptar teclas de borrado    
    elif input == '':
        label_result.config(text='0.00')
        label_discount.config(text='0.00')
        price_cost.set('0.00')
        return True
    
    # cortar paso a carracteres no numericos
    else:
        return False
        
# mostrar el msg de licencia    
def show_license():
    messagebox.showwarning('Info', 'Copyright (c) 2021 dragos2yo, Licencia MIT \nhttps://github.com/dragos2yo/pvpcalc/LICENSE.md')
    
# mostrar informacion de la aplicacion    
def show_about():
    messagebox.showinfo('PVP Calc.', 'Calculadora de PVP, version 1.0')
    
# salir de la aplicacion    
def exit_app():
    question = messagebox.askokcancel('Salir', '¿Seguro que desea salir?')
    if question == True:
        root.destroy()

# muestra el frame de preferencias
def show_settings():
    body.grid_remove()
    settings.grid(row=0, column=0, padx=15, pady=15)

# muestra el cuerpo de la aplicacion
def show_body():
    input_price.focus()
    settings.grid_remove()
    body.grid(row=0, column=0, padx=15, pady=15)

# cuerpo del programa
body = Frame(root)
body.grid(row=0, column=0, padx=15, pady=15)

# barra de navegacion superior
menubarr = Menu(root)
root.config(menu=menubarr)

# menu Archivo
menufile = Menu(menubarr, tearoff=0)
menufile.add_command(label="Preferencias", command=show_settings)
menufile.add_command(label="Salir", command=exit_app)
menubarr.add_cascade(label="Archivo", menu=menufile)

# menu Ayuda
menuhelp = Menu(menubarr, tearoff=0)
menuhelp.add_command(label="Licencia", command=show_license)
menuhelp.add_command(label='Acerca de', command=show_about)
menubarr.add_cascade(label="Ayuda", menu=menuhelp)

# campo precio
label_price = Label(body, text='Precio:')
label_price.grid(row=0, column=0, padx=10, pady=10, sticky='w')

input_price = Entry(body, width=19, borderwidth=2)
input_price.grid(row=0, column=1, padx=10, pady=10, ipady=2, ipadx=2, sticky='w')
input_price.focus()

reg = root.register(calculate)
input_price.config(validate='key', validatecommand=(reg, '%P'))

# campo iva
check_iva = Checkbutton(body, variable=iva, text='IVA (' + str(config['iva']) + '%)', onvalue=1, offvalue=0, command=lambda:calculate(input_price.get()))
check_iva.grid(row=1, column=0, padx=10, pady=10, sticky='w')

# campo recargo de equivalencia
check_req = Checkbutton(body, variable=req, text='R.EQ. (' + str(config['req']) + '%)', onvalue=1, offvalue=0, command=lambda:calculate(input_price.get()))
check_req.grid(row=1, column=1, padx=10, pady=10, sticky='w')

# campo precio mayor
label_cost = Label(body, text='Precio mayor:')
label_cost.grid(row=2, column=0, padx=10, pady=10, sticky='w')

input_cost = Label(body, textvariable=price_cost, font=('Helvetica', 12, BOLD), fg='black')
input_cost.grid(row=2, column=1, padx=10, pady=10, sticky='w')

# campo insertar espacio
label_padding = Label(body, text='.', font=('Helvetica', 50), fg='WHITE', bg='white', justify='center')
label_padding.grid(row=3, column=0, padx=10, pady=10, columnspan=2, sticky='wens')

# campo resultado
label_result = Label(body, text='0.00', font=('Helvetica', 38, BOLD), fg='black', bg='white', justify='center')
label_result.grid(row=3, column=0, padx=10, pady=10, columnspan=2, sticky='wes')

# campo precio con el descuento 
label_discount = Label(body, text='0.00', font=('Helvetica', 12, BOLD), fg='green', bg='white')
label_discount.grid(row=3, column=0, padx=10, pady=10, sticky='wn')

# cuerpo de ajustes
settings = Frame(root)

# campo iva
label_iva = Label(settings, text='I.V.A. (%):')
label_iva.grid(row=0, column=0, padx=4, pady=1, sticky='w')

input_iva = Entry(settings, width=19, borderwidth=1, textvariable=iva_value)
input_iva.grid(row=0, column=1, padx=4, pady=1, ipady=2, ipadx=2, sticky='w')
iva_value.set(config['iva'])

# campo recargo 
label_req = Label(settings, text='R.EQ. (%):')
label_req.grid(row=1, column=0, padx=4, pady=1, sticky='w')

input_req = Entry(settings, width=19, borderwidth=1, textvariable=req_value)
input_req.grid(row=1, column=1, padx=4, pady=1, ipady=2, ipadx=2, sticky='w')
req_value.set(config['req'])

# campo ganancias
label_profit = Label(settings, text='Ganancias (%):')
label_profit.grid(row=2, column=0, padx=4, pady=1, sticky='w')

input_profit = Entry(settings, width=19, borderwidth=1, textvariable=profit)
input_profit.grid(row=2, column=1, padx=4, pady=1, ipady=2, ipadx=2, sticky='w')
profit.set(config['profit'])

# campo descuento de entrada
label_disc_in = Label(settings, text='Desc. entrada (%):')
label_disc_in.grid(row=3, column=0, padx=4, pady=1, sticky='w')

input_disc_in = Entry(settings, width=19, borderwidth=1, textvariable=discount_in)
input_disc_in.grid(row=3, column=1, padx=4, pady=1, ipady=2, ipadx=2, sticky='w')
discount_in.set(config['discount_in'])

# campo descuento de salida
label_disc_out = Label(settings, text='Desc. salida (%):')
label_disc_out.grid(row=4, column=0, padx=4, pady=1, sticky='w')

input_disc_out = Entry(settings, width=19, borderwidth=1, textvariable=discount_out)
input_disc_out.grid(row=4, column=1, padx=4, pady=1, ipady=2, ipadx=2, sticky='w')
discount_out.set(config['discount_out'])

# campo precio maximo permitido
label_max_price = Label(settings, text='Entrada max.:')
label_max_price.grid(row=5, column=0, padx=4, pady=1, sticky='w')

input_max_price = Entry(settings, width=19, borderwidth=1, textvariable=max_price)
input_max_price.grid(row=5, column=1, padx=4, pady=1, ipady=2, ipadx=2, sticky='w')
max_price.set(config['max_price'])

# campo totatal de decimos
label_max_float = Label(settings, text='Num. decimos:')
label_max_float.grid(row=6, column=0, padx=4, pady=1, sticky='w')

input_max_float = Entry(settings, width=19, borderwidth=1, textvariable=max_float)
input_max_float.grid(row=6, column=1, padx=4, pady=1, ipady=2, ipadx=2, sticky='w')
max_float.set(config['max_float'])

# campo iva
check_friendly_price = Checkbutton(settings, variable=friendly_price, text='Amigable', onvalue=1, offvalue=0)
check_friendly_price.grid(row=7, column=0, padx=4, pady=1, sticky='w')
friendly_price.set(config['friendly_price'])

# campo req
check_reduce_discount = Checkbutton(settings, variable=reduce_discount, text='Perder desc.', onvalue=1, offvalue=0)
check_reduce_discount.grid(row=7, column=1, padx=4, pady=1, sticky='w')
reduce_discount.set(config['reduce_discount'])

#boton cargar
buttoncreate = Button(settings, text=" ⇽ Atras ", command=show_body)
buttoncreate.grid(row=8, column=0, padx=4, pady=2, sticky='w')

#boton actualizar
buttoncreate = Button(settings,text=" ↺ Actualizar ", command=update_percent)
buttoncreate.grid(row=8, column=1, padx=4, pady=2, sticky='e')

root.mainloop()