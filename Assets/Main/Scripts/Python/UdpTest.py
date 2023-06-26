import socket
import json
import time


def server_close():
    print("closing socket")
    sock.close()
    print("done")


# Serverのアドレスを用意。Serverのアドレスは確認しておく必要がある。
SOCKET_SETTING = ("127.0.0.1", 10800)

# ①ソケットを作成する
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

array = [0, 1, 2, 3]
message = {}
message["array"] = array
while True:
    try:
        # ②messageを送信する
        print("Input any messages, Type [end] to exit")
        if message != "end":
            send_len = sock.sendto(json.dumps(message).encode("utf-8"), SOCKET_SETTING)
            time.sleep(1)
            # ※sendtoメソッドはkeyword arguments(address=serv_addressのような形式)を受け付けないので注意

            # ③Serverからのmessageを受付開始
            # print('Waiting response from Server')
            # rx_meesage, addr = sock.recvfrom(M_SIZE)
            # print(f"[Server]: {rx_meesage.decode(encoding='utf-8')}")

        else:
            server_close()
            break

    except KeyboardInterrupt:
        server_close
        break
