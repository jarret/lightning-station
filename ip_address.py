import socket

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
    except:
        s.close()
        return ""
    ip = s.getsockname()[0]
    s.close()
    return ip
