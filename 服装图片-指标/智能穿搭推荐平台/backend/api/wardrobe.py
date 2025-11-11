"""
衣橱管理 API
"""
from flask import request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from backend.api import wardrobe_bp
from backend.models import db, ClothingItem

@wardrobe_bp.route('/items', methods=['GET'])
@login_required
def get_wardrobe_items():
    """获取用户的所有衣物"""
    try:
        items = ClothingItem.query.filter_by(user_id=current_user.id).all()
        return jsonify({
            'items': [item.to_dict() for item in items]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wardrobe_bp.route('/items', methods=['POST'])
@login_required
def add_clothing_item():
    """添加衣物到衣橱"""
    try:
        data = request.get_json()
        
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
        
        return jsonify({
            'message': '添加成功',
            'item': item.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@wardrobe_bp.route('/items/<int:item_id>', methods=['DELETE'])
@login_required
def delete_clothing_item(item_id):
    """删除衣物"""
    try:
        item = ClothingItem.query.filter_by(id=item_id, user_id=current_user.id).first()
        
        if not item:
            return jsonify({'error': '衣物不存在'}), 404
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'message': '删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@wardrobe_bp.route('/items/<int:item_id>', methods=['PUT'])
@login_required
def update_clothing_item(item_id):
    """更新衣物信息"""
    try:
        item = ClothingItem.query.filter_by(id=item_id, user_id=current_user.id).first()
        
        if not item:
            return jsonify({'error': '衣物不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        for key in ['name', 'category', 'subcategory', 'color', 'pattern', 
                    'material', 'brand', 'size', 'style', 'season', 'occasion', 'price']:
            if key in data:
                setattr(item, key, data[key])
        
        db.session.commit()
        
        return jsonify({
            'message': '更新成功',
            'item': item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
