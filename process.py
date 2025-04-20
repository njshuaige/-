import cv2
import numpy as np
import math

class Detector:
    def __init__(self):
        self.img = None
        self.white_chess = []
        self.black_chess = []

    def find_roi(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([40, 255, 255])
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
        dilated_mask = cv2.dilate(mask, kernel, iterations=1)
        contours, _ = cv2.findContours(dilated_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        crossing_pts_sorted = []  # 预定义，避免未赋值错误

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 5000:
                continue

            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            # 角点赋值
            up_left, down_left, down_right, up_right = box
            # 顺序可以调整，确保边的顺序正确

            def get_divided_points(p1, p2, divisions=6):
                points = []
                for i in range(1, divisions):
                    t = i / divisions
                    point = (1 - t) * p1 + t * p2
                    if i in [1, 3, 5]:
                        points.append(point.astype(int))
                return points

            # 计算边上的点
            top_points = get_divided_points(up_left, up_right)
            right_points = get_divided_points(up_right, down_right)
            bottom_points = get_divided_points(down_right, down_left)
            left_points = get_divided_points(down_left, up_left)

            # 排序
            top_points_sorted = sorted(top_points, key=lambda p: p[0])
            bottom_points_sorted = sorted(bottom_points, key=lambda p: p[0])
            left_points_sorted = sorted(left_points, key=lambda p: p[1])
            right_points_sorted = sorted(right_points, key=lambda p: p[1])

            horizontal_lines = list(zip(top_points_sorted, bottom_points_sorted))
            vertical_lines = list(zip(left_points_sorted, right_points_sorted))

            def line_intersection(p1, p2, p3, p4):
                p1, p2, p3, p4 = map(np.array, (p1, p2, p3, p4))
                s1 = p2 - p1
                s2 = p4 - p3
                denom = -s2[0] * s1[1] + s1[0] * s2[1]
                if denom == 0:
                    return None
                s = (-s1[1] * (p1[0] - p3[0]) + s1[0] * (p1[1] - p3[1])) / denom
                t = (s2[0] * (p1[1] - p3[1]) - s2[1] * (p1[0] - p3[0])) / denom
                if 0 <= s <= 1 and 0 <= t <= 1:
                    return p1 + t * s1
                return None

            crossing_pts = []
            for h_start, h_end in horizontal_lines:
                for v_start, v_end in vertical_lines:
                    pt = line_intersection(h_start, h_end, v_start, v_end)
                    if pt is not None:
                        crossing_pts.append(pt.astype(int))

            crossing_pts_sorted = sorted(crossing_pts, key=lambda p: (-p[1], p[0]))

            # 绘制交点
            for idx, pt_int in enumerate(crossing_pts_sorted, start=1):
                cv2.circle(img, tuple(pt_int), 7, (0, 255, 255), 3)
                text = f"{idx}: ({pt_int[0]}, {pt_int[1]})"
                text_pos = (pt_int[0] + 10, pt_int[1] + 10)
                cv2.putText(img, text, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)

        return img, crossing_pts_sorted
