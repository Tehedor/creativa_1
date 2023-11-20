#!/usr/bin/env python
from subprocess import call, run
from lib_mv import MV,Red
import logging, sys, json
from os import path
from control_file import control_search,control_state,control_change_state,control_add,control_rm


# #########################################################################
# Creación control_file
# #########################################################################
reset_file = False
if path.exists("control_file") == False:
    reset_file = True
else:
    with open ('control_file','r') as archivo:
        n_lines = len(archivo.readlines())
    if n_lines < 5:
        reset_file = True
          

if reset_file == True:
    with open ('control_file','w') as archivo:
        archivo.write("#### RED #### 0 -> no lan; 1 -> hay LAN\n")
        archivo.write("\tLAN\t0\n")
        archivo.write("\n#### MAQUINAS VIRTUALES #### 0 -> parada; 1 -> arrancada\n\n")  
    n_lines = 4
# #########################################################################
# #########################################################################

with open('auto_p2.json', 'r') as f:
    data = json.load(f)


num_server = data['num_server']
# debug = data['debug']

if len(sys.argv) < 2:
    print("Error: No se proporcionó el segundo argumento.")
    sys.exit(1)


def init_log():
    # Creacion y configuracion del logger
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger('auto_p2')
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    log.addHandler(ch)
    log.propagate = False

def pause():
    programPause = raw_input("Press the <ENTER> key to continue...")

# Main
init_log()
print('CDPS - mensaje info1')



# #########################################################################
# Argumentos
# #########################################################################
second_arg = sys.argv[1]

next_arg = []

all_vm = ["c1","lb"]
for i in range(num_server):
    all_vm.append("s" + str(i+1)) 

i=2
if len(sys.argv) > 2:
    while i < len(sys.argv) and sys.argv[i] != " ":
        print(sys.argv[i][1:].isdigit())
        if sys.argv[i] != "lb" and sys.argv[i] != "c1" and not(sys.argv[i].startswith("s") and sys.argv[i][1:].isdigit()):
            print(f"maquina {sys.argv[i]} no permitida")                
        else:
            next_arg.append(sys.argv[i])
        i = i + 1
else:
    next_arg = all_vm



# #########################################################################
# #########################################################################
# Aplicacion
# #########################################################################
# #########################################################################


if second_arg == 'crear':
    imagen = "cdps-vm-base-pc1.qcow2"   
    
    if not control_state("LAN","1"):
        if1 = Red("LAN1")
        if2 = Red("LAN2")
        if1.crear_red()
        if2.crear_red()
        control_add("LAN")
    
    for nombre_mv in next_arg:
        if not control_search(nombre_mv):
            nombre = MV(nombre_mv)
            router = False
            if nombre_mv == "lb":
                router = True
            nombre.crear_mv(imagen, router)
            # nombre.crear_mv(imagen,interface_red, router)
            control_add(nombre_mv)
        else:
            print(f"Error: La maquina {nombre_mv} ya existe")
    
elif second_arg == 'arrancar':

    # Arrancar maquinas
    for nombre_mv in next_arg:
        if control_search(nombre_mv):
            if control_state(nombre_mv,"0"):    
                nombre = MV(nombre_mv)
                nombre.arrancar_mv() 
                # nombre.mostrar_consola_mv()
                control_change_state(nombre_mv,"1")
            else:
                print(f"Error: La maquina {nombre_mv} ya esta arrancada")
        else:
            print(f"Error: La maquina {nombre_mv} no existe")


elif second_arg == 'parar':
    for nombre_mv in next_arg:
        if control_search(nombre_mv):
            if control_state(nombre_mv,"1"):
                nombre = MV(nombre_mv)
                nombre.parar_mv()
                control_change_state(nombre_mv,"0")
            else:
                print(f"Error: La maquina {nombre_mv} ya esta parada")
        else:
            print(f"Error: La maquina {nombre_mv} no existe")
      
elif second_arg == 'liberar':
    for nombre_mv in next_arg:
        nombre = MV(nombre_mv)
        nombre.liberar_mv()
        control_rm(nombre_mv)
   
    # Liberar redes
    with open ('control_file','r') as archivo:
        n_lines = len(archivo.readlines())

    print(n_lines)

    if n_lines < 6:
        if1 = Red("LAN1")
        if2 = Red("LAN2")
        if1.liberar_red()
        if2.liberar_red()
        control_rm("LAN")

elif second_arg == 'consola':
    for nombre_mv in next_arg:
        nombre = MV(nombre_mv)
        run(["xterm","-e","sudo","virsh","console",nombre_mv])
elif second_arg == 'monitor':
    run(["watch", "-n", "2", "virsh", "list", "--all"])
else:
    print(f"Error: Argumento desconocido {second_arg}")
