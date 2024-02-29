import tkinter as tk
from pythonosc import udp_client, dispatcher, osc_server
from threading import Thread
from datetime import datetime

Main_port_num = 5557  # 윈도우 포트번호
Server1_port_num = 4206  # 라즈베리파이 포트번호
Server2_port_num = 4209  # 라즈베리파이 포트번호

def send_osc_signal(ip_address, port, value):
    client = udp_client.SimpleUDPClient(ip_address, port)
    client.send_message("/SILOKSH", value)

class OSCSenderApp:
    def __init__(self, master, ip1, ip2, port1, port2):  # 서버를 지정.
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

        self.label = tk.Label(master, text=" [ LED CUBE Control , Set Time and Confirm]", font=("Helvetica", 24))
        self.label.pack()

        self.time_entry = tk.Entry(master, font=("Helvetica", 20))
        self.time_entry.pack(pady=20)

        self.confirm_button = tk.Button(master, text="확인", command=self.confirm_time, width=30, height=5,
                                         font=("Helvetica", 20))
        self.confirm_button.pack(pady=20)

        self.exit_button = tk.Button(master, text="종료", command=self.exit_program, width=30, height=5,
                                     font=("Helvetica", 20))
        self.exit_button.pack(pady=20)

        self.status_label = tk.Label(master, text="", font=("Helvetica", 20))
        self.status_label.pack()

        self.current_time_label = tk.Label(master, text="", font=("Helvetica", 20))
        self.current_time_label.place(x=20, y=20)  # UI 왼쪽 상단에 배치

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

        # 타이머 변수 초기화
        self.timer = None

        # 현재 시간 업데이트 시작
        self.update_current_time()

    def confirm_time(self):
        # 입력된 시간
        entered_time = self.time_entry.get()
        try:
            entered_time_obj = datetime.strptime(entered_time, "%H:%M:%S")
        except ValueError:
            self.status_label.config(text="시간 형식이 잘못되었습니다. 다시 입력해주세요.")
            return

        # 현재 시간
        current_time = datetime.now().strftime("%H:%M:%S")

        if current_time == entered_time:
            self.send_led_signal(1)
            self.status_label.config(text="LED를 켰습니다.")
            self.disable_buttons()
        else:
            self.status_label.config(text="설정한 시간과 현재 시간이 일치하지 않습니다.")
            self.status_label.after(1000, self.wait_for_match)

    def wait_for_match(self):
        self.status_label.config(text="대기중")
        self.confirm_button.config(state=tk.DISABLED)
        self.exit_button.config(state=tk.DISABLED)

        entered_time = self.time_entry.get()
        current_time = datetime.now().strftime("%H:%M:%S")
        if current_time == entered_time:
            self.send_led_signal(1)
            self.status_label.config(text="LED를 켰습니다.")
            self.disable_buttons()
        else:
            self.status_label.after(1000, self.wait_for_match)

    def disable_buttons(self):
        self.confirm_button.config(state=tk.DISABLED)
        self.exit_button.config(state=tk.DISABLED)

    def enable_buttons(self):
        self.confirm_button.config(state=tk.NORMAL)
        self.exit_button.config(state=tk.NORMAL)

    def send_led_signal(self, value):
        send_osc_signal(self.ip_address1, self.port1, value)
        send_osc_signal(self.ip_address2, self.port2, value)
        self.last_signal = value
        self.update_status_label()

    def update_status_label(self):
        if self.last_signal is not None:
            if self.last_signal == 1:
                status_text = " LED ON (값: 1, 주소: /SILOKSH)"
            else:
                status_text = " LED OFF (값: 0, 주소: /SILOKSH)"
            self.status_label.config(text=status_text)

    def handle_osc_signal(self, address, *args):
        if address == "/Rasp1" and args[0] == 3 and self.last_signal == 1:
            self.send_led_signal(0)
            self.enable_buttons()
        if address == "/Rasp2" and args[0] == 4 and self.last_signal == 1:
            self.send_led_signal(0)
            self.enable_buttons()

    # 종료버튼을 누르면 실행되는 함수
    def exit_program(self):
        self.server.shutdown()
        self.master.destroy()

    def update_current_time(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.current_time_label.config(text=f"현재 시간: {current_time}")
        self.master.after(1000, self.update_current_time)  # 1초마다 현재 시간 갱신

if __name__ == "__main__":
    Rasp1_address = "192.168.0.5"
    Rasp2_address = "192.168.0.4"
    port1 = Server1_port_num
    port2 = Server2_port_num

    root = tk.Tk()
    app = OSCSenderApp(root, Rasp1_address, Rasp2_address, port1, port2)
    root.mainloop()
