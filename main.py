import cv2
import time
from process import Detector                 # 棋盘检测器
import chess_detect                          # 棋子检测模块
from grid import GRID                        # 棋盘状态管理类
from coordinate_converter import convert_coordinate  # 坐标转换函数
from send import Sender                      # 串口发送类

# === 初始化摄像头和模块 ===
cap = cv2.VideoCapture(1)
detector = Detector()
sender = Sender(port="COM9", baudrate=9600)

if not cap.isOpened():
    print("摄像头无法打开！")
    exit()

# === 用户输入目标格子编号 ===
def get_target_index():
    while True:
        try:
            idx = int(input("请输入要发送的中心点编号（1~9，对应格子1到9）: "))
            if 1 <= idx <= 9:
                return idx - 1  # 用户输入从1开始，程序从0开始
            else:
                print("请输入 1 到 9 之间的数字！")
        except ValueError:
            print("输入无效，请输入数字！")

# 获取目标格子编号
target_index = get_target_index()
print(f"你选择的发送格子编号是 {target_index + 1}")

last_process_time = time.time()
grid_instance = None
centers_real = None
sent_once = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # === 检测黄色棋盘和九个中心点 ===
    yellow, centers = detector.find_roi(frame)

    # === 初始化 GRID（仅执行一次）===
    if centers is not None and len(centers) == 9 and grid_instance is None:
        grid_instance = GRID(centers, radius=15)
        centers_real = [convert_coordinate(p) for p in centers]

        print("已初始化 GRID 实例")
        print("=== 九个中心点的图像坐标与实际坐标（单位：cm） ===")
        for i, (pix, real) in enumerate(zip(centers, centers_real)):
            print(f"格子 {i+1}: 图像坐标 {pix} -> 实际坐标 {real}")

    # === 每 0.2 秒进行一次处理与发送 ===
    current_time = time.time()
    if current_time - last_process_time >= 0.2:
        black, white, _, _ = chess_detect.chess_detect(frame, debug=True)
        print("黑棋坐标:", black)
        print("白棋坐标:", white)

        if grid_instance and centers and not sent_once:
            grid_status = grid_instance.check_grid(frame, debug=True)
            print("当前棋盘状态:")
            for row in grid_status:
                print(row)

            # === 串口发送逻辑（优先黑棋，否则白棋）===
            try:
                target_center = centers[target_index]
                piece_point = None

                if black:
                    piece_point = black[0]
                    print("发送黑棋坐标")
                elif white:
                    piece_point = white[0]
                    print("发送白棋坐标")
                else:
                    print("未检测到棋子，不发送")

                if piece_point is not None:
                    # === 将像素坐标转换为实际坐标 ===
                    piece_real = convert_coordinate(piece_point)
                    target_real = convert_coordinate(target_center)

                    # === 发送实际坐标数据 ===
                    sent = sender.send_data(piece_real, target_real)
                    print("已发送数据:", ' '.join(f"{b:02X}" for b in sent))
                    sent_once = True
                    print("已发送一次，程序将停止发送。")

            except Exception as e:
                print(f"发送失败: {e}")

        last_process_time = current_time

    # === 显示画面 ===
    cv2.imshow("Frame with Yellow Rectangle and Grid", yellow)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

