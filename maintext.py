import cv2
import time
from process import Detector         # 棋盘检测器
import chess_detect                 # 棋子检测模块（含 classify_board_chess_color）
from grid import GRID               # 优化后的 GRID 类
from coordinate_converter import convert_coordinate, encode_coord  # 坐标转换模块 ✅ 新增

cap = cv2.VideoCapture(1)
detector = Detector()

if not cap.isOpened():
    print("摄像头无法打开！")
    exit()

last_print_time = time.time()
grid_instance = None  # GRID 实例
centers_real = None   # 存储实际坐标（单位 cm）

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 检测黄色矩形和九个中心点
    yellow, centers = detector.find_roi(frame)

    # 初始化 grid（只初始化一次，后续复用）
    if centers is not None and len(centers) == 9 and grid_instance is None:
        grid_instance = GRID(centers, radius=15)
        print("已初始化 GRID 实例")

        # === 坐标转换 === ✅
        centers_real = [convert_coordinate(p) for p in centers]
        print("九个中心点的实际坐标（单位：cm）:")
        for i, (pix, real) in enumerate(zip(centers, centers_real)):
            print(f"格子 {i+1}: 图像坐标 {pix} -> 实际坐标 {real}")

    # 每隔 0.2秒检查一次状态
    current_time = time.time()
    if current_time - last_print_time >= 0.2:
        black, white, _, _ = chess_detect.chess_detect(frame, debug=True)
        print("黑棋坐标:", black)
        print("白棋坐标:", white)
        print("九个中心点坐标:", centers)

        if grid_instance:
            grid_status = grid_instance.check_grid(frame, debug=True)
            print("当前棋盘状态:")
            for row in grid_status:
                print(row)

        last_print_time = current_time

    # 显示窗口
    cv2.imshow("Frame with Yellow Rectangle and Grid", yellow)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
