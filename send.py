import serial
import struct

def pack_points(chess_point, center_point):
    """
    打包棋子坐标和棋盘中心坐标，单位: 毫米 -> 厘米，发送小端 float。
    """
    try:
        # 坐标单位转换：毫米 → 厘米
        x1, y1 = chess_point[0] / 10.0, chess_point[1] / 10.0
        x2, y2 = center_point[0] / 10.0, center_point[1] / 10.0

        print(f"转换为厘米坐标：")
        print(f"  棋子位置: ({x1:.2f}, {y1:.2f})")
        print(f"  棋盘中心: ({x2:.2f}, {y2:.2f})")

        # 小端打包
        data = b''.join([
            struct.pack('<f', x1),
            struct.pack('<f', y1),
            struct.pack('<f', x2),
            struct.pack('<f', y2),
        ])

        # 帧头帧尾
        packet = bytes([0xFF]) + data + bytes([0xFE])
        return packet

    except Exception as e:
        raise RuntimeError(f"打包失败: {str(e)}")

class Sender:
    def __init__(self, port, baudrate):
        self.ser = serial.Serial(port, baudrate, timeout=1)

    def send_packed_data(self, chess_point, center_point):
        byte_data = pack_points(chess_point, center_point)
        self.ser.write(byte_data)
        print("发送的十六进制数据:")
        print(' '.join(f"{b:02X}" for b in byte_data))

    @staticmethod
    def list_ports():
        """列出可用串口"""
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
