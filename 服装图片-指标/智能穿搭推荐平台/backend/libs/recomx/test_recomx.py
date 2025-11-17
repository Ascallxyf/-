"""RecomX 模块测试与使用示例

本文件演示如何使用 RecomX 提供的三个核心 API。

运行测试:
    python -m pytest backend/libs/recomx/test_recomx.py -v
    
或直接运行:
    python backend/libs/recomx/test_recomx.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime


def test_recommend_outfit_basic():
    """测试基础推荐功能"""
    print("\n" + "="*70)
    print("TEST 1: 基础推荐功能 (recommend_outfit)")
    print("="*70)
    
    # 添加项目路径
    project_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(project_root))
    
    # 创建 Flask 应用上下文
    from backend.app import create_app
    from backend.config.config import config
    
    app = create_app(config['testing'])
    
    with app.app_context():
        from backend.models.database import db, User, ClothingItem, UserProfile
        from backend.libs.recomx.core import recommend_outfit
        
        # 清空测试数据
        db.drop_all()
        db.create_all()
        
        # 创建测试用户
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password'
        )
        db.session.add(user)
        db.session.commit()
        
        print(f"✓ 创建测试用户: ID={user.id}")
        
        # 创建用户画像
        profile = UserProfile(
            user_id=user.id,
            age=25,
            gender='女',
            body_type='沙漏形',
            skin_tone='暖色调'
        )
        db.session.add(profile)
        db.session.commit()
        
        print(f"✓ 创建用户画像")
        
        # 创建衣物
        items_data = [
            {
                'user_id': user.id,
                'name': '白色T恤',
                'category': '上装',
                'color': '白色',
                'season': '春夏',
                'occasion': '日常'
            },
            {
                'user_id': user.id,
                'name': '牛仔裤',
                'category': '下装',
                'color': '深蓝',
                'season': '春夏秋冬',
                'occasion': '日常'
            },
            {
                'user_id': user.id,
                'name': '黑色皮鞋',
                'category': '鞋子',
                'color': '黑色',
                'season': '春夏秋冬',
                'occasion': '商务'
            }
        ]
        
        for item_data in items_data:
            item = ClothingItem(**item_data)
            db.session.add(item)
        
        db.session.commit()
        print(f"✓ 创建 {len(items_data)} 件衣物")
        
        # ───────────────────────────────────────────────────────────────
        # 测试1: 成功推荐
        # ───────────────────────────────────────────────────────────────
        print("\n[测试1a] 正常推荐请求:")
        result = recommend_outfit(
            user_id=user.id,
            context={
                'occasion': '日常',
                'weather': '晴天',
                'season': '春季',
                'limit': 5
            }
        )
        
        print(f"  状态: {result.get('status')}")
        print(f"  推荐理由: {result.get('rationale')}")
        print(f"  置信度: {result.get('confidence')}")
        print(f"  推荐数量: {len(result.get('items', []))}")
        print(f"  上下文: {json.dumps(result.get('context'), indent=2, ensure_ascii=False)}")
        
        assert result['status'] == 'success', "推荐应该成功"
        assert len(result.get('items', [])) > 0, "应该返回至少一个推荐"
        
        # ───────────────────────────────────────────────────────────────
        # 测试2: 空衣橱
        # ───────────────────────────────────────────────────────────────
        print("\n[测试1b] 空衣橱测试:")
        user2 = User(
            username='emptyuser',
            email='empty@example.com',
            password_hash='hashed'
        )
        db.session.add(user2)
        db.session.commit()
        
        profile2 = UserProfile(user_id=user2.id)
        db.session.add(profile2)
        db.session.commit()
        
        result = recommend_outfit(
            user_id=user2.id,
            context={'occasion': '日常'}
        )
        
        print(f"  状态: {result.get('status')}")
        print(f"  错误: {result.get('error')}")
        
        assert result['status'] == 'error', "空衣橱应该返回错误"
        assert result.get('error_code') == 'WARDROBE_EMPTY'
        
        # ───────────────────────────────────────────────────────────────
        # 测试3: 用户不存在
        # ───────────────────────────────────────────────────────────────
        print("\n[测试1c] 用户不存在测试:")
        result = recommend_outfit(
            user_id=99999,
            context={'occasion': '日常'}
        )
        
        print(f"  状态: {result.get('status')}")
        print(f"  错误: {result.get('error')}")
        
        assert result['status'] == 'error', "用户不存在应该返回错误"
        assert result.get('error_code') == 'USER_NOT_FOUND'
        
        print("\n✓ 所有推荐测试通过！")


def test_save_and_load_history():
    """测试历史记录保存和加载"""
    print("\n" + "="*70)
    print("TEST 2: 历史记录管理 (save_history + load_history)")
    print("="*70)
    
    project_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(project_root))
    
    from backend.app import create_app
    from backend.config.config import config
    
    app = create_app(config['testing'])
    
    with app.app_context():
        from backend.models.database import db, User, ClothingItem, UserProfile
        from backend.libs.recomx.core import (
            recommend_outfit, 
            save_history, 
            load_history
        )
        
        # 清空测试数据
        db.drop_all()
        db.create_all()
        
        # 创建测试用户和衣物
        user = User(
            username='history_test',
            email='history@example.com',
            password_hash='hashed'
        )
        db.session.add(user)
        db.session.commit()
        
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()
        
        # 创建衣物
        for i in range(3):
            item = ClothingItem(
                user_id=user.id,
                name=f'衣物{i}',
                category=['上装', '下装', '鞋子'][i],
                color='随机'
            )
            db.session.add(item)
        db.session.commit()
        
        print(f"✓ 创建测试用户和衣物")
        
        # ───────────────────────────────────────────────────────────────
        # 生成推荐
        # ───────────────────────────────────────────────────────────────
        print("\n[测试2a] 生成推荐:")
        rec_result = recommend_outfit(
            user_id=user.id,
            context={
                'occasion': '约会',
                'weather': '晴天',
                'season': '春季'
            }
        )
        print(f"  推荐状态: {rec_result['status']}")
        
        # ───────────────────────────────────────────────────────────────
        # 保存推荐历史
        # ───────────────────────────────────────────────────────────────
        print("\n[测试2b] 保存推荐历史:")
        save_result = save_history(user.id, rec_result)
        
        print(f"  保存状态: {save_result['status']}")
        print(f"  历史ID: {save_result.get('history_id')}")
        print(f"  保存时间: {save_result.get('saved_at')}")
        
        assert save_result['status'] == 'success', "保存应该成功"
        assert save_result.get('history_id') is not None, "应该返回有效的历史ID"
        
        history_id = save_result['history_id']
        
        # ───────────────────────────────────────────────────────────────
        # 加载推荐历史
        # ───────────────────────────────────────────────────────────────
        print("\n[测试2c] 加载推荐历史:")
        history = load_history(user.id, limit=10)
        
        print(f"  返回历史记录数: {len(history)}")
        
        if history:
            latest = history[0]
            print(f"  最新记录ID: {latest['recommendation_id']}")
            print(f"  场合: {latest['context']['occasion']}")
            print(f"  天气: {latest['context']['weather']}")
            print(f"  置信度: {latest['confidence']}")
            print(f"  服装数: {len(latest['items'])}")
        
        assert len(history) > 0, "应该返回至少一条历史记录"
        assert history[0]['recommendation_id'] == history_id, "最新记录ID应该匹配"
        
        # ───────────────────────────────────────────────────────────────
        # 保存多条历史
        # ───────────────────────────────────────────────────────────────
        print("\n[测试2d] 保存多条历史:")
        for i in range(3):
            context = {
                'occasion': ['商务', '休闲', '约会'][i],
                'weather': ['晴天', '雨天', '阴天'][i],
                'season': '春季'
            }
            rec = recommend_outfit(user.id, context)
            save_history(user.id, rec)
        
        history = load_history(user.id, limit=10)
        print(f"  总历史记录数: {len(history)}")
        print(f"  前3条:")
        for i, rec in enumerate(history[:3]):
            print(f"    [{i+1}] {rec['context']['occasion']} - {rec['created_at']}")
        
        assert len(history) >= 4, "应该至少有4条历史记录"
        
        print("\n✓ 所有历史记录测试通过！")


def test_data_structure():
    """测试返回数据结构"""
    print("\n" + "="*70)
    print("TEST 3: 数据结构验证")
    print("="*70)
    
    project_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(project_root))
    
    from backend.app import create_app
    from backend.config.config import config
    
    app = create_app(config['testing'])
    
    with app.app_context():
        from backend.models.database import db, User, ClothingItem, UserProfile
        from backend.libs.recomx.core import recommend_outfit
        
        db.drop_all()
        db.create_all()
        
        # 创建测试数据
        user = User(
            username='struct_test',
            email='struct@example.com',
            password_hash='hashed'
        )
        db.session.add(user)
        db.session.commit()
        
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()
        
        item = ClothingItem(
            user_id=user.id,
            name='测试衣物',
            category='上装',
            color='红色'
        )
        db.session.add(item)
        db.session.commit()
        
        # ───────────────────────────────────────────────────────────────
        # 验证推荐结果结构
        # ───────────────────────────────────────────────────────────────
        print("\n[测试3a] 成功推荐返回结构:")
        result = recommend_outfit(user.id, {'occasion': '日常'})
        
        required_keys = ['status', 'items', 'rationale', 'confidence', 'style_analysis', 'context']
        
        print(f"  返回字段:")
        for key in required_keys:
            value = result.get(key)
            print(f"    - {key}: {type(value).__name__}")
            assert key in result, f"缺少必需字段: {key}"
        
        print(f"\n  数据类型检查:")
        assert isinstance(result['status'], str), "status 应该是字符串"
        assert isinstance(result['items'], list), "items 应该是列表"
        assert isinstance(result['rationale'], str), "rationale 应该是字符串"
        assert isinstance(result['confidence'], (int, float)), "confidence 应该是数字"
        assert isinstance(result['context'], dict), "context 应该是字典"
        
        print(f"    ✓ 所有字段类型正确")
        
        # ───────────────────────────────────────────────────────────────
        # 验证错误响应结构
        # ───────────────────────────────────────────────────────────────
        print("\n[测试3b] 错误推荐返回结构:")
        error_result = recommend_outfit(99999, {})
        
        print(f"  返回字段:")
        for key in required_keys:
            assert key in error_result, f"缺少必需字段: {key}"
        
        assert error_result['status'] == 'error', "错误状态应该是 'error'"
        assert 'error_code' in error_result, "错误响应应该包含 error_code"
        
        print(f"  错误代码: {error_result.get('error_code')}")
        print(f"  ✓ 错误结构正确")
        
        print("\n✓ 所有数据结构测试通过！")


if __name__ == '__main__':
    print("\n" + "█"*70)
    print("  RecomX 模块综合测试")
    print("█"*70)
    
    try:
        test_recommend_outfit_basic()
        test_save_and_load_history()
        test_data_structure()
        
        print("\n" + "█"*70)
        print("  ✓ 所有测试通过!")
        print("█"*70 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
