import sys


class DataCom:
    SHOST = "localhost"  # Static: DataCom.SHOST
    SPORT = 3000         # Static: DataCom.SPORT
    FAIXA = 100

    def __init__(self, filename: str, numero_de_pares: int) -> None:
        if numero_de_pares <= 0:
            numero_de_pares = 1

        self.SIZE = numero_de_pares
        self.MAP = []

        # Configuração da lista MAP com pares de portas
        for a in range(self.SIZE):
            server_port, client_port = a, (a + 1)
            if client_port < self.SIZE:
                self.MAP.append([server_port, client_port])
            else:
                self.MAP.append([server_port, 0])

        self.IdxMap = self.__config_ports(filename)

        # Inicializando os atributos NEXT_IP e NEXT_PORT
        self.NEXT_IP = DataCom.SHOST
        self.NEXT_PORT = self.SUCESSOR

    def __config_ports(self, filename: str) -> int:
        _port = -1

        try:
            # Lê e atualiza a porta do arquivo
            with open(filename, 'r') as f:
                _port = int(f.read())

            with open(filename, 'w') as f:
                f.write(str(_port + 1))

        except IOError:
            print("Erro ao ler ou gravar o arquivo!!")
            sys.exit()

        # Calcula o índice e as portas
        I = _port % self.SIZE
        self.HOST_SERVER = DataCom.SHOST
        self.PORT_SERVER = self.MAP[I][0] * DataCom.FAIXA + DataCom.SPORT
        self.SUCESSOR = self.MAP[I][1] * DataCom.FAIXA + DataCom.SPORT

        # Nome do sucessor e do servidor
        self.sucessor_name = f"NO[{self.SUCESSOR}]"
        self.host_name = f"NO[{self.PORT_SERVER}]"

        # Calcula o antecessor
        Ant_I = I - 1 if I - 1 >= 0 else self.SIZE - 1
        self.antecessor_name = f"NO[{self.MAP[Ant_I][0] * DataCom.FAIXA + DataCom.SPORT}]"

        # Configura a faixa
        self.setF(I)
        return I

    def __repr__(self) -> str:
        return (
            f"Servidor ({self.HOST_SERVER}), "
            f"PortServer({self.PORT_SERVER}), "
            f"SUCESSOR({self.SUCESSOR} -> FAIXA[{self.RANGE_START} - {self.RANGE_END}]), ...."
            f"\nCliente vai conectar assim: ESCUTA({self.HOST_SERVER}), SUCESSOR({self.SUCESSOR}) ok!!"
        )

    def setF(self, I: int) -> None:
        self.RANGE_START = self.SUCESSOR - DataCom.SPORT - DataCom.FAIXA + 1
        self.RANGE_END = self.SUCESSOR - DataCom.SPORT

        if I + 1 == self.SIZE:
            self.RANGE_START = self.PORT_SERVER - DataCom.SPORT + 1  # Caso a Faixa Final até Zero

    def calculate_finger_table(self) -> list:
        """
        Calcula a Finger Table para o nó atual.
        """
        finger_table = []
        m = 7  # Número máximo de bits, assumido como 7 para este exemplo
        for j in range(m):
            finger = (self.PORT_SERVER + 2 ** j) % (2 ** m)
            finger_table.append(finger)
        return finger_table
