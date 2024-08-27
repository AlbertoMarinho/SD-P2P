# cliente.py

import socket  # Biblioteca para comunicação via sockets

class Cliente:
    def __init__(self, _info):
        # Inicializa o socket e define o estado de conexão como False
        self.sc = socket.socket()
        self.info = _info
        self.connected = False
        self.prompt = self.info.host_name + ":>> "
        self.resource_data = {}

    def run(self):
        # Abre a conexão com o servidor
        self.open()

        # Loop principal para enviar e receber mensagens
        while True:
            msg = input(str(self.prompt)).strip()

            if msg:
                self.send(msg)
                self.receive()
                msg.lower()

                # Sai do loop se o comando for 'exit'
                if msg == 'exit':
                    break

    def process_message(self, msg):
        parts = msg.split(", ")

        comando = parts[0]

        if comando in ["detentor", "download"]:
            message = parts[1] if len(parts) > 1 else ""
            return comando, message, None

        elif comando == "upload":
            resource_name = parts[1]
            data = ",".join(parts[2:])  # Os dados podem conter vírgulas
            return comando, resource_name, data.encode('latin1')  # Ou 'utf-8' dependendo da codificação usada

        return None, None, None

    def send(self, msg):
        k = 28  # Chave K que você quer procurar
        hostname = self.info.HOST_SERVER
        portnumber = self.info.SPORT

        if self.connected:
            if msg.startswith("detentor"):
                comando = "detentor"
                protocol_msg = f"[{k}, {hostname}, {portnumber}, {comando}]"
                self.sc.sendall(protocol_msg.encode('utf-8'))

            elif msg.startswith("upload"):
                _, resource_name, file_path = msg.split(" ")

                with open(file_path, 'rb') as f:
                    resource_data = f.read()
                    comando = f"upload {resource_name} {resource_data}"
                    
                    protocol_msg = f"[{k}, {hostname}, {portnumber}, {comando}]"
                    self.sc.sendall(comando.encode('utf-8'))

            elif msg.startswith("download"):
                _, resource_name = msg.split(" ")
                comando = f"download {resource_name}"

                protocol_msg = f"[{k}, {hostname}, {portnumber}, {comando}]"
                self.sc.sendall(comando.encode('utf-8'))
                
            else:
                print("Comando invalido !")

    def receive(self):
        if self.connected:
            data = self.sc.recv(4096).strip()
            msg = data.decode('utf-8')
            
            comando, message, data = self.process_message(msg)
            
            if(comando == "detentor"):
                print(message)
            elif (comando == "upload"):
                print(message)
            elif (comando == "download"):
                print(message)
                with open('download_file', 'wb') as f:
                    f.write(data)

    def close(self):
        # Fecha a conexão com o servidor
        if self.connected:
            self.send("exit")
            self.receive()
            self.sc.close()
            self.connected = False

    def open(self):
        if not self.connected:
            try:
                # Tenta se conectar ao servidor
                self.sc.connect((self.info.HOST_SERVER, self.info.SUCESSOR))
                self.connected = True
            except IOError:
                # Exibe uma mensagem de erro caso a conexão falhe
                print(f"SUCESSOR({self.info.sucessor_name}), Host({self.info.HOST_SERVER}), PORTA({str(self.info.SUCESSOR)}) Falhou!!!")
                self.connected = False
