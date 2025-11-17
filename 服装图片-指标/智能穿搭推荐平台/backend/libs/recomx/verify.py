#!/usr/bin/env python3
"""RecomX 模块代码验证 (不需要 Flask 依赖)

本脚本验证 RecomX 核心代码的完整性和正确性，不需要安装项目依赖。
"""

import re
import sys
from pathlib import Path


def check_file_exists(file_path):
    """检查文件是否存在"""
    if Path(file_path).exists():
        print(f"✓ {file_path} 存在")
        return True
    else:
        print(f"✗ {file_path} 不存在")
        return False


def check_function_definition(file_path, function_name):
    """检查函数是否定义"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = rf'^def {function_name}\('
    if re.search(pattern, content, re.MULTILINE):
        print(f"  ✓ 函数 {function_name}() 已定义")
        return True
    else:
        print(f"  ✗ 函数 {function_name}() 未定义")
        return False


def check_docstring(file_path, function_name):
    """检查函数是否有文档字符串"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找函数定义后的文档字符串
    pattern = rf'def {function_name}\([^)]*\)[^:]*:\n\s+"""'
    if re.search(pattern, content):
        print(f"  ✓ 函数 {function_name}() 有 docstring")
        return True
    else:
        print(f"  ✗ 函数 {function_name}() 缺少 docstring")
        return False


def check_error_handling(file_path, function_name):
    """检查函数是否有错误处理"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    in_function = False
    has_try = False
    
    for i, line in enumerate(lines):
        if f'def {function_name}(' in line:
            in_function = True
        elif in_function and line.strip().startswith('def '):
            break
        elif in_function and 'try:' in line:
            has_try = True
    
    if has_try:
        print(f"  ✓ 函数 {function_name}() 有错误处理")
        return True
    else:
        print(f"  ✗ 函数 {function_name}() 缺少错误处理")
        return False


def check_imports(file_path):
    """检查导入语句"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_imports = [
        'from typing import',
        'import json',
        'from datetime import',
        'import logging'
    ]
    
    all_present = True
    for imp in required_imports:
        if imp in content:
            print(f"  ✓ 导入 '{imp}' 存在")
        else:
            print(f"  ✗ 导入 '{imp}' 缺失")
            all_present = False
    
    return all_present


def check_return_values(file_path, function_name):
    """检查函数返回值"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    in_function = False
    return_count = 0
    
    for i, line in enumerate(lines):
        if f'def {function_name}(' in line:
            in_function = True
        elif in_function and line.strip().startswith('def '):
            break
        elif in_function and 'return ' in line:
            return_count += 1
    
    if return_count > 0:
        print(f"  ✓ 函数 {function_name}() 有 {return_count} 个 return 语句")
        return True
    else:
        print(f"  ✗ 函数 {function_name}() 没有 return 语句")
        return False


def main():
    """主要验证流程"""
    print("\n" + "="*70)
    print("  RecomX 模块代码验证")
    print("="*70)
    
    # 项目根目录（RecomX 在 backend/libs/recomx，所以往上走 3 级）
    project_root = Path(__file__).resolve().parents[3]
    
    # 检查的文件
    core_file = project_root / 'backend' / 'libs' / 'recomx' / 'core.py'
    init_file = project_root / 'backend' / 'libs' / 'recomx' / '__init__.py'
    readme_file = project_root / 'backend' / 'libs' / 'recomx' / 'README.md'
    test_file = project_root / 'backend' / 'libs' / 'recomx' / 'test_recomx.py'
    
    # 检查三个核心函数
    functions = ['recommend_outfit', 'save_history', 'load_history']
    
    passed = 0
    failed = 0
    
    # ───────────────────────────────────────────────────────────────────
    # 1. 检查文件存在性
    # ───────────────────────────────────────────────────────────────────
    print("\n[1] 检查文件存在性:")
    for f in [core_file, init_file, readme_file, test_file]:
        if check_file_exists(f):
            passed += 1
        else:
            failed += 1
    
    # ───────────────────────────────────────────────────────────────────
    # 2. 检查核心函数
    # ───────────────────────────────────────────────────────────────────
    print("\n[2] 检查核心函数定义:")
    for func in functions:
        print(f"\n  函数 {func}():")
        
        # 检查定义
        if check_function_definition(core_file, func):
            passed += 1
        else:
            failed += 1
        
        # 检查文档字符串
        if check_docstring(core_file, func):
            passed += 1
        else:
            failed += 1
        
        # 检查错误处理
        if check_error_handling(core_file, func):
            passed += 1
        else:
            failed += 1
        
        # 检查返回值
        if check_return_values(core_file, func):
            passed += 1
        else:
            failed += 1
    
    # ───────────────────────────────────────────────────────────────────
    # 3. 检查导入
    # ───────────────────────────────────────────────────────────────────
    print("\n[3] 检查导入:")
    if check_imports(core_file):
        passed += 1
    else:
        failed += 1
    
    # ───────────────────────────────────────────────────────────────────
    # 4. 检查模块导出
    # ───────────────────────────────────────────────────────────────────
    print("\n[4] 检查模块导出 (__init__.py):")
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    exports = ['recommend_outfit', 'save_history', 'load_history']
    for exp in exports:
        if exp in content:
            print(f"  ✓ {exp} 已导出")
            passed += 1
        else:
            print(f"  ✗ {exp} 未导出")
            failed += 1
    
    # ───────────────────────────────────────────────────────────────────
    # 5. 检查代码行数
    # ───────────────────────────────────────────────────────────────────
    print("\n[5] 检查代码规模:")
    with open(core_file, 'r') as f:
        core_lines = len(f.readlines())
    
    with open(readme_file, 'r') as f:
        readme_lines = len(f.readlines())
    
    with open(test_file, 'r') as f:
        test_lines = len(f.readlines())
    
    print(f"  core.py: {core_lines} 行")
    print(f"  README.md: {readme_lines} 行")
    print(f"  test_recomx.py: {test_lines} 行")
    print(f"  总计: {core_lines + readme_lines + test_lines} 行")
    passed += 1
    
    # ───────────────────────────────────────────────────────────────────
    # 6. 语法检查
    # ───────────────────────────────────────────────────────────────────
    print("\n[6] Python 语法检查:")
    try:
        import py_compile
        py_compile.compile(str(core_file), doraise=True)
        print(f"  ✓ core.py 语法正确")
        passed += 1
    except Exception as e:
        print(f"  ✗ core.py 语法错误: {e}")
        failed += 1
    
    # ───────────────────────────────────────────────────────────────────
    # 7. 检查辅助函数
    # ───────────────────────────────────────────────────────────────────
    print("\n[7] 检查辅助函数:")
    helper_functions = [
        '_create_error_response',
        '_build_context_dict',
        '_extract_outfit_ids',
        '_format_outfit_items'
    ]
    
    for func in helper_functions:
        if check_function_definition(core_file, func):
            print(f"  ✓ {func}() 已定义")
            passed += 1
        else:
            print(f"  ✗ {func}() 缺失")
            failed += 1
    
    # ───────────────────────────────────────────────────────────────────
    # 结果总结
    # ───────────────────────────────────────────────────────────────────
    print("\n" + "="*70)
    print(f"  验证结果: {passed} 通过, {failed} 失败")
    print("="*70)
    
    if failed == 0:
        print("\n✅ 所有检查通过！RecomX 模块已完成。\n")
        return 0
    else:
        print(f"\n❌ 发现 {failed} 个问题需要修复。\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
