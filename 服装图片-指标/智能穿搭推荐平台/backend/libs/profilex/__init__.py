"""ProfileX - 轻量用户画像接口

提供：
 - get_profile(user_id) -> dict
 - update_profile(user_id, data) -> dict
 - compute_style_vector(profile) -> list[float]

实现原则：轻量、可复用、与 `backend.models.UserProfile` 对齐。

示例：
>>> from backend.libs.profilex import compute_style_vector, get_sample_profile, demo
>>> vec = compute_style_vector(get_sample_profile())
>>> print(len(vec), vec)
"""
from .core import get_profile, update_profile, compute_style_vector
from .core import _validate_profile_data as validate_profile_data  # 供调试/测试使用
from .consts import VECTOR_LENGTH

__all__ = [
	'get_profile', 'update_profile', 'compute_style_vector',
	'validate_profile_data', 'VECTOR_LENGTH', 'get_sample_profile', 'demo_profile'
]

__version__ = '0.1.0'


def get_sample_profile() -> dict:
	"""返回一个用于 demo 或测试的示例画像 dict（不会写入 DB）。"""
	return {
		'age': 28,
		'gender': '女',
		'height': 165,
		'weight': 52,
		'body_type': '沙漏形',
		'skin_tone': '中性色调',
		'preferred_styles': ['休闲舒适', '时尚潮流'],
		'preferred_colors': ['蓝色', '白色']
	}


def demo_profile(print_output: bool = True) -> dict:
	"""运行一个本地 demo：生成示例画像并计算向量。

	返回：{'profile': dict, 'vector': list(float)}；如果 print_output=True，会打印结果。
	"""
	prof = get_sample_profile()
	vec = compute_style_vector(prof)
	out = {'profile': prof, 'vector': vec}
	if print_output:
		try:
			import json
			print('Sample profile:')
			print(json.dumps(prof, ensure_ascii=False, indent=2))
			print(f'Computed vector (len={len(vec)}):')
			print(vec)
		except Exception:
			# 不在意打印失败
			pass
	return out


def _run_demo_cli():
	"""供模块以脚本方式运行的简易入口。"""
	demo_profile(True)


if __name__ == '__main__':
	_run_demo_cli()
