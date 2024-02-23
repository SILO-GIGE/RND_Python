import tkinter as tk
from pythonosc import udp_client, dispatcher,osc_server
from threading import Thread

Main_port_num=5557 #윈도우 포트번호
Server1_port_num=4208 #라즈베리파이 포트번호
Server2_port_num=4209 #라즈베리파이 포트번호


def send_osc_signal(ip_address, port, value):
    client = udp_client.SimpleUDPClient(ip_address, port)
    client.send_message("/SILOKSH", value)

class OSCSenderApp:
    def __init__(self, master, ip1, ip2, port1, port2): # 서버를 지정. 
        self.master = master
        self.ip_address1 = ip1
        self.ip_address2 = ip2
        self.port1 = port1
        self.port2 = port2
        
        master.title("SILO LED CUBE OSC")
        
        # UI 크기를 2배로 확대
        window_width = 1200
        window_height = 800
        master.geometry(f"{window_width}x{window_height}")
        
        self.label = tk.Label(master, text=" [ LED CUBE Control , Push Button]", font=("Helvetica", 20))
        self.label.pack()
        
        self.led_on_button = tk.Button(master, text="LED ON", command=lambda: self.send_led_signal(1), width=30, height=5, font=("Helvetica", 20))
        self.led_on_button.pack(pady=20)
        
        self.led_off_button = tk.Button(master, text="LED OFF", command=lambda: self.send_led_signal(0),  width=30, height=5, font=("Helvetica", 20))
        self.led_off_button.pack(pady=20)
        
        self.exit_button = tk.Button(master, text="종료", command=self.exit_program,  width=30, height=5, font=("Helvetica", 20))
        self.exit_button.pack(pady=20)
        
        self.status_label = tk.Label(master, text="")
        self.status_label.pack()
        
        self.last_signal = None
    
        #OSC서버설정
        self.server_ip="0.0.0.0"
        self.server_port=Main_port_num
        self.dispatcher=dispatcher.Dispatcher()
        self.dispatcher.map("/Rasp1", self.handle_osc_signal)
        self.dispatcher.map("/Rasp2", self.handle_osc_signal)
        self.server = osc_server.ThreadingOSCUDPServer((self.server_ip, self.server_port), self.dispatcher)
        self.server_thread = Thread(target=self.server.serve_forever)
        self.server_thread.start()
        
        
    def send_led_signal(self, value):
        send_osc_signal(self.ip_address1, self.port1, value)
        send_osc_signal(self.ip_address2, self.port2, value)
        self.last_signal = value
        self.update_status_label()
        if value == 1:
            self.led_on_button.config(state=tk.DISABLED)
            self.led_off_button.config(state=tk.DISABLED)
            self.exit_button.config(state=tk.DISABLED)
        else:
            self.led_on_button.config(state=tk.NORMAL)
            self.led_off_button.config(state=tk.NORMAL)
            self.exit_button.config(state=tk.NORMAL)
    
    def update_status_label(self):
        if self.last_signal is not None:
            if self.last_signal is not None:
                status_text = f"현재 OSC 신호: Rasp1: /SILOKSH {self.last_signal}, Rasp2: /SILOKSH {self.last_signal}"
                
            if self.last_signal == 1:
                status_text = " LED ON (값: 1, 주소: /SILOKSH)"
            else:
                status_text = " LED OFF (값: 0, 주소: /SILOKSH)"
            self.status_label.config(text=status_text)
    
    def handle_osc_signal(self, address, *args):
        if address == "/Rasp1" and args[0] == 3  and self.last_signal == 1:
            self.led_on_button.config(state=tk.NORMAL)
            self.led_off_button.config(state=tk.NORMAL)
            self.exit_button.config(state=tk.NORMAL)
        if address == "/Rasp2" and args[0] == 4 and self.last_signal == 1:
            self.led_on_button.config(state=tk.NORMAL)
            self.led_off_button.config(state=tk.NORMAL)
            self.exit_button.config(state=tk.NORMAL)
            
    
    #종료버튼을 누르면 실행되는 함수    
    def exit_program(self):
        #send_osc_signal(self.ip_address, self.port, "E")  # 종료 신호를 보냄
        self.server.shutdown()
        self.master.destroy()

if __name__ == "__main__":
    Rasp1_address = "192.168.0.11"
    Rasp2_address = "192.168.0.9"
    port1 = Server1_port_num
    port2 = Server2_port_num
    
    root = tk.Tk()
    app = OSCSenderApp(root, Rasp1_address, Rasp2_address, port1,port2)
    root.mainloop()
