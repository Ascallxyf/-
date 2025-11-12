import numpy as np
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

class UserProfiler:
    """用户画像分析器
    
    基于用户行为和偏好构建个性化用户画像
    """
    
    def __init__(self):
        self.body_type_mapping = self._init_body_type_mapping()
        self.skin_tone_mapping = self._init_skin_tone_mapping()
        self.style_preferences = self._init_style_preferences()
        
    def _init_body_type_mapping(self) -> Dict[str, Dict[str, Any]]:
        """初始化体型映射"""
        return {
            '梨形': {
                'characteristics': ['下半身较宽', '肩膀较窄', '腰部明显'],
                'suitable_styles': ['A字裙', '高腰裤', '宽肩上衣'],
                'avoid_styles': ['紧身下装', '低腰裤', '横纹下装'],
                'color_suggestions': {
                    '上装': ['亮色', '图案', '装饰'],
                    '下装': ['深色', '纯色', '简洁']
                }
            },
            '苹果形': {
                'characteristics': ['上半身较宽', '腰部不明显', '腿部相对较细'],
                'suitable_styles': ['V领', '直筒裙', '高腰设计'],
                'avoid_styles': ['紧身上衣', '横纹上装', '腰部装饰'],
                'color_suggestions': {
                    '上装': ['深色', '纯色', '垂直线条'],
                    '下装': ['亮色', '图案', '细节']
                }
            },
            '沙漏形': {
                'characteristics': ['肩膀和臀部同宽', '腰部明显收紧'],
                'suitable_styles': ['修身剪裁', '腰部强调', '包身裙'],
                'avoid_styles': ['宽松直筒', '遮盖腰线'],
                'color_suggestions': {
                    '上装': ['任意颜色'],
                    '下装': ['任意颜色']
                }
            },
            '矩形': {
                'characteristics': ['肩膀臀部腰部相近', '身材较直'],
                'suitable_styles': ['腰部装饰', '层次搭配', '曲线强调'],
                'avoid_styles': ['直筒剪裁', '无腰线设计'],
                'color_suggestions': {
                    '上装': ['图案', '装饰', '层次'],
                    '下装': ['A字剪裁', '褶皱设计']
                }
            },
            '倒三角': {
                'characteristics': ['肩膀较宽', '腰臀较窄', '上半身强壮'],
                'suitable_styles': ['A字下装', '宽松下装', '细肩带'],
                'avoid_styles': ['宽肩设计', '垫肩', '船领'],
                'color_suggestions': {
                    '上装': ['深色', '简洁', '垂直线条'],
                    '下装': ['亮色', '图案', '体积感']
                }
            }
        }
    
    def _init_skin_tone_mapping(self) -> Dict[str, Dict[str, Any]]:
        """初始化肤色映射"""
        return {
            '暖色调': {
                'characteristics': ['偏黄底调', '金色血管', '适合金饰'],
                'suitable_colors': ['暖色系', '橙色', '黄色', '暖红', '桃色', '奶油色'],
                'avoid_colors': ['冷粉', '冷蓝', '纯白', '银灰'],
                'makeup_suggestions': ['暖调粉底', '橙调口红', '金棕眼影']
            },
            '冷色调': {
                'characteristics': ['偏粉底调', '蓝色血管', '适合银饰'],
                'suitable_colors': ['冷色系', '蓝色', '紫色', '冷红', '纯白', '灰色'],
                'avoid_colors': ['橙色', '黄色', '暖棕', '奶油色'],
                'makeup_suggestions': ['冷调粉底', '浆果色口红', '冷调眼影']
            },
            '中性色调': {
                'characteristics': ['冷暖平衡', '适合多种颜色'],
                'suitable_colors': ['大部分颜色', '黑白灰', '各种饱和度'],
                'avoid_colors': ['极端冷暖色'],
                'makeup_suggestions': ['中性粉底', '万能色彩']
            }
        }
    
    def _init_style_preferences(self) -> Dict[str, Dict[str, Any]]:
        """初始化风格偏好映射"""
        return {
            '商务正式': {
                'personality': ['专业', '严谨', '权威'],
                'occasions': ['工作', '会议', '商务活动'],
                'key_pieces': ['西装', '衬衫', '皮鞋', '公文包'],
                'colors': ['黑色', '深蓝', '灰色', '白色'],
                'materials': ['羊毛', '真丝', '棉质'],
                'lifestyle': ['职场精英', '管理层', '专业人士']
            },
            '休闲舒适': {
                'personality': ['随性', '舒适', '自然'],
                'occasions': ['日常', '购物', '朋友聚会'],
                'key_pieces': ['T恤', '牛仔裤', '运动鞋', '卫衣'],
                'colors': ['任意颜色'],
                'materials': ['棉质', '针织', '牛仔布'],
                'lifestyle': ['学生', '自由职业', '家庭主妇']
            },
            '时尚潮流': {
                'personality': ['前卫', '个性', '追求新鲜'],
                'occasions': ['聚会', '约会', '社交活动'],
                'key_pieces': ['设计师单品', '潮牌', '配饰'],
                'colors': ['流行色', '撞色', '亮色'],
                'materials': ['各种新材质'],
                'lifestyle': ['时尚从业者', '艺术工作者', '年轻人']
            },
            '甜美可爱': {
                'personality': ['温柔', '可爱', '少女心'],
                'occasions': ['约会', '聚会', '日常'],
                'key_pieces': ['连衣裙', '蕾丝', '蝴蝶结', '平底鞋'],
                'colors': ['粉色', '白色', '浅蓝', '米色'],
                'materials': ['雪纺', '蕾丝', '棉质'],
                'lifestyle': ['学生', '年轻女性', '文职工作']
            }
        }
    
    def analyze_user_profile(self, user_data: Dict[str, Any], 
                           clothing_history: List[Dict[str, Any]] = None,
                           behavior_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """分析用户画像
        
        Args:
            user_data: 用户基本信息
            clothing_history: 服装历史记录
            behavior_data: 行为数据
            
        Returns:
            用户画像分析结果
        """
        try:
            # 基础画像分析
            basic_profile = self._analyze_basic_profile(user_data)
            
            # 穿衣偏好分析
            style_profile = self._analyze_style_preferences(clothing_history or [])
            
            # 行为模式分析
            behavior_profile = self._analyze_behavior_patterns(behavior_data or {})
            
            # 身材建议分析
            body_recommendations = self._get_body_type_recommendations(user_data)
            
            # 色彩建议分析
            color_recommendations = self._get_color_recommendations(user_data)
            
            # 综合画像
            comprehensive_profile = {
                'basic_info': basic_profile,
                'style_preferences': style_profile,
                'behavior_patterns': behavior_profile,
                'body_recommendations': body_recommendations,
                'color_recommendations': color_recommendations,
                'personality_insights': self._generate_personality_insights(style_profile, behavior_profile),
                'shopping_suggestions': self._generate_shopping_suggestions(style_profile, user_data),
                'updated_at': datetime.now().isoformat()
            }
            
            return comprehensive_profile
            
        except Exception as e:
            print(f"用户画像分析错误: {str(e)}")
            return self._get_default_profile()
    
    def _analyze_basic_profile(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析基础画像"""
        age = user_data.get('age', 25)
        gender = user_data.get('gender', '女')
        height = user_data.get('height', 165)
        weight = user_data.get('weight', 55)
        body_type = user_data.get('body_type', '矩形')
        skin_tone = user_data.get('skin_tone', '中性色调')
        
        # 计算BMI
        bmi = weight / ((height / 100) ** 2) if height > 0 else 22
        
        # 年龄段分析
        age_group = self._categorize_age(age)
        
        # 体型分析
        body_analysis = self._analyze_body_type(body_type, height, weight)
        
        return {
            'age': age,
            'age_group': age_group,
            'gender': gender,
            'height': height,
            'weight': weight,
            'bmi': round(bmi, 1),
            'body_type': body_type,
            'skin_tone': skin_tone,
            'body_analysis': body_analysis
        }
    
    def _categorize_age(self, age: int) -> str:
        """年龄分组"""
        if age < 20:
            return '青少年'
        elif age < 30:
            return '青年'
        elif age < 45:
            return '中年'
        else:
            return '成熟'
    
    def _analyze_body_type(self, body_type: str, height: float, weight: float) -> Dict[str, Any]:
        """分析体型特征"""
        body_info = self.body_type_mapping.get(body_type, {})
        
        # BMI分析
        bmi = weight / ((height / 100) ** 2) if height > 0 else 22
        if bmi < 18.5:
            weight_category = '偏瘦'
        elif bmi < 24:
            weight_category = '正常'
        elif bmi < 28:
            weight_category = '偏胖'
        else:
            weight_category = '肥胖'
        
        return {
            'body_type': body_type,
            'weight_category': weight_category,
            'characteristics': body_info.get('characteristics', []),
            'suitable_styles': body_info.get('suitable_styles', []),
            'avoid_styles': body_info.get('avoid_styles', [])
        }
    
    def _analyze_style_preferences(self, clothing_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析穿衣偏好"""
        if not clothing_history:
            return {'dominant_styles': [], 'preferred_colors': [], 'preferred_categories': []}
        
        # 统计风格偏好
        styles = [item.get('style', '休闲') for item in clothing_history]
        style_counts = defaultdict(int)
        for style in styles:
            style_counts[style] += 1
        
        # 统计颜色偏好
        colors = [item.get('color', '未知') for item in clothing_history]
        color_counts = defaultdict(int)
        for color in colors:
            color_counts[color] += 1
        
        # 统计类别偏好
        categories = [item.get('category', '其他') for item in clothing_history]
        category_counts = defaultdict(int)
        for category in categories:
            category_counts[category] += 1
        
        # 统计品牌偏好
        brands = [item.get('brand', '未知') for item in clothing_history if item.get('brand')]
        brand_counts = defaultdict(int)
        for brand in brands:
            brand_counts[brand] += 1
        
        # 分析价格偏好
        prices = [item.get('price', 0) for item in clothing_history if item.get('price')]
        avg_price = sum(prices) / len(prices) if prices else 0
        price_range = self._categorize_price_range(avg_price)
        
        return {
            'dominant_styles': sorted(style_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'preferred_colors': sorted(color_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            'preferred_categories': sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            'preferred_brands': sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'average_price': round(avg_price, 2),
            'price_range': price_range,
            'total_items': len(clothing_history)
        }
    
    def _categorize_price_range(self, avg_price: float) -> str:
        """价格范围分类"""
        if avg_price < 100:
            return '经济型'
        elif avg_price < 300:
            return '中等'
        elif avg_price < 1000:
            return '中高端'
        else:
            return '奢侈品'
    
    def _analyze_behavior_patterns(self, behavior_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析行为模式"""
        # 购买频率分析
        purchase_frequency = behavior_data.get('purchase_frequency', 'medium')
        
        # 搭配频率分析
        outfit_frequency = behavior_data.get('outfit_frequency', 'daily')
        
        # 风格探索倾向
        style_exploration = behavior_data.get('style_exploration', 'moderate')
        
        # 品牌忠诚度
        brand_loyalty = behavior_data.get('brand_loyalty', 'moderate')
        
        # 价格敏感度
        price_sensitivity = behavior_data.get('price_sensitivity', 'moderate')
        
        return {
            'purchase_frequency': purchase_frequency,
            'outfit_frequency': outfit_frequency,
            'style_exploration': style_exploration,
            'brand_loyalty': brand_loyalty,
            'price_sensitivity': price_sensitivity,
            'shopping_behavior': self._analyze_shopping_behavior(behavior_data)
        }
    
    def _analyze_shopping_behavior(self, behavior_data: Dict[str, Any]) -> Dict[str, str]:
        """分析购物行为"""
        preferred_channels = behavior_data.get('preferred_channels', ['线上'])
        shopping_timing = behavior_data.get('shopping_timing', '随时')
        decision_factors = behavior_data.get('decision_factors', ['价格', '质量'])
        
        return {
            'preferred_channels': preferred_channels,
            'shopping_timing': shopping_timing,
            'key_decision_factors': decision_factors
        }
    
    def _get_body_type_recommendations(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取体型建议"""
        body_type = user_data.get('body_type', '矩形')
        body_info = self.body_type_mapping.get(body_type, {})
        
        return {
            'suitable_styles': body_info.get('suitable_styles', []),
            'avoid_styles': body_info.get('avoid_styles', []),
            'color_suggestions': body_info.get('color_suggestions', {}),
            'styling_tips': self._generate_styling_tips(body_type)
        }
    
    def _get_color_recommendations(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取色彩建议"""
        skin_tone = user_data.get('skin_tone', '中性色调')
        color_info = self.skin_tone_mapping.get(skin_tone, {})
        
        return {
            'suitable_colors': color_info.get('suitable_colors', []),
            'avoid_colors': color_info.get('avoid_colors', []),
            'makeup_suggestions': color_info.get('makeup_suggestions', []),
            'color_matching_tips': self._generate_color_tips(skin_tone)
        }
    
    def _generate_styling_tips(self, body_type: str) -> List[str]:
        """生成搭配建议"""
        tips_mapping = {
            '梨形': [
                '选择深色下装，浅色上装来平衡比例',
                '利用配饰和细节转移注意力到上半身',
                '选择A字裙来修饰臀部线条'
            ],
            '苹果形': [
                '选择V领和深V领来拉长颈部线条',
                '避免腰部过于紧身的设计',
                '利用垂直线条来拉长身形'
            ],
            '沙漏形': [
                '充分利用您的腰线优势',
                '选择修身剪裁突出身材曲线',
                '可以大胆尝试各种风格'
            ],
            '矩形': [
                '通过层次搭配增加身材曲线',
                '利用腰带和腰部装饰强调腰线',
                '选择有褶皱和细节的单品'
            ],
            '倒三角': [
                '选择宽松下装平衡上半身',
                '避免过多的肩部装饰',
                '利用下半身的亮色来转移视觉重心'
            ]
        }
        
        return tips_mapping.get(body_type, ['选择适合自己的风格最重要'])
    
    def _generate_color_tips(self, skin_tone: str) -> List[str]:
        """生成色彩搭配建议"""
        tips_mapping = {
            '暖色调': [
                '选择暖色系服装能让您看起来更有气色',
                '金色配饰比银色配饰更适合您',
                '避免过于冷调的蓝色和粉色'
            ],
            '冷色调': [
                '冷色系服装能突出您的优雅气质',
                '银色配饰能很好地衬托您的肤色',
                '纯白色比奶油白更适合您'
            ],
            '中性色调': [
                '您可以尝试各种颜色，适应性很强',
                '黑白灰是您的安全色选择',
                '可以根据心情和场合自由选择颜色'
            ]
        }
        
        return tips_mapping.get(skin_tone, ['选择让自己舒适自信的颜色'])
    
    def _generate_personality_insights(self, style_profile: Dict[str, Any], 
                                     behavior_profile: Dict[str, Any]) -> Dict[str, Any]:
        """生成个性洞察"""
        dominant_styles = [item[0] for item in style_profile.get('dominant_styles', [])]
        
        personality_traits = []
        lifestyle_indicators = []
        
        # 基于风格偏好推断个性
        for style in dominant_styles:
            if style in self.style_preferences:
                personality_traits.extend(self.style_preferences[style].get('personality', []))
                lifestyle_indicators.extend(self.style_preferences[style].get('lifestyle', []))
        
        # 去重
        personality_traits = list(set(personality_traits))
        lifestyle_indicators = list(set(lifestyle_indicators))
        
        return {
            'personality_traits': personality_traits[:5],
            'lifestyle_indicators': lifestyle_indicators[:3],
            'style_confidence': self._assess_style_confidence(style_profile),
            'fashion_involvement': self._assess_fashion_involvement(behavior_profile)
        }
    
    def _assess_style_confidence(self, style_profile: Dict[str, Any]) -> str:
        """评估风格自信度"""
        total_items = style_profile.get('total_items', 0)
        dominant_styles = style_profile.get('dominant_styles', [])
        
        if not dominant_styles or total_items < 5:
            return '探索期'
        
        # 计算风格集中度
        top_style_count = dominant_styles[0][1] if dominant_styles else 0
        concentration = top_style_count / total_items if total_items > 0 else 0
        
        if concentration > 0.7:
            return '专一型'
        elif concentration > 0.4:
            return '偏好明确'
        else:
            return '多样化'
    
    def _assess_fashion_involvement(self, behavior_profile: Dict[str, Any]) -> str:
        """评估时尚参与度"""
        style_exploration = behavior_profile.get('style_exploration', 'moderate')
        purchase_frequency = behavior_profile.get('purchase_frequency', 'medium')
        
        if style_exploration == 'high' and purchase_frequency == 'high':
            return '时尚达人'
        elif style_exploration == 'high':
            return '潮流关注者'
        elif purchase_frequency == 'high':
            return '购物爱好者'
        else:
            return '实用主义者'
    
    def _generate_shopping_suggestions(self, style_profile: Dict[str, Any], 
                                     user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成购物建议"""
        suggestions = []
        
        # 基于风格偏好的建议
        dominant_styles = [item[0] for item in style_profile.get('dominant_styles', [])]
        preferred_colors = [item[0] for item in style_profile.get('preferred_colors', [])]
        price_range = style_profile.get('price_range', '中等')
        
        # 基础单品建议
        if '商务正式' in dominant_styles:
            suggestions.append({
                'category': '基础单品',
                'item': '经典白衬衫',
                'reason': '商务风格的必备单品',
                'priority': 'high'
            })
        
        if '休闲舒适' in dominant_styles:
            suggestions.append({
                'category': '基础单品',
                'item': '质量好的基础T恤',
                'reason': '休闲风格的百搭单品',
                'priority': 'high'
            })
        
        # 颜色补充建议
        if '黑色' not in [color for color, _ in style_profile.get('preferred_colors', [])]:
            suggestions.append({
                'category': '颜色补充',
                'item': '黑色基础单品',
                'reason': '增加搭配的灵活性',
                'priority': 'medium'
            })
        
        # 季节性建议
        current_season = self._get_current_season()
        suggestions.append({
            'category': '季节更新',
            'item': f'{current_season}季新品',
            'reason': f'为{current_season}季更新衣橱',
            'priority': 'medium'
        })
        
        return suggestions[:5]
    
    def _get_current_season(self) -> str:
        """获取当前季节"""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return '春'
        elif month in [6, 7, 8]:
            return '夏'
        elif month in [9, 10, 11]:
            return '秋'
        else:
            return '冬'
    
    def _get_default_profile(self) -> Dict[str, Any]:
        """获取默认画像"""
        return {
            'basic_info': {
                'age': 25,
                'age_group': '青年',
                'gender': '女',
                'body_type': '矩形',
                'skin_tone': '中性色调'
            },
            'style_preferences': {
                'dominant_styles': [('休闲', 1)],
                'preferred_colors': [('蓝色', 1)],
                'preferred_categories': [('上装', 1)]
            },
            'behavior_patterns': {
                'purchase_frequency': 'medium',
                'style_exploration': 'moderate'
            },
            'body_recommendations': {
                'suitable_styles': ['基础款式'],
                'avoid_styles': [],
                'styling_tips': ['选择适合自己的风格']
            },
            'color_recommendations': {
                'suitable_colors': ['黑白灰'],
                'color_matching_tips': ['从基础色开始']
            },
            'personality_insights': {
                'personality_traits': ['实用'],
                'style_confidence': '探索期'
            },
            'shopping_suggestions': [],
            'updated_at': datetime.now().isoformat()
        }
    
    def update_user_profile(self, user_id: int, new_data: Dict[str, Any]) -> bool:
        """更新用户画像"""
        try:
            # 这里应该与数据库交互，更新用户画像
            # 由于没有实际的数据库连接，这里只是示例
            print(f"更新用户 {user_id} 的画像数据: {new_data}")
            return True
        except Exception as e:
            print(f"更新用户画像失败: {str(e)}")
            return False