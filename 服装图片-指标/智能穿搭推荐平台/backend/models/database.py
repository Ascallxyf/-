from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # 关系
    clothing_items = db.relationship('ClothingItem', backref='owner', lazy=True, cascade='all, delete-orphan')
    outfits = db.relationship('Outfit', backref='creator', lazy=True, cascade='all, delete-orphan')
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    recommendations = db.relationship('Recommendation', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }

class UserProfile(db.Model):
    """用户档案模型"""
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 基本信息
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    height = db.Column(db.Float)  # 身高 cm
    weight = db.Column(db.Float)  # 体重 kg
    
    # 体型特征
    body_type = db.Column(db.String(20))  # 梨形、苹果形、沙漏形等
    skin_tone = db.Column(db.String(20))  # 暖色调、冷色调、中性色调
    
    # 偏好设置
    preferred_styles = db.Column(db.Text)  # JSON格式存储偏好风格
    preferred_colors = db.Column(db.Text)  # JSON格式存储偏好颜色
    budget_range = db.Column(db.String(20))  # 预算范围
    
    # 场景偏好
    lifestyle = db.Column(db.String(50))  # 生活方式
    work_environment = db.Column(db.String(50))  # 工作环境
    
    # 系统计算字段
    style_vector = db.Column(db.Text)  # 风格向量
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'age': self.age,
            'gender': self.gender,
            'height': self.height,
            'weight': self.weight,
            'body_type': self.body_type,
            'skin_tone': self.skin_tone,
            'preferred_styles': json.loads(self.preferred_styles) if self.preferred_styles else [],
            'preferred_colors': json.loads(self.preferred_colors) if self.preferred_colors else [],
            'budget_range': self.budget_range,
            'lifestyle': self.lifestyle,
            'work_environment': self.work_environment,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ClothingItem(db.Model):
    """服装单品模型"""
    __tablename__ = 'clothing_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 基本信息
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 上装、下装、鞋子、配饰等
    subcategory = db.Column(db.String(50))  # 具体分类：衬衫、T恤、牛仔裤等
    
    # 属性信息
    color = db.Column(db.String(30))
    pattern = db.Column(db.String(30))  # 图案：纯色、条纹、格子等
    material = db.Column(db.String(50))  # 材质
    brand = db.Column(db.String(50))
    size = db.Column(db.String(10))
    
    # 风格属性
    style = db.Column(db.String(30))  # 风格：休闲、正式、运动等
    season = db.Column(db.String(20))  # 季节：春、夏、秋、冬、通用
    occasion = db.Column(db.String(50))  # 场合：工作、约会、运动等
    
    # 图片和特征
    image_url = db.Column(db.String(255))
    features = db.Column(db.Text)  # JSON格式存储图像特征
    tags = db.Column(db.Text)  # JSON格式存储标签
    
    # 元数据
    purchase_date = db.Column(db.Date)
    price = db.Column(db.Float)
    wear_count = db.Column(db.Integer, default=0)  # 穿着次数
    last_worn = db.Column(db.Date)  # 最后穿着日期
    rating = db.Column(db.Float)  # 用户评分
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'category': self.category,
            'subcategory': self.subcategory,
            'color': self.color,
            'pattern': self.pattern,
            'material': self.material,
            'brand': self.brand,
            'size': self.size,
            'style': self.style,
            'season': self.season,
            'occasion': self.occasion,
            'image_url': self.image_url,
            'features': json.loads(self.features) if self.features else {},
            'tags': json.loads(self.tags) if self.tags else [],
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'price': self.price,
            'wear_count': self.wear_count,
            'last_worn': self.last_worn.isoformat() if self.last_worn else None,
            'rating': self.rating,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Outfit(db.Model):
    """穿搭组合模型"""
    __tablename__ = 'outfits'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    clothing_items = db.Column(db.Text, nullable=False)  # JSON格式存储服装ID列表
    
    # 场景信息
    occasion = db.Column(db.String(50))
    season = db.Column(db.String(20))
    weather = db.Column(db.String(30))
    
    # 评价信息
    rating = db.Column(db.Float)
    wear_count = db.Column(db.Integer, default=0)
    last_worn = db.Column(db.Date)
    
    # 系统评分
    style_score = db.Column(db.Float)  # 风格匹配分数
    color_harmony = db.Column(db.Float)  # 色彩和谐度
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'clothing_items': json.loads(self.clothing_items) if self.clothing_items else [],
            'occasion': self.occasion,
            'season': self.season,
            'weather': self.weather,
            'rating': self.rating,
            'wear_count': self.wear_count,
            'last_worn': self.last_worn.isoformat() if self.last_worn else None,
            'style_score': self.style_score,
            'color_harmony': self.color_harmony,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Recommendation(db.Model):
    """推荐记录模型"""
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    recommendation_type = db.Column(db.String(20), default='outfit')  # outfit, purchase, style
    outfit_items = db.Column(db.Text)  # JSON格式存储推荐的服装ID
    
    # 推荐依据
    occasion = db.Column(db.String(50))
    weather = db.Column(db.String(30))
    season = db.Column(db.String(20))
    
    # 推荐质量
    confidence = db.Column(db.Float)  # 置信度
    reasoning = db.Column(db.Text)  # 推荐理由
    
    # 用户反馈
    user_feedback = db.Column(db.String(20))  # liked, disliked, neutral
    feedback_reason = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'recommendation_type': self.recommendation_type,
            'outfit_items': json.loads(self.outfit_items) if self.outfit_items else [],
            'occasion': self.occasion,
            'weather': self.weather,
            'season': self.season,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'user_feedback': self.user_feedback,
            'feedback_reason': self.feedback_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class StyleKnowledge(db.Model):
    """风格知识图谱模型"""
    __tablename__ = 'style_knowledge'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 实体信息
    entity_type = db.Column(db.String(20), nullable=False)  # color, style, category, etc.
    entity_name = db.Column(db.String(50), nullable=False)
    
    # 关系信息
    relation_type = db.Column(db.String(30))  # matches_with, conflicts_with, suitable_for
    target_entity = db.Column(db.String(50))
    
    # 属性信息
    attributes = db.Column(db.Text)  # JSON格式存储属性
    confidence = db.Column(db.Float, default=1.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_name': self.entity_name,
            'relation_type': self.relation_type,
            'target_entity': self.target_entity,
            'attributes': json.loads(self.attributes) if self.attributes else {},
            'confidence': self.confidence
        }