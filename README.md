# Chessboard Vision Project
## 有请下一组
中国海洋大学计算机视觉课程设计项目，旨在从单张图像识别国际象棋的棋盘布局。
项目采用混合策略，巧妙地结合了经典的计算机视觉技术（用于棋盘检测与校正）和现代深度学习技术（用于棋子分类），最终能够将识别结果输出为标准的霍桑-爱德华兹表示法 (FEN) 字符串。



✨ 项目特色
混合视觉技术: 综合利用OpenCV进行棋盘的透视变换、边缘检测和网格线定位，然后使用深度学习模型进行高精度的棋子分类。

高精度模型: 基于在ImageNet上预训练的VGG16模型进行迁移学习，对13种类别（黑白双方各6种棋子 + 空格）进行分类，在测试集上取得了优异的性能。

鲁棒的棋盘检测: 采用了投影分割法来抵抗棋子轮廓对网格线检测的干扰，能够处理有一定角度的棋盘图像。

标准化输出: 识别结果被准确地转换为FEN字符串，可以直接用于各种象棋软件或与象棋引擎（如Stockfish）进行交互。



🛠️ 技术栈
编程语言: Python

深度学习: Keras, TensorFlow

计算机视觉: OpenCV, Pillow (PIL)

科学计算与数据处理: NumPy, Pandas, Scikit-learn, SciPy

可视化: Matplotlib, Seaborn

象棋逻辑与渲染: python-chess, svglib, reportlab

📂 项目结构
.
├── Data/                       # 存放数据集
|  ├────Dataset
├── cv_chess_functions.py       # 核心函数库，封装了所有CV和图像处理功能
├── cv_chess_model_and_eval.ipynb # Jupyter Notebook，用于模型的训练、评估和分析
├── cv_chess_implement.ipynb    # Jupyter Notebook，主运行程序，用于读取、处理图片，生成结果图
├── model_VGG16.h5              # 训练好的模型权重文件
└── README.md                   # 本说明文件

🚀 运行指南
本项目推荐在Google Colab环境中运行，因为它提供了免费的GPU资源，可以大大加速模型的训练和推理。

在 Google Colab 中运行 (推荐)
第零步：下载数据集

从以下链接下载原始的棋子图片数据集：Chess Pieces Dataset on Kaggle 

将下载的压缩包 (data.zip) 上传到您Google Drive的项目主文件夹中。

### 第一步：准备数据 (自动划分训练/测试集)

在您的Google Drive中创建一个主文件夹 (例如 Chess_Project) 并将所有项目文件放入其中。

创建Data文件夹放置数据集。

将下载好的原始数据集解压到Data/Chess-Dataset文件夹中。

创建一个新的Colab Notebook，挂载您的Google Drive。

运行我们在对话中完善的数据划分脚本。并按照80/20的比例创建符合Keras ImageDataGenerator 要求的 train 和 test 目录结构。

### 第二步：训练模型

打开 cv_chess_model_and_eval.ipynb。

在菜单中选择 代码执行程序 (Runtime) -> 更改运行时类型 (Change runtime type)，并设置硬件加速器为 GPU。

确保Notebook中的数据路径指向您在第一步中创建的 Data 文件夹。

按顺序执行所有单元格。训练完成后，请务必将生成的 model_VGG16.h5 文件保存到您的项目主文件夹中。我们已经将保存代码修改为 model.save('/path/to/your/project/model_VGG16.h5')，它会自动完成这一步。

### 第三步：执行单张图片识别
我们提供了一个用于识别单张图片的流程。

准备环境: 在cv_chess_implement.ipynb中，运行我们最终版本的**“环境准备”单元格**。这会安装所有必需的系统依赖（如pycairo）并定义所有函数。

重启会话: 安装完成后，必须通过菜单 代码执行程序 (Runtime) -> 重启会Session (Restart session) 来使安装生效。

执行识别: 在重启后，运行我们最终版本的**“主程序”单元格**。它会：

1. 挂载Drive并加载您的模型和待识别的图片。

2. 要求您在代码中指定待识别图片的路径。

3. 执行包含透视变换和投影分割法的完整识别流程。（我们对测试图片test_image.jpeg已经做好了参数调试，您可以直接使用我们提供的测试图片得到结果"current_board.svg"）

4. 输出最终的FEN字符串、ASCII棋盘和生成的current_board.svg图像。

- 在本地运行 (实时识别)

确保您的电脑上已安装Python和所有在技术栈中列出的库。

将项目文件（包括model_VGG16.h5）放在同一个目录下。

运行主程序（同Colab平台方案）


🤝 致谢
本项目Andrew Underwood的基础上进行了大量的调试、优化和功能完善，特别是针对在Google Colab等云端环境中运行的适配和问题解决。

原始项目文章: Board Game Image Recognition using Neural Networks on Towards Data Science
