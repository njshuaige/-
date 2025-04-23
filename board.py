import cv2
import numpy as np

def get_point_color(img, center_point, radius):
    """ 获取指定点周围区域的平均 BGR 颜色 """
    x, y = center_point
    x1 = max(0, x - radius)
    x2 = min(img.shape[1], x + radius)
    y1 = max(0, y - radius)
    y2 = min(img.shape[0], y + radius)

    region = img[y1:y2, x1:x2]
    average_color = cv2.mean(region)[:3]  # BGR

    return tuple(int(c) for c in average_color)

def classify_board_chess_color(img, center_points, radius=20, debug=False):
    """ 判断棋盘上每个中心点的颜色，返回 -1(黑)、1(白)、0(无) """
    board_chess_colors = []

    for idx, point in enumerate(center_points):
        color = get_point_color(img, point, radius)

        if color[0] < 100 and color[1] < 100 and color[2] < 100:
            value = -1  # 黑棋
        elif color[0] > 150 and color[1] > 150 and color[2] > 150:
            value = 1   # 白棋
        else:
            value = 0   # 无棋

        board_chess_colors.append(value)

        if debug:
            print(f"格子 {idx+1}: BGR={color} → 棋子={value}")

    return board_chess_colors

# ✅ 添加 GRID 类
class GRID:
    def __init__(self, center_points, radius=15):
        self.center_points = center_points
        self.radius = radius

    def check_grid(self, img, debug=False):
        """ 返回 3x3 的棋盘状态列表 """
        flat = classify_board_chess_color(img, self.center_points, self.radius, debug)
        return [flat[i:i+3] for i in range(0, 9, 3)]

