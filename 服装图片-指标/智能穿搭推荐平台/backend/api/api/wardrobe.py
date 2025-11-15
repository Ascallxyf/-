"""衣橱管理 API"""
from datetime import datetime

from flask import request
from flask_login import login_required, current_user

from backend.api import wardrobe_bp
from backend.api.utils import respond, collect_validation_errors
from backend.libs.apix import success, error, validation_error, not_found, validate_wardrobe_item
from backend.models import db, ClothingItem

@wardrobe_bp.route('/items', methods=['GET'])
@login_required
def get_wardrobe_items():
    """获取用户的所有衣物"""
    try:
        items = ClothingItem.query.filter_by(user_id=current_user.id).all()
        payload = success({'items': [item.to_dict() for item in items]}, message='获取成功')
        return respond(payload)
    except Exception as e:
        return respond(error(e))

@wardrobe_bp.route('/items', methods=['POST'])
@login_required
def add_clothing_item():
    """添加衣物到衣橱"""
    try:
        data = request.get_json() or {}

        validation_payload = {
            'name': data.get('name'),
            'category': data.get('category'),
            'color': data.get('color'),
            'season': data.get('season'),
            'image_url': data.get('image_url')
        }
        validation_result = validate_wardrobe_item(validation_payload)
        if not validation_result.is_valid():
            return respond(validation_error(collect_validation_errors(validation_result)))
        
        item = ClothingItem(
            user_id=current_user.id,
            name=data.get('name'),
            category=data.get('category'),
            subcategory=data.get('subcategory'),
            color=data.get('color'),
            pattern=data.get('pattern'),
            material=data.get('material'),
            brand=data.get('brand'),
            size=data.get('size'),
            style=data.get('style'),
            season=data.get('season'),
            occasion=data.get('occasion'),
            purchase_date=datetime.fromisoformat(data['purchase_date']) if data.get('purchase_date') else None,
            price=data.get('price'),
            image_url=data.get('image_url')
        )
        
        db.session.add(item)
        db.session.commit()
        
        payload = success({'item': item.to_dict()}, message='添加成功', status=201)
        return respond(payload)
        
    except Exception as e:
        db.session.rollback()
        return respond(error(e))

@wardrobe_bp.route('/items/<int:item_id>', methods=['DELETE'])
@login_required
def delete_clothing_item(item_id):
    """删除衣物"""
    try:
        item = ClothingItem.query.filter_by(id=item_id, user_id=current_user.id).first()
        
        if not item:
            return respond(not_found('wardrobe_item'))
        
        db.session.delete(item)
        db.session.commit()

        return respond(success(message='删除成功'))

    except Exception as e:
        db.session.rollback()
        return respond(error(e))

@wardrobe_bp.route('/items/<int:item_id>', methods=['PUT'])
@login_required
def update_clothing_item(item_id):
    """更新衣物信息"""
    try:
        item = ClothingItem.query.filter_by(id=item_id, user_id=current_user.id).first()
        
        if not item:
            return respond(not_found('wardrobe_item'))
        
        data = request.get_json() or {}

        validation_payload = {
            'name': data.get('name', item.name),
            'category': data.get('category', item.category),
            'color': data.get('color', item.color),
            'season': data.get('season', item.season),
            'image_url': data.get('image_url', item.image_url)
        }
        validation_result = validate_wardrobe_item(validation_payload)
        if not validation_result.is_valid():
            return respond(validation_error(collect_validation_errors(validation_result)))
        
        # 更新字段
        for key in ['name', 'category', 'subcategory', 'color', 'pattern', 
                    'material', 'brand', 'size', 'style', 'season', 'occasion', 'price']:
            if key in data:
                setattr(item, key, data[key])
        
        db.session.commit()
        
        payload = success({'item': item.to_dict()}, message='更新成功')
        return respond(payload)
        
    except Exception as e:
        db.session.rollback()
        return respond(error(e))
