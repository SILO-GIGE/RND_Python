from pythonosc import udp_client\
    
if __name__ == "__main__":

    client = udp_client.SimpleUDPClient("192.168.0.11",4301) #라즈베리파이 IP주소와 보낼 포트번호를 입력한다.
    client.send_message("/SILOKSH", 0) #숫자 1을 라즈베리파이로 전송한다.