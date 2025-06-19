import os
from flask import Flask, request, url_for, redirect, render_template, jsonify, session
from predict import recognize_chessboard

IM1_PATH  = ''
OUT_PATH = ''
MODEL_PATH = './model/model.h5'
app = Flask(__name__)
app.secret_key = '123'

@app.route('/')
def home():
    return render_template('home.html',im1_path=IM1_PATH,out_path=OUT_PATH)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    files = request.files.getlist('file')
    upload_folder = './static/upload_image'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    global IM1_PATH
    IM1_PATH = os.path.join(upload_folder, files[0].filename)
    files[0].save(IM1_PATH)
    return "Files uploaded successfully", 200


@app.route('/result', methods=['GET', 'POST'])
def result():
    OUT_DIR = './static/output'
    try:
        # 识别棋盘
        fen, board_image_path = recognize_chessboard(
            image_path=IM1_PATH,
            model_path=MODEL_PATH,
            output_dir=OUT_DIR
        )

        if not fen or not board_image_path:
            return jsonify({"error": "棋盘识别失败"}), 500

        # 提取文件名用于URL
        board_image_filename = os.path.basename(board_image_path)
        image_url = f"/static/output/{board_image_filename}"

        global OUT_PATH
        OUT_PATH = image_url
        return jsonify({
            'status': 'success',
            'im1_path': IM1_PATH,
            'out_path': OUT_PATH
        })
    except Exception as e:
        print(f"处理过程中出错: {str(e)}")
        return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8848)