import cv2
import numpy as np

from colors import RED1_LOWER, RED1_UPPER


def remove_background(img, lower, upper):
    """ 移除指定颜色背景，并进行高斯模糊以降低干扰 """
    blurred_img = cv2.GaussianBlur(img, (3, 3), 0)  # 高斯模糊去噪
    hsv_img = cv2.cvtColor(blurred_img, cv2.COLOR_BGR2HSV)  # 转换为HSV格式

    lower_color = np.array(lower)
    upper_color = np.array(upper)

    mask = cv2.inRange(hsv_img, lower_color, upper_color)  # 创建掩膜
    cv2.bitwise_not(mask, mask)  # 掩膜取反，留下非背景区域

    return mask


def detect_chess_contours(img):
    """ 从背景识别棋子轮廓 """
    mask_PINK = remove_background(img, RED1_LOWER, RED1_UPPER)

    # 使用形态学开运算去除小干扰
    kernel = np.ones((5, 5), np.uint8)
    mask_PINK = cv2.morphologyEx(mask_PINK, cv2.MORPH_OPEN, kernel)

    cv2.namedWindow('Mask', cv2.WINDOW_NORMAL)
    cv2.imshow('Mask', mask_PINK)

    contours, _ = cv2.findContours(mask_PINK, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    filtered_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)

        if perimeter < (20 * 4) or area < 10:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h

        (x, y), radius = cv2.minEnclosingCircle(contour)
        min_circle_area = np.pi * radius ** 2
        area_ratio = min_circle_area / area

        # if (area_ratio < 1.2) and (0.90 < aspect_ratio < 1.10):
        filtered_contours.append(contour)

    return filtered_contours


def classify_background_chess_color(img, contours):
    """ 根据轮廓颜色分类棋子 """
    black_contours = []
    white_contours = []

    for contour in contours:
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, -1)
        mean_val = cv2.mean(img, mask=mask)

        if mean_val[0] < 100 and mean_val[1] < 100 and mean_val[2] < 100:
            black_contours.append(contour)
        elif mean_val[0] > 150 and mean_val[1] > 150 and mean_val[2] > 150:
            white_contours.append(contour)

    return black_contours, white_contours


def contours_to_positom(contours):
    """ 将轮廓转换为棋子位置 """
    contours_positions = []

    for contour in contours:
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            contours_positions.append((cX, cY))

    return contours_positions


def draw_chess(img, contours, color):
    """ 在图像上绘制棋子轮廓 """
    img_chess = img.copy()

    for contour in contours:
        cv2.drawContours(img_chess, [contour], -1, color, 8)

    chess_positions = contours_to_positom(contours)
    for chess_position in chess_positions:
        cv2.circle(img_chess, chess_position, 16, color, -1)
        cv2.putText(img_chess, f"{chess_position}", chess_position,
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    return img_chess


def chess_detect(img, debug=False):
    """ 从背景识别棋子位置 """
    chess_contours = detect_chess_contours(img)

    if len(chess_contours) == 0:
        if debug:
            cv2.namedWindow("img_chess", cv2.WINDOW_NORMAL)
            cv2.imshow("img_chess", img)
        return [], [], [], []

    black_contours, white_contours = classify_background_chess_color(img, chess_contours)
    black_coords = contours_to_positom(black_contours)
    white_coords = contours_to_positom(white_contours)

    if debug:
        img_chess = draw_chess(img, black_contours, (255, 100, 0))
        img_chess = draw_chess(img_chess, white_contours, (0, 100, 255))
        cv2.namedWindow("img_chess", cv2.WINDOW_NORMAL)
        cv2.imshow("img_chess", img_chess)

    return black_coords, white_coords, black_contours, white_contours

