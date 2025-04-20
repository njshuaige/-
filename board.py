import cv2
import numpy as np
class GRID:
    def __init__(self,dict):
        self.centers = dict['grid_centers']
        self.BOARD_SIZE = dict['BOARD_SIZE']
        self.GRID_SIZE = dict['GRID_SIZE']
        self.grid = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]
    def detect_piece(self,roi):
        lower_white = np.array([190, 190, 190])  # 白色阈值
        upper_white = np.array([255, 255, 255])
        lower_black = np.array([0, 0, 0])  # 黑色阈值
        upper_black = np.array([50, 50, 50])
        white_mask = cv2.inRange(roi, lower_white, upper_white)
        black_mask = cv2.inRange(roi, lower_black, upper_black)
        #统计像素数量
        white_pixels = cv2.countNonZero(white_mask)
        black_pixels = cv2.countNonZero(black_mask)

    # 判断棋子颜色
        if white_pixels > 50:  # 白棋
            return 1
        elif black_pixels > 250:  # 黑棋
            return -1
        else:  # 空
            return 0
        
    def update_grid(self,frame):
        for i in range(3):
            for j in range(3):
                x, y =self.centers[i][j]
                # 提取格子区域
                roi = frame[y - self.GRID_SIZE // 4:y + self.GRID_SIZE // 4, x - self.GRID_SIZE // 4:x + self.GRID_SIZE // 4]
                # 检测棋子
                piece = self.detect_piece(roi)
                # 如果检测到棋子且之前为空
                if piece != 0 and self.grid[i][j] == 0:
                    self.grid[i][j] = piece
                    print(f"棋子放入：({i}, {j}), 颜色：{'白棋' if piece == 1 else '黑棋'}, 中心坐标：({x}, {y})")
        print(self.grid)
        return self.grid
    def check_grid(self,frame):
        checked_grid = [[
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]]
        for i in range(3):
            for j in range(3):
                x, y =self.centers[i][j]
                # 提取格子区域
                roi = frame[y - self.GRID_SIZE // 4:y + self.GRID_SIZE // 4, x - self.GRID_SIZE // 4:x + self.GRID_SIZE // 4]
                # 检测棋子
                piece = self.detect_piece(roi)
                # 如果检测到棋子且之前为空
                if piece != 0 and checked_grid.grid[i][j] == 0:
                    checked_grid[i][j] = piece
                    
       
        return checked_grid
