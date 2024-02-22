import tkinter as tk
from pythonosc import udp_client, dispatcher,osc_server
from threading import Thread

Main_port_num=5557 #윈도우 포트번호
Server1_port_num=4208 #라즈베리파이 포트번호

def send_osc_signal(ip_address, port, value):
    client = udp_client.SimpleUDPClient(ip_address, port)
    client.send_message("/SILOKSH", value)

class OSCSenderApp:
    def __init__(self, master, ip_address, port):
        self.master = master
        self.ip_address = ip_address
        self.port = port
        
        master.title("OSC Sender App")
        
        # UI 크기를 2배로 확대
        window_width = 600
        window_height = 400
        master.geometry(f"{window_width}x{window_height}")
        
        self.label = tk.Label(master, text="보낼 값을 선택하세요:")
        self.label.pack()
        
        self.led_on_button = tk.Button(master, text="LED ON", command=lambda: self.send_led_signal(1), width=15, height=5)
        self.led_on_button.pack(pady=10)
        
        self.led_off_button = tk.Button(master, text="LED OFF", command=lambda: self.send_led_signal(0), width=15, height=5)
        self.led_off_button.pack(pady=10)
        
        self.exit_button = tk.Button(master, text="종료", command=self.exit_program, width=15, height=5)
        self.exit_button.pack(pady=10)
        
        self.status_label = tk.Label(master, text="")
        self.status_label.pack()
        
        self.last_signal = None
    
        #OSC서버설정
        self.server_ip="0.0.0.0"
        self.server_port=Main_port_num
        self.dispatcher=dispatcher.Dispatcher()
        self.dispatcher.map("/Rasp", self.handle_osc_signal)
        self.server = osc_server.ThreadingOSCUDPServer((self.server_ip, self.server_port), self.dispatcher)
        self.server_thread = Thread(target=self.server.serve_forever)
        self.server_thread.start()
        
        
    def send_led_signal(self, value):
        send_osc_signal(self.ip_address, self.port, value)
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
            if self.last_signal == 1:
                status_text = "현재상태 : LED ON (값: 1, 주소: /SILOKSH)"
            else:
                status_text = "현재상태 : LED OFF (값: 0, 주소: /SILOKSH)"
            self.status_label.config(text=status_text)
    
    def handle_osc_signal(self, address, *args):
        if address == "/Rasp" and args[0] == 3:
            self.led_on_button.config(state=tk.NORMAL)
            self.led_off_button.config(state=tk.NORMAL)
            self.exit_button.config(state=tk.NORMAL)
            
    
    #종료버튼을 누르면 실행되는 함수    
    def exit_program(self):
        #send_osc_signal(self.ip_address, self.port, "E")  # 종료 신호를 보냄
        self.server.shutdown()
        self.master.destroy()

if __name__ == "__main__":
    ip_address = "192.168.0.11"
    port = Server1_port_num
    
    root = tk.Tk()
    app = OSCSenderApp(root, ip_address, port)
    root.mainloop()
