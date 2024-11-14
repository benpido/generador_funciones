from generador_funciones import GeneradorFunciones  
#################################################################################
# Menu para interactuar con el generador de funciones                           #
# Ademas valida las entradas para frecuencia amplitud y ciclos para el canal 1  #
# Para el canal 2 solo se valida frecuencia y amplitud                          #
#################################################################################


controller = GeneradorFunciones()
controller.connect()

def display_menu():
    """
    Muestra el menú de opciones al usuario.
    """
    print("====== MENÚ PRINCIPAL ======")
    print("1. Encender el generador de funciones")
    print("2. Configurar canal 1 (Amplitud, Frecuencia y Ciclos")
    print("3. Ver estado actual canal 1")
    print("4. Configurar canal 2 (Amplitud y Frecuencia")
    print("5. Ver estado actual canal 2")
    print("6. Apagar el generador de funciones")
    print("7. Salir")
    print("============================")

def encenderGenerador():
    ######################################
    # Encender el generador de funciones #
    ######################################
    controller.turn_on()

def delCanal1():
    ####################################################
    # Configurar canal 1 (Amplitud, Frecuencia y Ciclos#
    ####################################################
    while True:
        try:
            frequency = float(input("Ingrese frecuencia en Hz (0.000001 a 20 000 000): "))
            if frequency < 0.000001 or frequency > 20000000:
                raise ValueError("La frecuencia debe estar entre 0.000001 Hz y 20 000 000 Hz")
            break
        except ValueError as e:
            print(e)
    while True:
        try:
            cycles = int(input("Ingresa la cantidad de ciclos (1 a 50 000): "))
            if cycles < 1 or cycles > 50000:
                raise ValueError("La cantidad de ciclos debe estar entre 1 y 50 000")
            break
        except ValueError as e:
            print(e)

    while True:
        try:
            amplitude = float(input("Ingresa el valor de amplitud en Vpp (0.002 a 10): "))
            if amplitude < 0.002 or amplitude > 10:
                raise ValueError("La amplitud debe estar entre 0.002 y 10 Vpp.")
            break
        except ValueError as e:
            print(e)

    controller.channel_1(frequency, amplitude, cycles)

def estadoCanal1():
    #####################################
    # Leer el estado actual del canal 1 #
    # ###################################
    controller.read_channel_1_state()

def delCanal2():
    #############################################
    # Configurar canal 2 (Amplitud y Frecuencia #
    #############################################
    while True:
        try:
            print("Deje en blanco y presione ENTER para usar valor por defecto 4.8 kHz")
            freq_input = input("Ingrese frecuencia en Hz (0.000001 a 20 000 000): ")
            if freq_input == "":
                frequency = 4800
            else:
                frequency = float(freq_input)
                if frequency < 0.000001 or frequency > 20000000:
                    raise ValueError("La frecuencia debe estar entre 0.000001 Hz y 20 000 000 Hz")
            break
        except ValueError as e:
            print(e)

    while True:
        try:
            print("Deje en blanco y presione ENTER para usar valor por defecto 5 Vpp")
            amp_input = input("Ingresa el valor de amplitud en Vpp (0.002 a 10): ")
            if amp_input == "":
                amplitude = 5
            else:
                amplitude = float(amp_input)
                if amplitude < 0.002 or amplitude > 10:
                    raise ValueError("La amplitud debe estar entre 0.002 y 10 Vpp.")
            break
        except ValueError as e:
            print(e)
    controller.channel_2(frequency, amplitude)

def estadoCanal2():
    #####################################
    # Leer el estado actual del canal 2 #
    # ###################################
    controller.read_channel_2_state()

def apagarGenerador():
    #####################################
    # Apagar el generador de funciones  #
    # ###################################
    controller.turn_off()

def salir():
    controller.disconnect()

def main():
    """Función principal que ejecuta el menú de opciones."""
    while True:
        display_menu()
        try:
            choice = int(input("Selecciona una opción: "))
            if choice == 1:
                encenderGenerador()
            elif choice == 2:
                delCanal1()
            elif choice == 3:
                estadoCanal1()
            elif choice == 4:
                delCanal2()
            elif choice == 5:
                estadoCanal2()
            elif choice == 6:
                apagarGenerador()
            elif choice == 7:
                salir()
                print("Saliendo del programa.")
                break
            else:
                print("Opción no válida, intenta de nuevo.")
        except ValueError:
            print("Por favor, ingrese un número válido.")


if __name__ == "__main__":
    main()
