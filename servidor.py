# servidor.py

import socket
import socketserver
import sys

class Servidor:
    prompt = "HOST"
    
    def __init__(self, _info):
        self.info = _info
        self.finger_table = self.info.calculate_finger_table()
        Servidor.prompt = self.info.host_name   
        self.resources = {}
    
    def run(self):
        with socketserver.TCPServer((self.info.HOST_SERVER, self.info.PORT_SERVER), lambda request, client_address, server: ComunicadorTCPHandler(request, client_address, server, self.info, self.finger_table)) as server:
            try:
                server.serve_forever()
            finally:
                server.shutdown()  # Garantir que o servidor seja desligado corretamente

# Handler para processar as conexões recebidas
class ComunicadorTCPHandler(socketserver.BaseRequestHandler):
    
    def __init__(self, request, client_address, server, info, finger_table):
        self.info = info  # Armazena a informação passada
        self.finger_table = finger_table  # Armazena a Finger Table
        super().__init__(request, client_address, server)  # Chama o construtor da classe base
    
    def add_resource(self, resource_name, resource_data):
        comando = "upload"
        message = ""

        if resource_name in self.resources:
            message = f"Falha ao adicionar o recurso '{resource_name}'. Recurso já existente !"
        else:
            self.resources[resource_name] = resource_data
            message = f"Recurso '{resource_name}' adicionado com sucesso."

        return f"[{comando}, {message}]"

    def get_resource(self, resource_name):
        comando = "download"
        message = ""

        if resource_name in self.resources:
            resource_data = self.resources[resource_name]
            message = f"Baixando recurso {resource_name}"
            return f"[{comando}, {message}, {resource_data}]"
        else:
            message = f"Recurso '{resource_name}' não encontrado ou inexistente."
            return f"[{comando}, {message}]"

    def handle(self):
        run, msg = True, ""
        while run:
            try:
                # Recebe e decodifica a mensagem do cliente
                self.data = self.request.recv(4096).strip()
                msg = self.data.decode('utf-8')
                
                # Exibe a mensagem recebida
                print(f"PEER: {self.client_address[0]}, Mensagem: {msg}\n{Servidor.prompt}:>> ", end="")
                
                # Processa a mensagem recebida
                k, ip, porta, comando = self.process_message(msg)

                if comando.startswith("detentor"):
                    # Verifica se este nó é o detentor da chave
                    if self.is_detentor(k):
                        comando = "detentor"
                        message = f"Eu sou o detentor da chave {k}"
                        response = f"[{comando}, {message}]"
                        self.request.sendall(response.encode('utf-8'))
                    else:
                        # Encaminha a mensagem para o próximo nó
                        self.forward_message(msg, k)

                elif comando.startswith("upload"):
                    # Tratamento de upload de recurso
                    resource_name = comando.split(" ")[1]
                    resource_data = comando.split(" ")[2]

                    response = self.add_resource(resource_name, resource_data)

                    self.request.sendall(response.encode('utf-8'))
                    
                elif comando.startswith("download"):
                    # Tratamento de download de recurso
                    resource_name = comando.split(" ")[1]

                    response = self.get_resource(resource_name, resource_data)
                    
                    self.request.sendall(response.encode('utf-8'))
                
            except Exception as e:
                print(f"******************************** CONNECTION DOWN: {e} ********************************")
                sys.exit()
            
            if msg.strip().lower() == "exit":
                print(f"Antecessor({Servidor.prompt}) saiu (e informou)!!!")   
                sys.exit()

    def process_message(self, msg):
        """
        Processa a mensagem recebida no formato [K, IP, PORTA, COMANDO].
        Retorna K, IP, PORTA e COMANDO.
        """
        msg = msg.strip("[]")
        parts = msg.split(", ")
        k = int(parts[0])
        ip = parts[1]
        porta = int(parts[2])
        comando = parts[3]
        
        return k, ip, porta, comando

    def is_detentor(self, k):
        """
        Verifica se este nó é o detentor da chave K, baseado no intervalo de chaves para o qual é responsável.
        """
        return self.info.RANGE_START <= k <= self.info.RANGE_END

    def forward_message(self, msg, k):
        """
        Encaminha a mensagem para o próximo nó na rede (sucessor) baseado na Finger Table.
        """
        try:
            # Encontra o próximo nó com base na Finger Table
            next_node = self.find_next_node(k)
            
            if next_node:
                next_ip, next_port = next_node
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((next_ip, next_port))
                    s.sendall(msg.encode('utf-8'))
                    print(f"Mensagem {msg} encaminhada para o nó {next_ip}:{next_port}")
            else:
                print(f"Nó para chave {k} não encontrado na Finger Table.")
        except Exception as e:
            print(f"Erro ao encaminhar a mensagem para o sucessor: {e}")

    def find_next_node(self, k):
        """
        Encontra o próximo nó na Finger Table baseado na chave K.
        """
        for finger in sorted(self.finger_table):
            if finger > self.info.PORT_SERVER and finger <= k:
                return self.info.HOST_SERVER, self.info.SUCESSOR
        
        return None
