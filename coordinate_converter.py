import numpy as np

x1 = [264, 135, 392, 400, 237]
y1 = [190, 203, 354, 78, 379]
x2 = [-6.6, -2.3, -10.7, -11.10, -6.20]
y2 = [9.6, 10.3, 14.9, 5.49, 15.60]

# === 2. 拟合线性变换模型 ===
A_x = np.vstack([x1, np.ones(len(x1))]).T
s_x, t_x = np.linalg.lstsq(A_x, x2, rcond=None)[0]

A_y = np.vstack([y1, np.ones(len(y1))]).T
s_y, t_y = np.linalg.lstsq(A_y, y2, rcond=None)[0]

# === 3. 转换函数：像素坐标 → 实际坐标（单位：cm） ===
def convert_coordinate(point):
    """
    将图像坐标 (x, y) 转换为实际物理坐标 (单位：cm)

    Args:
        point: (x, y) 图像坐标（像素）

    Returns:
        (x_real, y_real): 实际坐标（浮点数，单位 cm）
    """
    x_real = s_x * point[0] + t_x
    y_real = s_y * point[1] + t_y
    return (round(x_real, 2), round(y_real, 2))

# === 4. 编码帧格式函数（可选） ===
def encode_coord(x, y):
    """
    将浮点坐标 (cm) 编码为帧格式: FF XX XX YY YY FE

    Args:
        x, y: 实际坐标（单位 cm）

    Returns:
        bytearray: 编码后的帧数据
    """
    x_int = int(x * 100)
    y_int = int(y * 100)
    frame = bytearray()
    frame.append(0xFF)
    frame.extend(x_int.to_bytes(2, byteorder='big', signed=True))
    frame.extend(y_int.to_bytes(2, byteorder='big', signed=True))
    frame.append(0xFE)
    return frame
