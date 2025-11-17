# RecomX API 快速参考

## 导入
```python
from backend.libs.recomx import recommend_outfit, save_history, load_history
```

---

## API 速查

### 1️⃣ 生成推荐
```python
result = recommend_outfit(user_id, context)
```

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `user_id` | int | 用户ID | `1` |
| `context` | dict | 推荐上下文 | 见下表 |

**context 参数**:

| 字段 | 类型 | 必需 | 默认值 | 示例 |
|------|------|------|--------|------|
| `occasion` | str | 否 | '日常' | '商务', '约会', '运动' |
| `weather` | str | 否 | '晴天' | '晴', '雨', '雪' |
| `season` | str | 否 | '春季' | '春', '夏', '秋', '冬' |
| `location` | str | 否 | None | '室内', '室外', '办公室' |
| `limit` | int | 否 | 5 | 1-20 |

**返回值** (成功):
```python
{
    'status': 'success',
    'items': [...],           # 推荐的衣服列表
    'rationale': '...',       # 推荐理由
    'confidence': 0.85,       # 置信度
    'style_analysis': {...},  # 风格分析
    'context': {...},         # 推荐上下文
    'total': 3                # 返回数量
}
```

**错误代码**:
- `USER_NOT_FOUND` - 用户不存在
- `WARDROBE_EMPTY` - 衣橱为空
- `RECOMMENDATION_FAILED` - 推荐失败
- `RECOMMENDATION_ERROR` - 其他错误

---

### 2️⃣ 保存历史
```python
result = save_history(user_id, recommendation)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `user_id` | int | 用户ID |
| `recommendation` | dict | 推荐结果 (recommend_outfit 的返回值) |

**返回值** (成功):
```python
{
    'history_id': 42,
    'status': 'success',
    'saved_at': '2025-11-16T10:30:45...',
    'message': '推荐历史已保存'
}
```

---

### 3️⃣ 加载历史
```python
history = load_history(user_id, limit=20)
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `user_id` | int | - | 用户ID |
| `limit` | int | 20 | 返回数量 (1-100) |

**返回值**:
```python
[
    {
        'recommendation_id': 42,
        'items': [1, 3, 5],
        'context': {'occasion': '约会', 'weather': '晴天', 'season': '春季'},
        'rationale': '...',
        'confidence': 0.88,
        'created_at': '2025-11-16T10:30:45...',
        'user_feedback': 'liked|disliked|neutral|None',
        'feedback_reason': '...',
        'recommendation_type': 'outfit'
    },
    ...
]
```

---

## 代码示例

### 基础使用
```python
from backend.libs.recomx import recommend_outfit

# 生成推荐
result = recommend_outfit(1, {'occasion': '约会'})

if result['status'] == 'success':
    print(result['rationale'])
    for item in result['items']:
        print(f"  - {item['name']}")
else:
    print(f"错误: {result['error']}")
```

### 完整流程
```python
from backend.libs.recomx import recommend_outfit, save_history, load_history

# 1. 生成推荐
rec = recommend_outfit(1, {
    'occasion': '商务',
    'weather': '晴天',
    'season': '春季'
})

# 2. 保存历史
if rec['status'] == 'success':
    save_result = save_history(1, rec)
    print(f"保存 ID: {save_result['history_id']}")

# 3. 加载历史
history = load_history(1, limit=5)
print(f"最近 {len(history)} 条推荐")
```

### 在 API 中使用
```python
from flask import request, jsonify, Blueprint
from backend.libs.recomx import recommend_outfit, save_history

rec_bp = Blueprint('rec', __name__)

@rec_bp.route('/outfit', methods=['POST'])
def get_outfit():
    data = request.get_json()
    
    result = recommend_outfit(
        user_id=current_user.id,
        context={
            'occasion': data.get('occasion'),
            'weather': data.get('weather'),
            'season': data.get('season')
        }
    )
    
    if result['status'] == 'success':
        save_history(current_user.id, result)
        return jsonify(result), 200
    else:
        return jsonify(result), 400
```

---

## 常见场景

### 场景 1: 用户衣橱为空
```python
result = recommend_outfit(1, {})

if result['status'] == 'error':
    if result['error_code'] == 'WARDROBE_EMPTY':
        # 提示用户添加衣物
        return "请先添加衣物"
```

### 场景 2: 检查推荐质量
```python
result = recommend_outfit(1, {'occasion': '商务'})

if result['status'] == 'success':
    if result['confidence'] > 0.8:
        save_history(1, result)  # 置信度高才保存
    else:
        print(f"置信度低 ({result['confidence']:.1%})")
```

### 场景 3: 获取推荐理由
```python
result = recommend_outfit(1, {})

print(f"推荐理由: {result['rationale']}")
print(f"风格分析: {result['style_analysis']}")
print(f"置信度: {result['confidence']:.1%}")
```

---

## 错误处理

```python
result = recommend_outfit(user_id, context)

if result['status'] == 'error':
    code = result['error_code']
    msg = result['error']
    
    if code == 'USER_NOT_FOUND':
        # 用户不存在
        return "用户不存在，请先注册"
    
    elif code == 'WARDROBE_EMPTY':
        # 衣橱为空
        return "衣橱为空，请先添加衣物"
    
    elif code == 'RECOMMENDATION_FAILED':
        # 推荐失败
        return f"推荐失败: {msg}"
    
    else:
        # 其他错误
        return f"发生错误: {msg}"
```

---

## 性能建议

| 操作 | 预期耗时 | 建议 |
|------|---------|------|
| `recommend_outfit()` | 200-500ms | 异步调用、缓存结果 |
| `save_history()` | <50ms | 可异步保存 |
| `load_history()` | <100ms | 可缓存 |

### 优化建议
1. 缓存推荐结果 (Redis, 1 小时)
2. 异步保存历史 (Celery 后台任务)
3. 限流保护 (每用户/分钟限制)

---

## 文件位置

```
backend/libs/recomx/
├── core.py              ← 核心实现
├── __init__.py          ← 导入入口
├── README.md            ← 完整文档
├── test_recomx.py       ← 单元测试
└── IMPLEMENTATION.md    ← 实现说明
```

---

## 调试

```python
import logging

# 启用调试日志
logging.basicConfig(level=logging.DEBUG)

# 查看详细日志
result = recommend_outfit(1, {})
# 日志中会显示:
# - INFO: Recommendation generated for user 1...
# - WARNING: User X not found
# - ERROR: Recommendation failed
```

---

**最后更新**: 2025-11-16  
**版本**: v2.1
