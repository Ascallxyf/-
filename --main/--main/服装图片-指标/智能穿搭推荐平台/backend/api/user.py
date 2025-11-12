"""
用户画像 API
"""
from flask import request, jsonify
from flask_login import login_required, current_user
from backend.api import user_bp
from backend.models import db, UserProfile
import json

@user_bp.route('/profile', methods=['GET'])
@login_required
def get_user_profile():
    """获取用户画像"""
    try:
        if not current_user.profile:
            return jsonify({'error': '用户画像不存在'}), 404
        
        return jsonify(current_user.profile.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile', methods=['POST', 'PUT'])
@login_required
def update_user_profile():
    """更新用户画像"""
    try:
        data = request.get_json()
        
        profile = current_user.profile
        if not profile:
            profile = UserProfile(user_id=current_user.id)
            db.session.add(profile)
        
        # 更新基本信息
        for key in ['age', 'gender', 'height', 'weight', 'body_type', 
                    'skin_tone', 'budget_range', 'lifestyle', 'work_environment']:
            if key in data:
                setattr(profile, key, data[key])
        
        # 更新偏好（JSON格式）
        if 'preferred_styles' in data:
            profile.preferred_styles = json.dumps(data['preferred_styles'], ensure_ascii=False)
        
        if 'preferred_colors' in data:
            profile.preferred_colors = json.dumps(data['preferred_colors'], ensure_ascii=False)
        
        db.session.commit()
        
        return jsonify({
            'message': '更新成功',
            'profile': profile.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
