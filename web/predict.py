import numpy as np
import os
from PIL import Image as PIL_Image
import cv2
import glob
import re
import chess
import chess.svg
import shutil
import tempfile
import time
from datetime import datetime
from keras.models import load_model
import cairosvg


def natural_keys(text):
    """用于自然排序文件名"""

    def atoi(text):
        return int(text) if text.isdigit() else text

    return [atoi(c) for c in re.split('(\d+)', text)]


def grab_cell_files(folder_name):
    """获取所有格子图像文件"""
    return sorted(glob.glob(os.path.join(folder_name, '*.png')), key=natural_keys)


def classify_cells(model, img_filename_list):
    """分类每个格子并生成FEN字符串"""
    category_reference = {
        0: 'b', 1: 'k', 2: 'n', 3: 'p', 4: 'q', 5: 'r', 6: '1',
        7: 'B', 8: 'K', 9: 'N', 10: 'P', 11: 'Q', 12: 'R'
    }
    pred_list = []

    for filename in img_filename_list:
        img_arr = PIL_Image.open(filename).resize((224, 224))
        if img_arr.mode != 'RGB':
            img_arr = img_arr.convert('RGB')

        img_data = np.array(img_arr, dtype=np.float32)
        img_data = img_data[:, :, ::-1]  # RGB to BGR
        img_data[:, :, 0] -= 103.939
        img_data[:, :, 1] -= 116.779
        img_data[:, :, 2] -= 123.68

        img_data = np.expand_dims(img_data, axis=0)
        out = model.predict(img_data, verbose=0)
        pred_list.append(category_reference[np.argmax(out)])

    raw_fen_string = ''.join(pred_list)
    reversed_fen_string = raw_fen_string[::-1]
    rows_64_chars = [reversed_fen_string[i:i + 8] for i in range(0, 64, 8)]
    processed_rows = [re.sub('1+', lambda m: str(len(m.group(0))), row) for row in rows_64_chars]
    return '/'.join(processed_rows)


def fen_to_image(fen, output_path):
    """将FEN转换为棋盘图像"""
    try:
        board = chess.Board(fen)
        svg_path = tempfile.mktemp(suffix='.svg')

        with open(svg_path, "w") as f:
            f.write(chess.svg.board(board=board))

        cairosvg.svg2png(url=svg_path, write_to=output_path)
        os.remove(svg_path)
        return board
    except Exception as e:
        print(f"FEN转换错误: {e}")
        return None


def fixed_x_crop_images(img, points):
    """根据网格点裁剪格子图像"""
    cropped_images = []
    if len(points) < 81:
        return cropped_images

    for row in range(8):
        for col in range(8):
            p1_index = row * 9 + col
            p3_index = (row + 1) * 9 + (col + 1)

            x_start = int(points[p1_index][0])
            y_start = int(points[p1_index][1])
            x_end = int(points[p3_index][0])
            y_end = int(points[p3_index][1])

            if y_end > y_start and x_end > x_start:
                cropped = img[y_start:y_end, x_start:x_end]
                if cropped.size > 0:
                    cropped_images.append(cropped)
    return cropped_images


def find_grid_lines(projection, min_dist=25, threshold_ratio=0.3):
    """查找网格线位置"""
    if len(projection) == 0:
        return []

    threshold = np.max(projection) * threshold_ratio
    peaks = np.where(projection > threshold)[0]

    if len(peaks) == 0:
        return []

    lines = []
    current_line = [peaks[0]]

    for i in range(1, len(peaks)):
        if peaks[i] - peaks[i - 1] < min_dist:
            current_line.append(peaks[i])
        else:
            if current_line:
                lines.append(int(np.mean(current_line)))
            current_line = [peaks[i]]

    if current_line:
        lines.append(int(np.mean(current_line)))

    return lines


def recognize_chessboard(image_path, model_path, output_dir='output'):
    """
    识别棋盘的主函数

    参数:
        image_path: 棋盘图片路径
        model_path: 模型文件路径
        output_dir: 输出目录

    返回:
        (fen, board_image_path): FEN字符串和生成的棋盘图像路径
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 创建临时目录
    temp_cell_dir = os.path.join(output_dir, 'temp_cells')
    os.makedirs(temp_cell_dir, exist_ok=True)

    # 加载模型
    try:
        model = load_model(model_path)
        print(f"成功加载模型: {model_path}")
    except Exception as e:
        print(f"模型加载失败: {e}")
        return None, None

    # 读取图像
    img_original = cv2.imread(image_path)
    if img_original is None:
        print(f"无法读取图像: {image_path}")
        return None, None

    # 透视变换参数
    input_pts = np.float32([[531, 17], [1371, 21], [1667, 982], [233, 979]])
    width, height = 800, 800
    output_pts = np.float32([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]])

    # 应用透视变换
    M = cv2.getPerspectiveTransform(input_pts, output_pts)
    warped_img = cv2.warpPerspective(img_original, M, (width, height))

    # 网格检测
    gray = cv2.cvtColor(warped_img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    # 投影分析
    vertical_projection = np.sum(edges, axis=0)
    horizontal_projection = np.sum(edges, axis=1)

    # 查找网格线
    v_lines_x = find_grid_lines(vertical_projection, min_dist=25, threshold_ratio=0.3)
    h_lines_y = find_grid_lines(horizontal_projection, min_dist=25, threshold_ratio=0.3)

    # 确保有9条线
    if len(v_lines_x) < 9 or len(h_lines_y) < 9:
        print(f"警告: 检测到非常规网格 (水平: {len(h_lines_y)}, 垂直: {len(v_lines_x)})")
        if len(v_lines_x) < 2 or len(h_lines_y) < 2:
            v_lines_x = np.linspace(0, width, 9, dtype=int)
            h_lines_y = np.linspace(0, height, 9, dtype=int)
        else:
            v_lines_x = np.linspace(min(v_lines_x), max(v_lines_x), 9, dtype=int)
            h_lines_y = np.linspace(min(h_lines_y), max(h_lines_y), 9, dtype=int)

    # 生成网格点
    points = []
    for y in h_lines_y:
        for x in v_lines_x:
            points.append((x, y))

    # 裁剪格子图像
    cropped_images = fixed_x_crop_images(warped_img, points)

    # 保存格子图像
    for i, crop_img in enumerate(cropped_images):
        cell_path = os.path.join(temp_cell_dir, f'cell_{i:03d}.png')
        cv2.imwrite(cell_path, crop_img)

    # 获取格子文件列表
    img_filename_list = grab_cell_files(temp_cell_dir)

    # 生成FEN
    fen = classify_cells(model, img_filename_list)
    print(f"生成的FEN: {fen}")

    # 创建带时间戳的棋盘图像文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    board_image_filename = f"chessboard_{timestamp}.png"
    board_image_path = os.path.join(output_dir, board_image_filename)

    # 生成棋盘图像
    board = fen_to_image(fen, board_image_path)

    # 清理临时文件
    shutil.rmtree(temp_cell_dir)

    if board:
        print(f"成功生成棋盘图像: {board_image_path}")
        return fen, board_image_path
    else:
        print("无法生成棋盘图像")
        return fen, None


# 命令行接口
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='国际象棋棋盘识别系统')
    parser.add_argument('--image', type=str, required=True, help='输入棋盘图像路径')
    parser.add_argument('--model', type=str, required=True, help='模型文件路径')
    parser.add_argument('--output', type=str, default='output', help='输出目录')

    args = parser.parse_args()

    print("=" * 50)
    print("国际象棋棋盘识别系统")
    print("=" * 50)

    # 运行处理流程
    fen, board_image = recognize_chessboard(args.image, args.model, args.output)

    if fen:
        print("处理完成！")
        print(f"最终FEN: {fen}")
        if board_image:
            print(f"棋盘图像已保存至: {board_image}")
    else:
        print("处理失败，请检查错误信息")