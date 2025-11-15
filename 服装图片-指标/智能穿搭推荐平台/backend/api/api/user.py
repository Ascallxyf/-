"""用户画像 API"""
import json

from flask import request
from flask_login import login_required, current_user

from backend.api import user_bp
from backend.api.utils import respond, collect_validation_errors
from backend.libs.apix import success, error, not_found, validation_error, validate_profile
from backend.models import db, UserProfile

@user_bp.route('/profile', methods=['GET'])
@login_required
def get_user_profile():
    """获取用户画像"""
    try:
        if not current_user.profile:
            return respond(not_found('user_profile'))

        return respond(success(current_user.profile.to_dict(), message='获取成功'))
        
    except Exception as e:
        return respond(error(e))

@user_bp.route('/profile', methods=['POST', 'PUT'])
@login_required
def update_user_profile():
    """更新用户画像"""
    try:
        data = request.get_json() or {}

        validation_result = validate_profile(data)
        if not validation_result.is_valid():
            return respond(validation_error(collect_validation_errors(validation_result)))
        
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
        
        payload = success({'profile': profile.to_dict()}, message='更新成功')
        return respond(payload)
        
    except Exception as e:
        db.session.rollback()
        return respond(error(e))
