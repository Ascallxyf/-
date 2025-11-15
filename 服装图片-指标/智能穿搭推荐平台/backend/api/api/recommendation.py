"""推荐服务 API"""
from flask import request, current_app
from flask_login import login_required, current_user

from backend.api import recommendation_bp
from backend.api.utils import respond, collect_validation_errors
from backend.libs.apix import success, error, validation_error, validate_recommendation_context
from backend.libs.recomx import recommend_outfit as recomx_recommend_outfit, save_history, load_history

@recommendation_bp.route('/outfit', methods=['POST'])
@login_required
def recommend_outfit():
    """获取穿搭推荐"""
    try:
        data = request.get_json() or {}

        context_payload = {
            'occasion': data.get('occasion', '日常'),
            'weather': data.get('weather', '晴天'),
            'season': data.get('season', '春季'),
            'limit': data.get('limit', 5)
        }
        validation_result = validate_recommendation_context(context_payload)
        if not validation_result.is_valid():
            return respond(validation_error(collect_validation_errors(validation_result)))

        recommendation = recomx_recommend_outfit(current_user.id, context_payload)
        if recommendation.get('error'):
            return respond(error(recommendation['error'], status=400))

        history = save_history(current_user.id, recommendation)
        payload = success(
            {
                'recommendation': recommendation,
                'history': history
            },
            message='获取推荐成功'
        )
        return respond(payload)
        
    except Exception as e:
        return respond(error(e))

@recommendation_bp.route('/style', methods=['POST'])
@login_required
def analyze_style():
    """分析服装风格"""
    try:
        data = request.get_json()
        image_url = data.get('image_url')
        
        if not image_url:
            return respond(error('缺少图片URL', status=400))
        
        # 调用风格分析器
        analysis = current_app.style_analyzer.analyze_style(image_url)
        return respond(success(analysis, message='分析成功'))
        
    except Exception as e:
        return respond(error(e))

@recommendation_bp.route('/history', methods=['GET'])
@login_required
def get_recommendation_history():
    """获取推荐历史"""
    try:
        limit = min(int(request.args.get('limit', 20)), 100)
        history = load_history(current_user.id, limit)
        return respond(success({'history': history}, message='获取历史成功'))
        
    except Exception as e:
        return respond(error(e))
