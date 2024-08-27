# main.py

import threading  # Para trabalhar com threads
import readchar  # Para capturar teclas do teclado
import sys  # Para manipulação de argumentos de linha de comando
from time import sleep  # Para pausas no programa
from data import DataCom  # Importa a classe DataCom para comunicação de dados
from servidor import Servidor  # Importa a classe Servidor
from cliente import Cliente  # Importa a classe Cliente

def main():
    # Definir número padrão de pares
    numero_de_pares = 2

    # Verifica se um número de pares foi passado como argumento
    if len(sys.argv) >= 2:
        numero_de_pares = int(sys.argv[1])

    # Inicializa as informações de comunicação com o arquivo 'portas.txt'
    info = DataCom("portas.txt", numero_de_pares)

    # Cria instâncias do servidor e cliente com as informações de comunicação
    servidor = Servidor(info)
    cliente = Cliente(info)

    # Calcula e exibe a Finger Table
    finger_table = info.calculate_finger_table()
    print("Finger Table para o nó:")
    for idx, finger in enumerate(finger_table, start=1):
        print(f"F{idx}: {finger}")

    # Inicia o servidor em uma thread separada
    tserver = threading.Thread(target=servidor.run)
    tserver.start()

    # Pequena pausa para garantir que o servidor esteja pronto
    sleep(0.1)

    # Exibe as informações iniciais e espera pela tecla ENTER para conectar
    print(info)
    print("******************************** [<<ENTER>>=CONECTAR] ********************************")

    # Captura a tecla pressionada e verifica se é ENTER
    if readchar.readkey() == '\r': 
        print("******************************** [<<EXIT>>=SAIR] ********************************")

        # Inicia o cliente em uma thread separada
        tclient = threading.Thread(target=cliente.run)
        tclient.start()

        # Aguarda as threads do servidor e cliente finalizarem
        tserver.join()
        tclient.join()

        print("******************************** FIM CONECTADO ********************************")
        print(repr(readchar.readkey()))  # Exibe a tecla pressionada
    else:
        print("******************************** ABORT ANTES DE CONECTAR ********************************")

        # Fecha a conexão do cliente se abortado antes de conectar
        cliente.close()
        print(repr(readchar.readkey()))  # Exibe a tecla pressionada

if __name__ == '__main__':
    main()
