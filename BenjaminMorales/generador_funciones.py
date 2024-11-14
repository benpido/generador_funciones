import pyvisa
import time

class GeneradorFunciones:
    """
    Clase para controlar un generador de funciones RIGOL DG1022 mediante VISA.

    Esta clase permite la conexión y el control remoto del generador de funciones RIGOL DG1022,
    facilitando la configuración de canales, lectura de estados y manejo seguro de la conexión.
    Utiliza pyvisa como backend para comunicarse con el dispositivo a través de los comandos SCPI estándar.

    Métodos:
        connect(): Intenta conectar con el generador de funciones especificado en la lista de recursos VISA.
                   Busca un dispositivo que contenga 'DG1D200' en su descripción. Si lo encuentra, establece
                   una conexión y configura un tiempo de espera. Retorna True si la conexión es exitosa.
        disconnect(): Cierra la conexión activa con el generador y apaga el dispositivo de forma segura.
        is_connected(): Verifica si hay una conexión activa con el generador de funciones.
        turn_on(): Enciende el generador de funciones si está conectado.
        turn_off(): Apaga el generador de funciones si está conectado.
        channel_1(frecuencia, amplitud, ciclos, offset=0): Configura el canal 1 con los parámetros
                                                           especificados para operar en modo Burst.
        channel_2(frecuencia=4800, amplitud=5, offset=0): Configura el canal 2 con una onda sinusoidal.
        read_channel_1_state(): Consulta y retorna el estado actual del canal 1.
        read_channel_2_state(): Consulta y retorna el estado actual del canal 2.
        handle_disconnection(): Maneja la desconexión intentando cerrar la conexión actual y
                                reconectando si es posible.
        close(): Cierra todos los recursos VISA asociados al generador de funciones.

    Ejemplo de uso:
        generador = GeneradorFunciones()
        if generador.connect():
            generador.turn_on()
            generador.channel_1(1000, 5, 10)
            estado = generador.read_channel_1_state()
            print(estado)
            generador.turn_off()
        generador.close()
    """
    def __init__(self):
        self.pyvisa = pyvisa.ResourceManager() # Instancia de PYVISA, Gestor de comunicaciones con los dispositivos
        self.pyvisa_list = self.pyvisa.list_resources()
        self.index = None ## Almacena el indice donde se debe intentar la conexccion
        self.instrument = None # Objeto que representa y contiene la conexion activa con el generador de funciones
        
    def connect(self):
    #############################################################################################################################
    # Este metodo listara los recursos deisponibles por PYVISA, los recorre y espera que alguno de ellos contenga DG1D200       #
    # Si no es el generador especificado, cierra la conexion pyvisa retorna FALSE eh imprime por consola Que no se encontro     #
    # Si salta algun error en en este flujo, imprime el error por consola y no se interrumpe el codigo.                         #
    #############################################################################################################################
        try:
            for i, device in enumerate(self.pyvisa_list):
                if "DG1D200" in device:
                    self.index = i  # Asigna el índice a self.index
                    break  # Termina el bucle después de encontrar el dispositivo
            else:
            # Si no se encuentra el dispositivo, establece self.index en None
                self.index = None
                print("Dispositivo no encontrado.")
                return False

            # Abre la conexión con el dispositivo en `self.index`
            if self.index is not None:
                self.instrument = self.pyvisa.open_resource(self.pyvisa_list[self.index])
                self.instrument.timeout = 10000  # Aumenta el timeout a 10 segundos
                # Envía el comando de identificación, espera un momento, y lee la respuesta
                self.instrument.write('*IDN?')
                time.sleep(0.5)  
                idn_response = self.instrument.read()  # Lee la respuesta
                idn_response = idn_response.split(",")
                marca = idn_response[0]
                modelo = idn_response[1]
                print("Se a conectado exitosamente al dispositivo")
                print("Fabricante: " ,marca)
                print("Modelo: ",modelo)
                return True  # Conexión exitosa
            else:
                print("Índice no válido para abrir el recurso.")
                return False
        
        except pyvisa.VisaIOError as e:
            print("Error de comunicación con el dispositivo:", str(e))
            return False
        except Exception as e:
            print("Error inesperado al conectar:", str(e))
            return False

    def disconnect(self):
    #####################################################################################    
    # Si hay una conexion activa del generador de funciones, la cierra                  #
    # Ademas vacia el objeto que representa a la conexion con el generador de funciones #
    #####################################################################################
        if self.instrument:
            try :
                self.turn_off()
                self.instrument.close()
                self.instrument = None
                print("Generador desconectado y apagado.")
            except pyvisa.VisaIOError as e:
                print(f"Error al desconectar el generador: {e}")
            except Exception as e:
                print(f"Error inesperado al desconectar: {e}")
        else:
            print("No hay instrumento que desconectar.")
   
    def is_connected(self): 
        ########################################################################################################
        # Retorna TRUE si hay una conexion activa con el generador de funciones en caso contrario retorna FALSE#
        ########################################################################################################
        return self.instrument is not None
   
    def turn_on(self): 
        ##########################################################################################################
        # Si esta conectado, Manda señal de encendido al generador de funciones                                  #
        # Si salta algun error en este proceso, imprime por consola el error y maneja una desconeccion segura    #
        ##########################################################################################################
        if self.is_connected():
            try:
                self.instrument.write("OUTP ON")
                time.sleep(0.5)
                print("Generador encendido.")
            except pyvisa.VisaIOError as e:
                print(f"Error de comunicación al encender el generador: {e}")
                self.handle_disconnection()
            except Exception as e:
                print(f"Error inesperado al encender el generador: {e}")
                self.handle_disconnection()
        else:
            print("No hay conexión activa con el generador.")
            return

    def channel_2(self, frecuencia=4800, amplitud=5, offset=0): 
        ###########################################################################################
        # Configura el canal 2 con una onda SINOUDAL con los parámetros especificados             #
        # Offset, es opcional, es para hacer que la funcion ocile entre estos valores en voltaje  #    
        # Frecuencia en Hz; Amplitud en Voltaje pico a pico (Vpp); Offset en Voltaje              #
        ###########################################################################################
        if self.is_connected():
            try:
                command = f"APPL:SIN:CH2 {frecuencia},{amplitud},{offset}"
                self.instrument.write(command)
                print(f"Onda sinusoidal en CH2 configurada: {frecuencia} Hz, {amplitud} Vpp, Offset {offset} V.")
            except pyvisa.VisaIOError as e:
                print(f"Error de comunicación al configurar CH2: {e}")
                self.handle_disconnection()
            except Exception as e:
                print(f"Error inesperado al configurar CH2: {e}")
                self.handle_disconnection()
        else:
            print("No hay conexión activa con el generador.")
   
    def read_channel_2_state(self):
    ###########################################################################################
    # Lee el estado del canal 2 y devuelve la configuración actual del canal                  #
    # La salida esperada es del tipo : "SIN,1.000000e+03,5.000000e+00,-1.500000e+00"          #
    # Que representa un configuracion de : Frecuencia 1000Hz; Amplitud 5.0Vpp; Offset -1.5 V  #
    ###########################################################################################
        if self.is_connected():
            try:
                time.sleep(0.5)
                # comando de consulta para leer el estado de CH2
                self.instrument.write('APPLy:CH2?')
                time.sleep(0.5)
                response = self.instrument.read()
                print(f"Estado del Canal 2: {response}")
                return response
            except pyvisa.VisaIOError as e:
                print(f"Error de comunicación al leer el estado de CH2: {e}")
                self.handle_disconnection()
            except Exception as e:
                print(f"Error inesperado al leer el estado de CH2: {e}")
                self.handle_disconnection()
        else:
            print("No hay conexión activa con el generador.")
   
    def channel_1(self, frecuencia, amplitud, ciclos, offset=0):
        #############################################################
        # Configura el canal 1 en modo Burst con una onda sinoudal  #
        #    Parámetros:                                            #
        #    - frecuencia: Frecuencia de la onda sinusoidal en Hz   #
        #    - amplitud: Amplitud voltaje pico a pico de la onda    #
        #    - ciclos: Número de ciclos en el modo Burst            #
        #############################################################

        if self.is_connected():
            try:
                command = f"APPLy:SINusoid {frecuencia},{amplitud},{offset}"
                self.instrument.write(command)
                time.sleep(0.5)
                print(f"Canal 1 configurado: {frecuencia} Hz, {amplitud} Vpp")
                self.instrument.write("BURS:STAT ON") # Habilita el modo Burst
                time.sleep(0.5)
                self.instrument.write("BURS:MODE TRIG") # Establece el modo de Burst a "Triggered"
                time.sleep(0.5)
                self.instrument.write(f"BURS:NCYC {ciclos}") # Número de ciclos en Burst
                time.sleep(0.5)
                self.instrument.write("BURS:PHAS 0") # Configura fase inicial en 0
                time.sleep(0.5)
                self.instrument.write("TRIG:SOUR IMM") # Configura el disparo como inmediato
                time.sleep(0.5)

            except pyvisa.VisaIOError as e:
                print(f"Error de comunicación al configurar CH1 en modo Burst: {e}")
                self.handle_disconnection()
            except Exception as e:
                print(f"Error inesperado al configurar CH1 en modo Burst: {e}")
                self.handle_disconnection()
        else:
            print("No hay conexión activa con el generador.")
   
    def read_channel_1_state(self):
        #################################################################################
        # Lee el estado del canal 1 y devuelve la configuración actual del canal        #
        # la salida esperada es del tipo : "SIN,1.000000e+03,5.000000e+00,0.000000e+00" #
        # Que representa wave_type; Frecuencia 1000Hz; Amplitud 5.0Vpp; Offset 0 V      #
        #################################################################################
        if self.is_connected():
            try:
                self.instrument.write('BURS:STAT?')
                time.sleep(0.5)
                burst =  self.instrument.read()
                time.sleep(0.5)
                self.instrument.write('APPLy?')
                time.sleep(0.5)
                response = self.instrument.read()
                print(f"Estado actual del Canal 1: {response}")
                print(f"Estado actual de modo burst en el canal 1 es: {burst}")
                return response
               
            except pyvisa.VisaIOError as e:
                print(f"Error de comunicación al leer el estado de CH1: {e}")
                self.handle_disconnection()
            except Exception as e:
                print(f"Error inesperado al leer el estado de CH1: {e}")
                self.handle_disconnection()
        else:
            print("No hay conexión activa con el generador.")
        
    def turn_off(self):
    ############################################################################################
    # Si esta conectado, Manda una señal de APAGADO, Y maneja errores y una desconeccion segura#
    ############################################################################################
        if self.is_connected():
            try:
                self.instrument.write("OUTP OFF")
                time.sleep(0.5)
                print("Generador apagado.")
            except pyvisa.VisaIOError as e:
                print(f"Error de comunicación al apagar el generador: {e}")
                self.handle_disconnection()
            except Exception as e:
                print(f"Error inesperado al apagar el generador: {e}")
        else:
            print("No hay conexión activa con el generador.")
   
    def handle_disconnection(self):
    ###############################################################################################################################
    # Este metodo cierra la coneccion de pyvisa con el generador de funciones de manera correcta e intenta reconectar una sola vez#
    ###############################################################################################################################
        print("Manejando desconexión...")
        if self.instrument:
            try:
                self.instrument.close()
            except pyvisa.VisaIOError as e:
                print(f"No se pudo cerrar la conexión correctamente: {e}")
            except Exception as e:
                print(f"Error inesperado al cerrar la conexión: {e}")
            finally:
                self.instrument = None
        else:
            print("No hay conexión activa con el generador.")

        time.sleep(2)  # intentar reconectar
        if self.connect():
            print("Reconectado exitosamente.")
        else:
            print("No se pudo reconectar.")
   
    def close(self):
    ############################################################################################################
    # Si hay una conexion activa con el generador de funciones la cierra, y luego cierra la intancia de PYVISA #
    ############################################################################################################
        if self.instrument:
            self.disconnect()
            self.pyvisa.close()
        else:
            print("No hay conexión activa con el generador.")

## IMPORTANTE, NOTA:
# Las validaciones de los rangos estan en el menu
# Hay algunas partes donde la conexion queda activa, por ejemlo en turn_off
#   - Si se apaga, tambien se quiere realizar la desconexion ?
# El generador de funciones, permite ingresarle unidad de media
#   - En el menu solo se permitira ingresas en su minima unidad (Hz; Vpp;)