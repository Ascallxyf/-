"""ApiX 功能测试套件

运行方法：
    python backend/libs/apix/test_apix.py
"""
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

from backend.libs.apix.schemas import validate_wardrobe_item, validate_profile, ValidationResult
from backend.libs.apix.responses import (
    success,
    error,
    get_message,
    register_messages,
    throttled,
    ValidationException,
)


def test_validation():
    """测试数据验证功能"""
    print("=== 测试数据验证功能 ===")

    # 测试有效的衣橱物品
    valid_item = {
        'name': '白色T恤',
        'category': '上装',
        'color': '白色',
        'season': '夏季'
    }
    result = validate_wardrobe_item(valid_item)
    print(f"有效衣橱物品验证: {result.is_valid()}")
    if not result.is_valid():
        print(f"错误: {[e.to_dict() for e in result.errors]}")

    # 测试无效的衣橱物品
    invalid_item = {
        'name': '',  # 空名称
        'category': '无效类别',  # 无效类别
        'color': '无效颜色'  # 无效颜色
    }
    result = validate_wardrobe_item(invalid_item)
    print(f"无效衣橱物品验证: {result.is_valid()}")
    if not result.is_valid():
        print(f"错误: {[e.to_dict() for e in result.errors]}")


def test_responses():
    """测试响应格式化功能"""
    print("\n=== 测试响应格式化功能 ===")

    # 测试成功响应
    success_resp = success({'user_id': 123}, '用户创建成功')
    print(f"成功响应: {success_resp}")

    # 测试错误响应
    error_resp = error('用户名已存在', 409)
    print(f"错误响应: {error_resp}")

    # 测试异常响应
    try:
        raise ValueError('测试异常')
    except Exception as e:
        exception_resp = error(e)
        print(f"异常响应: {exception_resp}")


def test_internationalization():
    """测试国际化功能"""
    print("\n=== 测试国际化功能 ===")

    # 测试中文消息
    en_msg = get_message('validation_error', 'en')
    print(f"英文验证错误消息: {en_msg}")

    register_messages('zh', {'custom_key': '自定义消息'})
    custom = get_message('custom_key', 'zh')
    print(f"自定义消息: {custom}")


def test_debug_and_throttle():
    print("\n=== 测试调试字段与限流 ===")
    os.environ['APIX_DEBUG'] = '1'
    resp = error(ValueError('mock error'))
    print(f"包含调试信息: {'debug' in resp}")
    os.environ.pop('APIX_DEBUG', None)

    throttle_resp = throttled(30)
    print(f"限流响应: {throttle_resp}")


def test_validation_result_raise():
    print("\n=== 测试 ValidationResult raise ===")
    result = ValidationResult()
    result.add_error('field', 'required', '字段必填')
    try:
        result.raise_for_errors()
    except ValidationException as exc:
        print(f"捕获 ValidationException: {exc.details}")

    # 测试英文消息
    en_msg = get_message('validation_error', 'en')
    print(f"英文验证错误消息: {en_msg}")

if __name__ == '__main__':
    print("开始测试 ApiX 模块功能...\n")

    test_debug_and_throttle()
    test_validation_result_raise()
    test_validation()
    test_responses()
    test_internationalization()

    print("\n✅ ApiX 模块测试完成！")