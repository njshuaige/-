import cv2
import time
from process import Detector
import chess_detect
from grid import GRID
from coordinate_converter import convert_coordinate
from send import Sender
from ai_helper import check_winner, help_move  # AI 判断模块

# === 初始化 ===
cap = cv2.VideoCapture(1)
detector = Detector()
sender = Sender(port="COM9", baudrate=9600)

if not cap.isOpened():
    print("摄像头无法打开")
    exit()

grid_instance = None
centers_real = None
sent_once = False
last_process_time = time.time()
player = 1  # 黑棋先手（1: 黑棋, -1: 白棋）

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # === 检测黄色矩形和中心点 ===
    yellow, centers = detector.find_roi(frame)

    # 初始化 GRID（只运行一次）
    if centers is not None and len(centers) == 9 and grid_instance is None:
        grid_instance = GRID(centers, radius=15)
        centers_real = [convert_coordinate(p) for p in centers]
        print("=== 九个中心点实际坐标 ===")
        for i, real in enumerate(centers_real):
            print(f"格子{i+1} : {real}")

    # 每隔 0.3 秒处理一次图像
    current_time = time.time()
    if current_time - last_process_time >= 0.3:
        # === 检测棋子 ===
        black, white, _, _ = chess_detect.chess_detect(frame, debug=False)
        print("黑棋位置:", black)
        print("白棋位置:", white)

        if grid_instance:
            grid_status = grid_instance.check_grid(frame, debug=True)
            print("当前棋盘状态:")
            for row in grid_status:
                print(row)

            # === 判断胜负 ===
            winner = check_winner(grid_status)
            if winner != 0:
                print("胜者是：", "黑棋" if winner == -1 else "白棋")
                sent_once = True  # 禁止再发送
            else:
                # === AI 推荐下一步 ===
                recommended = help_move(grid_status, player=player)
                if recommended and not sent_once:
                    i, j = recommended
                    grid_index = i * 3 + j
                    target_center = centers[grid_index]
                    target_real = convert_coordinate(target_center)
                    print(f"推荐落子: 格子 {grid_index + 1}, 坐标 {target_real}")

                    # === 获取当前玩家的棋子位置 ===
                    if player == 1:
                        piece_point = black[0] if black else None
                    else:
                        piece_point = white[0] if white else None

                    if piece_point:
                        piece_real = convert_coordinate(piece_point)
                        sent = sender.send_data(piece_real, target_real)
                        print("已发送数据:", ' '.join(f"{b:02X}" for b in sent))
                        sent_once = True
                    else:
                        print("未检测到当前玩家棋子，未发送数据")
                elif sent_once:
                    print("数据已发送，跳过发送")
                else:
                    print("无推荐位置，可能已满盘")

        last_process_time = current_time

    # === 显示图像窗口 ===
    cv2.imshow("TicTacToe System", yellow)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('p'):
        sent_once = False
        print("已重置状态，允许重新发送")

cap.release()
cv2.destroyAllWindows()
