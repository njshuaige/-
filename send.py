import serial

def pack_data(chess_point, point):
    try:
        # 四舍五入保留整数
        cx, cy = round(chess_point[0]), round(chess_point[1])  # 黑棋坐标
        px, py = round(point[0]), round(point[1])              # 目标中心点

        print(f"[DEBUG] 打包数据坐标: 黑棋({cx},{cy})，目标中心点({px},{py})")

        # 协议格式: [0xFF, cy, cx, px, py, 0xFE]
        return bytes([0xFF, cy & 0xFF, cx & 0xFF, px & 0xFF, py & 0xFF, 0xFE])

    except Exception as e:
        raise RuntimeError(f"坐标打包失败: {e}")

class Sender:
    def __init__(self, port, baudrate):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        if not self.ser.is_open:
            raise RuntimeError(f"串口 {port} 未能打开")

    def send_data(self, chess_point, point):
        data = pack_data(chess_point, point)
        self.ser.write(data)
        self.ser.flush()  # 保证立即写入
        print(f"[DEBUG] 已发送数据: {' '.join(f'{b:02X}' for b in data)}")
        return data  # 返回发送的字节数据

    @staticmethod
    def list_ports():
        import serial.tools.list_ports
        return [port.device for port in serial.tools.list_ports.comports()]

