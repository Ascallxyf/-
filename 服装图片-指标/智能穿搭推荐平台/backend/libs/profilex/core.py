"""ProfileX 核心实现

职责：
    - 用户画像的读取与更新（对接 backend.models.UserProfile）
    - 将画像转换为推荐可用的数值向量（固定维度）

对外契约：
    get_profile(user_id: int) -> dict
    update_profile(user_id: int, data: dict) -> dict
    compute_style_vector(profile: dict) -> list[float]

异常策略：校验失败 -> ValueError；系统错误 -> RuntimeError
"""
from __future__ import annotations
from typing import Dict, Any, List
import json
from backend.models import db, UserProfile
from .consts import GENDER_MAP, BODY_LIST, SKIN_LIST, VECTOR_LENGTH, stable_map


# ---- 辅助: 校验/清洗输入 ----
def _validate_profile_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """只保留允许的字段并做最小校验，抛出 ValueError 表示输入问题。"""
    allowed = {
        'age': int,
        'gender': (str, type(None)),
        'height': (int, float, type(None)),
        'weight': (int, float, type(None)),
        'body_type': (str, type(None)),
        'skin_tone': (str, type(None)),
        'preferred_styles': (list, type(None)),
        'preferred_colors': (list, type(None)),
        'budget_range': (str, type(None)),
        'lifestyle': (str, type(None)),
        'work_environment': (str, type(None)),
    }

    clean: Dict[str, Any] = {}
    for k, v in data.items():
        if k not in allowed:
            continue
        expected = allowed[k]
        if v is None:
            clean[k] = None
            continue
        if not isinstance(v, expected):
            raise ValueError(f"字段 {k} 类型错误，期望 {expected}，但收到 {type(v)}")
        # 简单范围校验
        if k == 'age' and (v < 0 or v > 120):
            raise ValueError('age 值不在合理范围')
        clean[k] = v
    return clean


def get_profile(user_id: int) -> Dict[str, Any]:
    """从数据库加载用户画像并以 JSON-可序列化的 dict 返回。

    Raises:
        ValueError: 当 user_id 无效或未找到画像时
        RuntimeError: DB 操作出错
    """
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError('user_id 必须为正整数')
    try:
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            raise ValueError(f'未找到 user_id={user_id} 的画像')
        return profile.to_dict()
    except ValueError:
        raise
    except Exception as e:
        raise RuntimeError(f'查询画像失败: {e}')


def update_profile(user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """校验并持久化用户画像更新，返回最新画像 dict。

    行为：
    - 仅接受白名单字段
    - 自动创建不存在的 UserProfile 记录
    - 更新后计算并存储 style_vector
    """
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError('user_id 必须为正整数')

    clean = _validate_profile_data(data)

    try:
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.session.add(profile)

        # 赋值并处理 JSON 字段
        if 'preferred_styles' in clean:
            profile.preferred_styles = json.dumps(clean.get('preferred_styles') or [])
        if 'preferred_colors' in clean:
            profile.preferred_colors = json.dumps(clean.get('preferred_colors') or [])

        # 直接映射其余允许字段
        for f in ('age', 'gender', 'height', 'weight', 'body_type', 'skin_tone', 'budget_range', 'lifestyle', 'work_environment'):
            if f in clean:
                setattr(profile, f, clean[f])

        # 计算并持久化风格向量（作为 JSON 文本），保证向量稳定
        profile_dict = profile.to_dict()
        vec = compute_style_vector(profile_dict)
        profile.style_vector = json.dumps(vec)

        db.session.commit()
        return profile.to_dict()
    except ValueError:
        raise
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f'更新画像失败: {e}')


def compute_style_vector(profile: Dict[str, Any]) -> List[float]:
    """把画像映射为固定长度的数值向量（长度 20），说明：

    向量结构 (示例，总长度 = 20)：
    - [0] 年龄归一化 (age / 100)
    - [1:4] 性别 one-hot (男, 女, 其他)
    - [4:9] 体型 one-hot (梨形, 苹果形, 沙漏形, 矩形, 倒三角)
    - [9:12] 肤色 one-hot (暖色调, 冷色调, 中性色调)
    - [12:16] 前 4 个偏好风格的稳定数值映射（缺省为0）
    - [16:20] 前 4 个偏好颜色的稳定数值映射（缺省为0）

    设计原则：易解释、维度稳定、对缺失值鲁棒。
    """
    # 安全读取字段
    age = (profile.get('age') or 0)
    try:
        age_f = float(age)
    except Exception:
        age_f = 0.0
    age_norm = max(0.0, min(age_f / 100.0, 1.0))

    gender = (profile.get('gender') or '').strip()
    gender_vec = [1.0 if gender == g else 0.0 for g in GENDER_MAP]
    # 其它 -> 第三个槽
    if sum(gender_vec) == 0:
        gender_vec.append(1.0)
    else:
        gender_vec.append(0.0)

    body = (profile.get('body_type') or '').strip()
    body_vec = [1.0 if body == b else 0.0 for b in BODY_LIST]

    skin = (profile.get('skin_tone') or '').strip()
    skin_vec = [1.0 if skin == s else 0.0 for s in SKIN_LIST]
    # 如果都不是，保持 0 向量

    # 稳定映射字符串到 [0,1) 的数值：用可复现的简单映射（字符码和模运算）
    pref_styles = profile.get('preferred_styles') or []
    if isinstance(pref_styles, str):
        try:
            pref_styles = json.loads(pref_styles)
        except Exception:
            pref_styles = []
    styles_vec = [stable_map(pref_styles[i]) if i < len(pref_styles) else 0.0 for i in range(4)]

    pref_colors = profile.get('preferred_colors') or []
    if isinstance(pref_colors, str):
        try:
            pref_colors = json.loads(pref_colors)
        except Exception:
            pref_colors = []
    colors_vec = [stable_map(pref_colors[i]) if i < len(pref_colors) else 0.0 for i in range(4)]

    vec: List[float] = [age_norm] + gender_vec + body_vec + skin_vec + styles_vec + colors_vec
    # 最终保证长度为 VECTOR_LENGTH
    if len(vec) < VECTOR_LENGTH:
        vec += [0.0] * (VECTOR_LENGTH - len(vec))
    else:
        vec = vec[:VECTOR_LENGTH]
    return vec
