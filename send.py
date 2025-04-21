import serial


def pack_points(point1, point2):
    """
    将两个坐标点打包为指定格式的字节数组
    输入格式示例：
        point1 = (-1.11, 10.09)
        point2 = (-10.07, 7.69)
    输出格式：
        [0xFF, 符号位..., 0xFE]
    """
    def process_coordinate(number):
        """处理单个坐标，返回(符号, 整数部分, 小数部分)"""
        # 验证输入类型
        if not isinstance(number, (int, float)):
            raise TypeError("坐标必须是数字类型")
        
        # 计算符号位 (0: 正, 1: 负)
        sign = 1 if number < 0 else 0
        
        # 分离整数和小数部分
        abs_num = abs(number)
        integer_part = int(abs_num)
        
        # 处理小数部分（保留两位，精确转换）
        decimal_str = "{:.2f}".format(abs_num).split('.')[1]
        decimal_part = int(decimal_str)
        
        # 数值范围验证
        if not (0 <= integer_part <= 255):
            raise ValueError(f"整数部分 {integer_part} 超出范围 (0-255)")
        if not (0 <= decimal_part <= 99):
            raise ValueError(f"小数部分 {decimal_part} 超出范围 (0-99)")
        
        return sign, integer_part, decimal_part

    try:
        # 处理点1的x和y坐标
        x1_sign, x1_int, x1_frac = process_coordinate(point1[0])
        y1_sign, y1_int, y1_frac = process_coordinate(point1[1])
        
        # 处理点2的x和y坐标
        x2_sign, x2_int, x2_frac = process_coordinate(point2[0])
        y2_sign, y2_int, y2_frac = process_coordinate(point2[1])
        
        # 构建数据包
        packet = [
            0xFF,
            # 点1数据
            x1_sign, y1_sign,
            x1_int, x1_frac,
            y1_int, y1_frac,
            # 点2数据
            x2_sign, y2_sign,
            x2_int, x2_frac,
            y2_int, y2_frac,
            0xFE
        ]
        
        # 转换为字节数组
        return bytes(packet)
    
    except (ValueError, TypeError) as e:
        raise RuntimeError(f"数据打包失败: {str(e)}")



class Sender:
    def __init__(self, port, baudrate):
        self.timeout = 1
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)



    def send_packed_data(self,point1,point2):
        byte_data = pack_points(point1,point2)
        self.ser.write(byte_data)
        print("已发送")

    def list_ports():
        """列出可用串口"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]


# 示例使用
if __name__ == "__main__":
    port = 'COM10'
    baudrate = 9600
    sender = Sender(port,baudrate)
    point1 = (-0.13,17.92)
    point2 = (-4,12)
    #result = pack_points(point1,point2)
    #print(result)
    #print(bytes([0xFF,0xFE]))
    sender.send_packed_data(point1,point2)
