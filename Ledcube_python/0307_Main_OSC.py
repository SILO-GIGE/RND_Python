'''
여러개의 OSC신호를 보내는 코드
LED CUBE MAIN CONTROL OSC UI
시간을 입력하면 그 시간에 콘텐츠가 재생된다.

'''

import tkinter as tk
from pythonosc import udp_client, dispatcher, osc_server
from threading import Thread
from datetime import datetime,timedelta
import time
Main_port_num = 5557  # 윈도우 포트번호
Server1_port_num = 4206  # 시현 RND 라즈베리파이
Server2_port_num = 4207  # MDW 라즈베리파이1 포트번호
Server3_port_num = 4208  # MDW 라즈베리파이2 포트번호
contents_num=50  #반복할 숫자


def send_osc_signal(ip_address, port, value):
    client = udp_client.SimpleUDPClient(ip_address, port)
    client.send_message("/SILOKSH", value)

class OSCSenderApp:
    def __init__(self, master, ip1, ip2,ip3, port1, port2,port3):  # 서버를 지정.
        self.master = master
        self.num = 0  #콘텐츠를 반복할 횟수에 대한 변수 초기화
        self.timer_seconds = 0  # 타이머 초 초기화
        self.rasp1_state = 0
        self.rasp2_state = 0
        self.rasp3_state = 0

        self.ip_address1 = ip1
        self.ip_address2 = ip2
        self.ip_address3 = ip3
        self.port1 = port1
        self.port2 = port2
        self.port3 = port3

        master.title("SILO LED CUBE CONTROL UI")
        master.configure(bg="white")

        # UI 크기를 2배로 확대
        window_width = 1000
        window_height = 500
        master.geometry(f"{window_width}x{window_height}")

        self.label = tk.Label(master, text=" [ LED CUBE Control , Set start time]", font=("Arial", 30,"bold"),bg="white")
        self.label.pack()
        self.time_entry = tk.Entry(master, font=("Helvetica", 20,"bold"),bd=3, relief="solid")
        self.time_entry.insert(0, "Enter time")
        self.time_entry.config(fg="gray")
        self.time_entry.bind("<FocusIn>", self.on_entry_click)
        self.time_entry.bind("<FocusOut>", self.on_focus_out)
        self.time_entry.pack(pady=20)
        
        # '10초뒤' 버튼 추가
        self.ten_seconds_button = tk.Button(master, text="5s later", command=self.set_time_ten_seconds_later, width=10, height=1, font=("Helvetica", 15, "bold"))
        self.ten_seconds_button.pack()
        self.ten_seconds_button.place(x=700, y=70)  # 원하는 위치로 조정
        
        self.led_off_button = tk.Button(master, text="led off", command=self.led_off, width=10, height=1, font=("Helvetica", 15, "bold"))
        self.led_off_button.pack()
        self.led_off_button.place(x=850, y=70)  # 원하는 위치로 조정
        
        #확인버튼설정
        self.confirm_button = tk.Button(master, text="CONFIRM", command=self.confirm_time, width=30, height=2,
                                         font=("Helvetica", 20,"bold"))
        #종료버튼설정
        self.confirm_button.pack(pady=20)

        self.exit_button = tk.Button(master, text="EXIT", command=self.exit_program, width=30, height=2,
                                     font=("Helvetica", 20,"bold"))
        self.exit_button.pack(pady=20)

        self.status_label = tk.Label(master, text="", font=("Helvetica", 20,"bold"))
        self.status_label.pack()

        #현재시간표시


        self.current_time_label = tk.Label(master, text="", font=("Helvetica", 20))
        self.current_time_label.place(x=20, y=60)  # UI 왼쪽 상단에 배치

        self.last_signal = None

        # OSC서버설정
        self.server_ip = "0.0.0.0"
        self.server_port = Main_port_num
        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.map("/Rasp1", self.handle_osc_signal)
        self.dispatcher.map("/Rasp2", self.handle_osc_signal)
        self.dispatcher.map("/Rasp3", self.handle_osc_signal)
        self.server = osc_server.ThreadingOSCUDPServer((self.server_ip, self.server_port), self.dispatcher)
        self.server_thread = Thread(target=self.server.serve_forever)
        self.server_thread.start()

        # 타이머 변수 초기화
        self.timer = None

        # 현재 시간 업데이트 시작
        self.update_current_time()
    def on_entry_click(self, event):
        if self.time_entry.get() == "Enter time":
            self.time_entry.delete(0, tk.END)
            self.time_entry.config(fg="black")

    def on_focus_out(self, event):
        if not self.time_entry.get():
            self.time_entry.insert(0, "Enter time")
            self.time_entry.config(fg="gray")
    def confirm_time(self):
        # 입력된 시간
        entered_time = self.time_entry.get()
        try:
            entered_time_obj = datetime.strptime(entered_time, "%H:%M:%S")
        except ValueError:
            self.status_label.config(text="Invaild time format. Please enter again",bg="white")
            
            # 빨간색으로 깜빡이도록 설정
            self.status_label.after(50, lambda: self.status_label.config(fg="red"))
            self.blink_entry_background(self.time_entry,times=1)
            return

        # 현재 시간
        current_time = datetime.now().strftime("%H:%M:%S")
        
        if current_time == entered_time:
            self.send_led_signal(1)
            self.status_label.config(text="LED ON. CONTENTS PLAYING",fg="blue",bg="white")
            self.disable_buttons()
        elif current_time > entered_time:
            self.recheck_time()
        else:
            self.status_label.config(text="시간설정완료",fg="blue",bg="white")
            #self.status_label.place(x=600, y=00)  # 좌측 중간에 배치
            self.time_entry.config(bg="blue")  # 파란색으로 입력 창 배경색 변경
            self.status_label.after(1000, self.wait_for_match)

    def recheck_time(self):
        # 입력한 시간 초기화
        self.time_entry.delete(0, tk.END)
        # 오류 메시지 표시
        self.status_label.config(text="Entered time is earlier than current time. Please enter again", fg="red",bg="white")
        self.blink_entry_background(self.time_entry, times=1)
        # 확인 버튼을 다시 처음 상태로 설정
        self.confirm_button.config(command=self.confirm_time)   
    
    
    def blink_entry_background(self, entry_widget, color1="red", color2=None, delay=500, times=1):
        if color2 is None:
            color2 = entry_widget.cget("bg")  # 현재 배경색 가져오기
        for i in range(times):
            entry_widget.config(bg=color1)
            entry_widget.after(delay * (2*i + 1), lambda: entry_widget.config(bg=color2))
            entry_widget.after(delay * (2*i + 2), lambda: entry_widget.config(bg=color1))
        entry_widget.after(delay * (2*times + 1), lambda: entry_widget.config(bg=color2))  # 마지막으로 원래대로 돌아오도록 설정
    
    #시간이 일치할때까지 대기하는함수.
    def wait_for_match(self):
        self.status_label.config(text="대기중",bg="white")
        self.confirm_button.config(state=tk.DISABLED)
        self.exit_button.config(state=tk.DISABLED)
        self.time_entry.config(state=tk.DISABLED)
        self.ten_seconds_button.config(state=tk.DISABLED)
        self.led_off_button.config(state=tk.DISABLED)

        entered_time = self.time_entry.get()
        current_time = datetime.now().strftime("%H:%M:%S")
        if current_time == entered_time:
            
            self.send_led_signal(1)
            self.status_label.config(text="LED ON. CONTENTS PLAYING",fg="blue",bg="white")
            self.disable_buttons()
        else:
            self.status_label.after(1000, self.wait_for_match)

    def disable_buttons(self):
        self.confirm_button.config(state=tk.DISABLED)
        self.exit_button.config(state=tk.DISABLED)
        self.ten_seconds_button.config(state=tk.DISABLED)
        self.led_off_button.config(state=tk.DISABLED)

    def enable_buttons(self):
        self.confirm_button.config(state=tk.NORMAL)
        self.exit_button.config(state=tk.NORMAL)
        self.ten_seconds_button.config(state=tk.NORMAL)
        self.led_off_button.config(state=tk.NORMAL)

    def send_led_signal(self, value):
        send_osc_signal(self.ip_address1, self.port1, value)
        send_osc_signal(self.ip_address2, self.port2, value)
        send_osc_signal(self.ip_address3, self.port3, value)
        self.last_signal = value
        self.update_status_label()
    
    def update_status_label(self):
        if self.last_signal is not None:
            if self.last_signal == 1:
                status_text = " LED ON (값: 1, 주소: /SILOKSH)"
            else:
                status_text = " LED OFF (값: 0, 주소: /SILOKSH)"
            self.status_label.config(text=status_text)
    #global i
    
    def handle_osc_signal(self, address, *args):
        
        if address == "/Rasp1" and args[0] == 3 and self.last_signal == 1:
            self.rasp1_state = 1
            #print("111")
        if address == "/Rasp2" and args[0] == 4 and self.last_signal == 1:
            self.rasp2_state = 1
            #print("222")
        if address == "/Rasp3" and args[0] == 5 and self.last_signal == 1:
            self.rasp3_state = 1
            #print("333")
        
        if self.rasp1_state * self.rasp2_state * self.rasp3_state == 1 and self.num <contents_num-1:
            self.send_led_signal(1)
            print(self.num)
            self.num +=1
            self.rasp1_state = 0
            self.rasp2_state = 0
            self.rasp3_state = 0
            
        if self.rasp1_state * self.rasp2_state * self.rasp3_state == 1 and self.num ==contents_num-1:
            self.enable_buttons()
            self.num=0
            # 다시 처음 상태로 돌아가기 위해 시간 입력 창을 활성화하고 대기 상태 메시지를 지우기
            self.time_entry.config(state=tk.NORMAL)
            self.time_entry.delete(0, tk.END)
            self.time_entry.insert(0, "Enter time")
            self.time_entry.config(fg="gray",bg="white")
            self.status_label.config(text="", bg="white")
            self.send_led_signal(0)
            self.rasp1_state = 0
            self.rasp2_state = 0
            self.rasp3_state = 0
            print("all receive DONE!!") 
        
    # 종료버튼을 누르면 실행되는 함수
    def exit_program(self):
        self.send_led_signal(0) #종료하기전 0을 보낸다.
        self.server.shutdown()
        self.master.destroy()

    def update_current_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.current_time_label.config(text=f"Current Time: {current_time}",bg="white")
        self.current_time_label.place(x=20, y=70)  # UI 왼쪽 상단으로부터 좀 아래로 이동
        self.master.after(1000, self.update_current_time)  # 1초마다 현재 시간 갱신
        
    #10초뒤 시간이 자동입력
    def set_time_ten_seconds_later(self):
        current_time = datetime.now()
        ten_seconds_later = current_time + timedelta(seconds=5)
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, ten_seconds_later.strftime("%H:%M:%S"))
    def led_off(self):
        self.send_led_signal(0)
        
if __name__ == "__main__":
    Rasp1_address = "192.168.50.233" #CUBE1 시현RND 라즈베리파이
    Rasp2_address = "192.168.50.240" #CUBE2 MDW 라즈베리파이1
    Rasp3_address = "192.168.50.160" #CUBE3 MDW 라즈베리파이2
    port1 = Server1_port_num
    port2 = Server2_port_num
    port3 = Server3_port_num
    
    root = tk.Tk()
    app = OSCSenderApp(root, Rasp1_address, Rasp2_address,Rasp3_address, port1, port2, port3)
    # 윈도우 창이 닫힐 때 프로그램 종료를 위한 설정
    root.protocol("WM_DELETE_WINDOW", app.exit_program)
    root.mainloop()