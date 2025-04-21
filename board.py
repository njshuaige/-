import cv2
import numpy as np

class GRID:
    def __init__(self, config):
        self.centers = config['grid_centers']
        self.BOARD_SIZE = config['BOARD_SIZE']
        self.GRID_SIZE = config['GRID_SIZE']
        self.grid = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

        # 自动修正中心点结构为 3x3
        if isinstance(self.centers, np.ndarray) and self.centers.shape == (9, 2):
            self.centers = self.centers.reshape((3, 3, 2)).tolist()
        elif isinstance(self.centers, list) and len(self.centers) == 9 and isinstance(self.centers[0], (list, tuple)):
            self.centers = np.array(self.centers).reshape((3, 3, 2)).tolist()

    def detect_piece(self, roi):
        lower_white = np.array([190, 190, 190])
        upper_white = np.array([255, 255, 255])
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([50, 50, 50])

        white_mask = cv2.inRange(roi, lower_white, upper_white)
        black_mask = cv2.inRange(roi, lower_black, upper_black)

        white_pixels = cv2.countNonZero(white_mask)
        black_pixels = cv2.countNonZero(black_mask)

        if white_pixels > 50:
            return 1  # 白棋
        elif black_pixels > 250:
            return -1  # 黑棋
        else:
            return 0  # 空
    def update_grid(self, frame):
        for i in range(3):
            for j in range(3):
                index = i * 3 + j
                center = self.centers[index]
                x, y = int(center[0]), int(center[1])
                roi = frame[y - self.GRID_SIZE // 4:y + self.GRID_SIZE // 4,
                            x - self.GRID_SIZE // 4:x + self.GRID_SIZE // 4]
                piece = self.detect_piece(roi)
                if piece != 0 and self.grid[i][j] == 0:
                    self.grid[i][j] = piece
                    print(f"棋子放入：({i}, {j}), 颜色：{'白棋' if piece == 1 else '黑棋'}, 中心坐标：({x}, {y})")
        print(self.grid)
        return self.grid


    def check_grid(self, frame):
        checked_grid = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        for i in range(3):
            for j in range(3):
                index = i * 3 + j
                center = self.centers[index]
                x, y = int(center[0]), int(center[1])
                roi = frame[y - self.GRID_SIZE // 4:y + self.GRID_SIZE // 4,
                            x - self.GRID_SIZE // 4:x + self.GRID_SIZE // 4]
                piece = self.detect_piece(roi)
                checked_grid[i][j] = piece
        return checked_grid
