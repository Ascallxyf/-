# StyleX 模块入口
# 作用：对外暴露风格分析的高层API，供 backend/api/recommendation.py 使用。
# 对外API：analyze_style, extract_tags
# TODO（实现者）：
# - 兼容 image_url 与 image_path 两种输入方式
# - 输出与 WardrobeX 的颜色格式一致（RGB整数三元组）
from .core import analyze_style, extract_tags

接口契约（对外暴露 API）
核心接口
接口名称	入参说明	出参说明	异常类型
analyze_style	- image_url: Optional [str] 图片 URL（二选一，优先度低于 image_path）
- image_path: Optional [str] 本地图片路径（二选一）	返回 Dict [str, Any]，结构如下：
{
"tags": List [str] 风格标签列表，
"palette": List [tuple [int, int, int]] 主色调调色板（RGB 格式）
}	- ValueError：未提供输入 / URL 无效 / 文件不存在
- RuntimeError：图片读取失败
extract_tags	- image_path: str 本地图片路径	返回 List [str] 风格标签列表（支持单独调用标签提取功能）	- ValueError：文件不存在
- RuntimeError：图片读取失败
辅助接口（内部暴露，供模块内调用）
接口名称	入参说明	出参说明	作用
_load_image	- image_url: Optional[str]
- image_path: Optional[str]	返回 PIL.Image.Image 图片对象	统一加载 URL / 本地图片
extract_color_palette	- image: PIL.Image.Image 图片对象
- n_colors: int = 5 需提取的主色调数量	返回 List [tuple [int, int, int]] 调色板（RGB 整数三元组，与 WardrobeX 一致）	提取图片主色调
三、核心功能说明
1. 图片多源加载
支持本地路径（image_path）直接读取，自动校验文件存在性；
支持网络 URL（image_url）下载，自动创建临时文件，读取后清理，避免磁盘残留；
内置超时控制（10 秒）和异常捕获，适配网络波动、无效 URL 等场景。
2. 调色板提取（与 WardrobeX 兼容）
采用 KMeans 聚类算法，对图片像素进行颜色聚合，默认提取 5 种主色调；
输出格式与 WardrobeX 完全一致（RGB 整数三元组，如 (255, 240, 220)），支持跨模块直接复用；
内置图片缩小预处理（100x100），在保证精度的同时提升计算性能。
3. 风格标签生成
基础版：结合「颜色特征」+「文件名语义」生成粗粒度标签（如 color_255_240_220、casual）；
扩展版：支持接入深度学习模型（如 ResNet、CLIP），输出细粒度风格标签（如「法式复古」「日式通勤」「街头潮流」）；
标签可扩展性：支持自定义标签词典，适配不同场景的标签体系（如职场、校园、户外）。
4. 异常处理与容错
输入校验：强制要求 image_url 或 image_path 二选一，否则直接抛出异常；
过程容错：图片读取、URL 下载、聚类计算等环节均有异常捕获，返回明确的错误信息（如「URL 下载失败：连接超时」）；
格式兼容：自动将图片转换为 RGB 格式，适配 PNG、JPG、WEBP 等常见图片格式。
四、依赖与环境要求
依赖库
依赖名称	版本要求	用途
Pillow	≥9.0.0	图片读取与格式转换
numpy	≥1.21.0	像素数据处理
scikit-learn	≥1.0.0	KMeans 颜色聚类
requests	≥2.26.0	URL 图片下载
python	≥3.8	语法兼容
环境要求
操作系统：Windows/macOS/Linux（无平台限制）；
硬件要求：基础 CPU 即可运行（扩展深度学习模型时需 GPU 支持）；
网络要求：仅当使用 image_url 时需联网，本地图片加载无需网络。
