
from multiprocessing.connection import Listener, Client
from threading import Thread, Event

P = None

class Proxy():

    def __init__(self, addr=('127.0.0.1', 9999)):
        global P
        self.__addr = addr
        self.__pipe = None
        self.__is_alive = False
        self.__t = None
        self.__signal_evt = None
        self.__msg = None
        P = self

    def start(self):
        self.__pipe = Listener(self.__addr)
        self.__signal_evt = Event()
        self.__t = Thread(target=self.__listener_worker)
        self.__t.start()

    def send(self, msg):
        if self.__is_alive:
            self.__msg = msg
            self.__signal_evt.set()

    def close(self):
        self.__msg = 'KILL'
        with Client(self.__addr) as c:
            self.__signal_evt.set()

        self.__t.join()



    def __listener_worker(self):
        while self.__msg != 'KILL':
            with self.__pipe.accept() as conn:
                self.__is_alive = True
                while self.__is_alive:
                    self.__signal_evt.wait()
                    self.__signal_evt.clear()
                    if self.__msg == 'KILL':
                        self.__is_alive = False
                    else:
                        try:
                            conn.send(self.__msg)
                        except (EOFError, BrokenPipeError, ConnectionResetError):
                            self.__is_alive = False

                