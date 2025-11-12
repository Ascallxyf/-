# WardrobeX 模块入口
# 作用：对外暴露衣橱条目 CRUD 与图片处理相关的高层API。
# 对外API（core）：add_item, update_item, delete_item, list_items, process_upload
# 对外API（image_utils）：extract_color_palette, generate_thumbnail
# TODO（实现者）：
# - 与 ClothingItem 模型对接，保证字段一致（name/category/color/season/image_url）
# - 图片处理出错的容错与回滚（例如缩略图失败时不写入DB）
from .core import add_item, update_item, delete_item, list_items, process_upload
from .image_utils import extract_color_palette, generate_thumbnail
