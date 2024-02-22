from pythonosc import udp_client
import tkinter as tk
    
    
def send_osc_signal(ip_address, port, value):
    client = udp_client.SimpleUDPClient(ip_address, port)
    client.send_message("/SILOKSH", value)
    
    
if __name__ == "__main__":
    ip_address = "192.168.0.11" #라즈베리파이IP주소
    port = 4301  
    
    # 사용자로부터 값을 입력 받음
    while True:
        try:
            user_input = int(input("보낼 값을 입력하세요 (0 또는 1): "))
            if user_input == 'q':
                break
            elif user_input not in [0, 1]:
                raise ValueError("0 또는 1을 입력하세요.")
            
            # OSC 신호 전송
            send_osc_signal(ip_address, port, user_input)
        except ValueError as e:
            print(e)