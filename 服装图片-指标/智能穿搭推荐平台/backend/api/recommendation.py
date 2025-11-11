"""
推荐服务 API
"""
from flask import request, jsonify, current_app
from flask_login import login_required, current_user
from backend.api import recommendation_bp
from backend.models import ClothingItem, Recommendation, db

@recommendation_bp.route('/outfit', methods=['POST'])
@login_required
def recommend_outfit():
    """获取穿搭推荐"""
    try:
        data = request.get_json()
        
        # 获取用户衣橱
        clothing_items = ClothingItem.query.filter_by(user_id=current_user.id).all()
        
        if not clothing_items:
            return jsonify({'error': '衣橱为空，请先添加衣物'}), 400
        
        # 获取推荐参数
        occasion = data.get('occasion', '日常')
        weather = data.get('weather', '晴天')
        season = data.get('season', '春季')
        
        # 调用推荐引擎
        recommendations = current_app.recommendation_engine.recommend_outfit(
            clothing_items=clothing_items,
            user_profile=current_user.profile,
            occasion=occasion,
            weather=weather,
            season=season
        )
        
        return jsonify({
            'recommendations': recommendations
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recommendation_bp.route('/style', methods=['POST'])
@login_required
def analyze_style():
    """分析服装风格"""
    try:
        data = request.get_json()
        image_url = data.get('image_url')
        
        if not image_url:
            return jsonify({'error': '缺少图片URL'}), 400
        
        # 调用风格分析器
        analysis = current_app.style_analyzer.analyze_style(image_url)
        
        return jsonify(analysis), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recommendation_bp.route('/history', methods=['GET'])
@login_required
def get_recommendation_history():
    """获取推荐历史"""
    try:
        recommendations = Recommendation.query.filter_by(
            user_id=current_user.id
        ).order_by(Recommendation.created_at.desc()).limit(20).all()
        
        return jsonify({
            'recommendations': [rec.to_dict() for rec in recommendations]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
