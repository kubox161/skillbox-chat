#  Created by Roman Babenko
#  kubox61@gmail.com
#  Copyright (c) 2019

#  Сервер для обработки сообщений от клиентов
#
#  Ctrl + Alt + L - форматирование кода
#
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory, connectionDone
from twisted.protocols.basic import LineOnlyReceiver


class ServerProtocol(LineOnlyReceiver):
    factory: 'Server'
    login: str = None
    history: list = []

    def connectionMade(self):
        # Потенциальный баг для внимательных =)
        self.factory.clients.append(self)
        print("Connected")

    def connectionLost(self, reason=connectionDone):
        self.factory.clients.remove(self)
        print("Disconnected")

    def lineReceived(self, line: bytes):
        content = line.decode()

        if self.login is not None:
            content = f"Message from {self.login}: {content}"
            self.history.append(content)
            for user in self.factory.clients:
                if user is not self:
                    user.sendLine(content.encode())
        else:
            # login:admin -> admin
            if content.startswith("login:"):
                self.login = content.replace("login:", "")
                print(self.login)
                for log in self.factory.log_user:
                    print(log)
                    if log == self.login:
                        self.sendLine(f"Логин {self.login} занят, попробуйте другой".encode())
                        # ServerProtocol.connectionLost(self)
                self.factory.log_user.append(f"{self.login}")
                self.sendLine("Welcome!".encode())
                self.send_history()
                # self.sendLine(f"{self.login}".encode())
                # if self.login is not self.factory.logins:

            else:
                self.sendLine("Invalid login".encode())
    def send_history(self):
        x = 0
        for hist in self.history[:-1]:
            if x < 10:
                self.sendLine(f"{hist}".encode())
                x += 1
            else:
                break



class Server(ServerFactory):
    protocol = ServerProtocol
    clients: list
    log_user: list

    def startFactory(self):
        self.clients = []
        self.log_user = [None]
        print("Server started")

    def stopFactory(self):
        print("Server closed")


reactor.listenTCP(1234, Server())
reactor.run()
