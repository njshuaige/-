import cv2
import numpy as np

from colors import  PINK_LOWER, PINK_UPPER


def remove_background(img, lower, upper):
    
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # 转换为HSV格式

    lower_color = np.array(lower)  # 颜色范围下限
    upper_color = np.array(upper)  # 颜色颜色上限

    mask = cv2.inRange(hsv_img, lower_color, upper_color)  # 创建掩膜

    # kernel = np.ones((5, 5), np.uint8)             # 定义结构元素  
    # mask = cv2.erode(mask, kernel, iterations=5)   # 收缩操作
    # mask = cv2.dilate(mask, kernel, iterations=5)  # 膨胀操作
 
    cv2.bitwise_not(mask, mask)  # 翻转掩膜 

    return mask


def detect_chess_contours(img):
    """ 从背景识别棋子轮廓 """

    mask_PINK = remove_background(img, PINK_LOWER, PINK_UPPER)  # 移除粉色背景
    # mask_green  = remove_background(img,  GREEN_LOWER,  GREEN_UPPER)
    # mask = mask_yellow & mask_green

    cv2.namedWindow('Mask', cv2.WINDOW_NORMAL)   # 显示掩膜
    cv2.imshow('Mask', mask_PINK)

    contours, _ = cv2.findContours(mask_PINK, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # 查找轮廓
    
    filtered_contours = []

    for contour in contours:  # 提取位置和颜色

        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)

        if perimeter < (20 * 4) or area < 10:  # 过滤小的轮廓 
            continue

        # circularity = (4 * np.pi * area) / (perimeter * perimeter)
        # print(f"圆形度: {circularity}")
        
        # 计算长宽比
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h
        # print(f"长宽比: {aspect_ratio}")
        
        # 计算 最小外接圆 与 轮廓 的面积之比
        (x, y), radius = cv2.minEnclosingCircle(contour)
        min_circle_area = np.pi * radius ** 2
        area_ratio = min_circle_area / area
        # cv2.circle(img, (int(x), int(y)), int(radius), (0, 0, 255), 2) # 绘制最小外接圆
        # print(f"最小外接圆面积与轮廓面积之比: {area_ratio}")
        
        # 过滤条件
        if (area_ratio < 1.3)  and (0.90 < aspect_ratio < 1.10):
            filtered_contours.append(contour)

    return filtered_contours      


def classify_background_chess_color(img, contours):
    """ 根据轮廓颜色分类棋子 """

    black_contours = []
    white_contours = []

    for contour in contours:
        # 计算轮廓的平均颜色
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, -1)  # 填充轮廓以获取颜色
        mean_val = cv2.mean(img, mask=mask)  # 计算平均色彩

        # 判断颜色是否接近黑色或白色
        if mean_val[0] < 100 and mean_val[1] < 100 and mean_val[2] < 100:  # 接近黑色
            black_contours.append(contour)
        elif mean_val[0] > 150 and mean_val[1] > 150 and mean_val[2] > 150:  # 接近白色
            white_contours.append(contour)

    return black_contours, white_contours


def contours_to_positom(contours):
    """ 将轮廓转换为棋子位置 """

    contours_positions = []

    for contour in contours:
        M = cv2.moments(contour)  # 计算轮廓的中心点
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
        cv2.putText(img_chess, f" {chess_position[0], chess_position[1]}", chess_position, cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    return img_chess


def chess_detect(img, debug=False):
    """ 从背景识别棋子位置 """

    chess_contours = detect_chess_contours(img)  # 获取所有棋子轮廓

    if len(chess_contours) == 0:  # 如果没有找到任何棋子轮廓，则返回空列表
       
        if debug:  # 调试模式
            cv2.namedWindow("img_chess", cv2.WINDOW_NORMAL)
            cv2.imshow("img_chess", img)

        return [], [], [], []
    
    black_contours, white_contours = classify_background_chess_color(img, chess_contours)  # 按颜色分类
    black_coords = contours_to_positom(black_contours)  # 获取黑棋子位置
    white_coords = contours_to_positom(white_contours)  # 获取白棋子位置

    # print(f"黑色棋子数量: {len(black_coords)}, 位置: {black_coords}")
    # print(f"白色棋子数量: {len(white_coords)}, 位置: {white_coords}")
 
    if debug:  # 调试模式
        img_chess = draw_chess(img, black_contours, (255, 100, 0))
        img_chess = draw_chess(img_chess, white_contours, (0, 100, 255))
        cv2.namedWindow("img_chess", cv2.WINDOW_NORMAL)
        cv2.imshow("img_chess", img_chess)

    return black_coords, white_coords, black_contours, white_contours
