import tkinter as tk
from pythonosc import udp_client, dispatcher, osc_server
from threading import Thread

Main_port_num = 5557  # 윈도우 포트번호
Server1_port_num = 4208  # 라즈베리파이1 포트번호
Server2_port_num = 4209  # 라즈베리파이2 포트번호

def send_osc_signal(ip_address, port, value):
    client = udp_client.SimpleUDPClient(ip_address, port)
    client.send_message("/SILOKSH", value)

class OSCSenderApp:
    def __init__(self, master, ip1, ip2, port1, port2):
        self.master = master
        self.ip_address1 = ip1
        self.ip_address2 = ip2
        self.port1 = port1
        self.port2 = port2

        master.title("OSC Sender App")

        # UI 크기를 2배로 확대
        window_width = 2000
        window_height = 1300
        master.geometry(f"{window_width}x{window_height}")

        self.label = tk.Label(master, text=" [ LED CUBE Control , Push Button]", font=("Helvetica", 20))
        self.label.pack()

        self.all_cube_on_button = tk.Button(master, text="ALL CUBE ON", command=self.send_all_cube_signal,
                                             width=10, height=3, font=("Helvetica", 20))
        self.all_cube_on_button.pack(pady=10)

        self.cube1_on_button = tk.Button(master, text="CUBE1 ON", command=self.send_cube1_on_signal, width=10,
                                          height=3, font=("Helvetica", 20))
        self.cube1_on_button.pack(pady=10)

        self.cube2_on_button = tk.Button(master, text="CUBE2 ON", command=self.send_cube2_on_signal, width=10,
                                          height=3, font=("Helvetica", 20))
        self.cube2_on_button.pack(pady=10)

        self.cube1_off_button = tk.Button(master, text="CUBE1 OFF", command=self.send_cube1_off_signal, width=10,
                                           height=3, font=("Helvetica", 20))
        self.cube1_off_button.pack(pady=10)

        self.cube2_off_button = tk.Button(master, text="CUBE2 OFF", command=self.send_cube2_off_signal, width=10,
                                           height=3, font=("Helvetica", 20))
        self.cube2_off_button.pack(pady=10)

        self.exit_button = tk.Button(master, text="EXIT", command=self.exit_program,
                                     width=10, height=3, font=("Helvetica", 20))
        self.exit_button.pack(pady=10)

        self.status_label = tk.Label(master, text="")
        self.status_label.pack()

        self.last_signal = None

        # OSC서버설정
        self.server_ip = "0.0.0.0"
        self.server_port = Main_port_num
        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.map("/Rasp1", self.handle_osc_signal)
        self.dispatcher.map("/Rasp2", self.handle_osc_signal)
        self.server = osc_server.ThreadingOSCUDPServer((self.server_ip, self.server_port), self.dispatcher)
        self.server_thread = Thread(target=self.server.serve_forever)
        self.server_thread.start()

    def send_all_cube_signal(self):
        send_osc_signal(self.ip_address1, self.port1, 1)
        send_osc_signal(self.ip_address2, self.port2, 1)
        self.last_signal = 1
        self.update_status_label()
        self.disable_buttons()

    def send_cube1_on_signal(self):
        send_osc_signal(self.ip_address1, self.port1, 1)
        self.last_signal = 1
        self.update_status_label()
        self.disable_buttons()

    def send_cube2_on_signal(self):
        send_osc_signal(self.ip_address2, self.port2, 1)
        self.last_signal = 1
        self.update_status_label()
        self.disable_buttons()

    def send_cube1_off_signal(self):
        send_osc_signal(self.ip_address1, self.port1, 0)
        self.last_signal = 0
        self.update_status_label()
        self.enable_buttons()

    def send_cube2_off_signal(self):
        send_osc_signal(self.ip_address2, self.port2, 0)
        self.last_signal = 0
        self.update_status_label()
        self.enable_buttons()

    def disable_buttons(self):
        self.all_cube_on_button.config(state=tk.DISABLED)
        self.cube1_on_button.config(state=tk.DISABLED)
        self.cube2_on_button.config(state=tk.DISABLED)
        self.exit_button.config(state=tk.DISABLED)

    def enable_buttons(self):
        self.all_cube_on_button.config(state=tk.NORMAL)
        self.cube1_on_button.config(state=tk.NORMAL)
        self.cube2_on_button.config(state=tk.NORMAL)
        self.exit_button.config(state=tk.NORMAL)

    def update_status_label(self):
        if self.last_signal is not None:
            status_text = f"현재 OSC 신호: Rasp1: /SILOKSH {self.last_signal}, Rasp2: /SILOKSH {self.last_signal}"
            self.status_label.config(text=status_text)

    def handle_osc_signal(self, address, *args):
        if (address == "/Rasp1" and args[0] == 3) or (address == "/Rasp2" and args[0] == 4):
            self.enable_buttons()
            if self.last_signal == 1:
                self.all_cube_on_button.config(state=tk.NORMAL)
                self.exit_button.config(state=tk.NORMAL)

    # 종료버튼을 누르면 실행되는 함수
    def exit_program(self):
        self.server.shutdown()
        self.master.destroy()

if __name__ == "__main__":
    Ras1_address = "192.168.0.11"
    Ras2_address = "192.168.0.9"
    port1 = Server1_port_num
    port2 = Server2_port_num

    root = tk.Tk()
    app = OSCSenderApp(root, Ras1_address, Ras2_address, port1, port2)
    root.mainloop()
