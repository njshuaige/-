import cv2
import time
from process import Detector  # 你已有的棋盘检测器
import chess_detect           # 你已有的棋子检测模块
from grid import GRID         # 我们刚刚写好的 GRID 类

cap = cv2.VideoCapture(1)
detector = Detector()

if not cap.isOpened():
    print("摄像头无法打开！") 
    exit()

# 记录上次打印的时间
last_print_time = time.time()

# 初始化 grid 类的占位对象
grid_instance = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 检测黄色矩形和九个中心点
    yellow, centers = detector.find_roi(frame)

    # 初始化 grid（只初始化一次）
    if grid_instance is None and len(centers) == 9:
        config = {
            'grid_centers': centers,
            'BOARD_SIZE': 90,
            'GRID_SIZE': 30
        }
        grid_instance = GRID(config)

    # 每隔2秒打印一次棋子状态
    current_time = time.time()
    if current_time - last_print_time >= 2:
        black, white, _, _ = chess_detect.chess_detect(frame, debug=True)
        print("黑棋坐标:", black)
        print("白棋坐标:", white)
        print("九个中心点坐标:", centers)

        if grid_instance:
            grid_status = grid_instance.check_grid(frame)
            print("当前棋盘状态:")
            for row in grid_status:
                print(row)

        last_print_time = current_time

    cv2.imshow("Frame with Yellow Rectangle and Grid", yellow)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
