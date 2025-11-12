import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import json
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import random
from core.services.recommendation.scoring.color_harmony import ColorHarmonyStrategy

class RecommendationEngine:
    """智能推荐引擎
    
    基于多模态知识图谱和协同过滤的服装推荐算法
    """

    # TODO 模块任务（实现层内部）
    # 1. 数据输入解耦：当前直接接收 ORM dict，需要抽象为标准 ItemDTO 输入适配层。
    # 2. 过滤策略细化：_filter_items_by_context 拆为季节/场合/天气独立策略类，支持动态启停。
    # 3. 组合生成优化：_generate_outfit_combinations 增加剪枝（同类多余单品、重复颜色阈值）。
    # 4. 评分体系模块化：_calculate_* 方法统一放入 scoring/ 目录并实现 Strategy 接口。
    # 5. 解释增强：_generate_reasoning 返回结构化对象含 rule_id、evidence、score_piece。
    # 6. 可观测性：为 recommend_outfit 添加统计（生成组合数、平均评分、耗时）写入日志。
    # 7. 冷启动逻辑：当 items < N 或 profile 缺失时，走默认色系 + 通用场合推荐路径。
    # 8. A/B 支持：在评分阶段读取 config.experiment_flags 决定是否启用新策略。
    # 9. 错误降级：任何单一评分策略失败不影响总体（捕获异常返回中性分 0.5）。
    # 10. 单元测试：为颜色/风格/季节评分各写 2 个边界测试（极端颜色、单品、不匹配季节）。
    # 验收标准：模块化重构后主类方法长度显著下降（< 30 行），新增策略可无需改动核心入口。
    
    def __init__(self):
        self.style_rules = self._load_style_rules()
        self.color_harmony = self._load_color_harmony()
        self.occasion_mapping = self._load_occasion_mapping()
        self.season_mapping = self._load_season_mapping()
        # 策略实例（逐步替换内部评分函数）
        self._color_strategy = ColorHarmonyStrategy(self.color_harmony)
        
    def _load_style_rules(self) -> Dict[str, Any]:
        """加载风格搭配规则"""
        return {
            '商务正式': {
                'required_categories': ['上装', '下装', '鞋子'],
                'preferred_styles': ['正式', '商务', '优雅'],
                'colors': ['黑色', '深蓝', '灰色', '白色', '米色'],
                'patterns': ['纯色', '细条纹'],
                'materials': ['羊毛', '丝绸', '棉质', '聚酯纤维']
            },
            '休闲舒适': {
                'required_categories': ['上装', '下装'],
                'preferred_styles': ['休闲', '舒适', '运动'],
                'colors': ['任意'],
                'patterns': ['任意'],
                'materials': ['棉质', '针织', '牛仔布']
            },
            '时尚潮流': {
                'required_categories': ['上装', '下装'],
                'preferred_styles': ['时尚', '潮流', '个性'],
                'colors': ['任意'],
                'patterns': ['任意'],
                'materials': ['任意']
            },
            '甜美可爱': {
                'required_categories': ['上装', '下装'],
                'preferred_styles': ['甜美', '可爱', '少女'],
                'colors': ['粉色', '白色', '浅蓝', '米色', '薄荷绿'],
                'patterns': ['碎花', '波点', '蕾丝'],
                'materials': ['雪纺', '蕾丝', '棉质']
            }
        }
    
    def _load_color_harmony(self) -> Dict[str, List[str]]:
        """加载色彩搭配规则"""
        return {
            '黑色': ['白色', '灰色', '红色', '金色', '银色'],
            '白色': ['黑色', '蓝色', '红色', '粉色', '任意'],
            '灰色': ['白色', '黑色', '粉色', '蓝色', '黄色'],
            '红色': ['白色', '黑色', '米色', '深蓝'],
            '蓝色': ['白色', '米色', '黄色', '红色', '灰色'],
            '粉色': ['白色', '灰色', '米色', '深蓝'],
            '黄色': ['白色', '蓝色', '灰色', '黑色'],
            '绿色': ['白色', '米色', '棕色', '黑色'],
            '紫色': ['白色', '灰色', '黑色', '银色'],
            '棕色': ['米色', '白色', '绿色', '橙色']
        }
    
    def _load_occasion_mapping(self) -> Dict[str, Dict[str, Any]]:
        """加载场合搭配映射"""
        return {
            '工作': {
                'styles': ['商务正式', '优雅知性'],
                'colors': ['深色系为主'],
                'formality': 0.8
            },
            '约会': {
                'styles': ['甜美可爱', '时尚潮流', '优雅知性'],
                'colors': ['任意'],
                'formality': 0.6
            },
            '聚会': {
                'styles': ['时尚潮流', '个性张扬'],
                'colors': ['亮色系'],
                'formality': 0.4
            },
            '运动': {
                'styles': ['运动休闲'],
                'colors': ['任意'],
                'formality': 0.2
            },
            '日常': {
                'styles': ['休闲舒适'],
                'colors': ['任意'],
                'formality': 0.3
            }
        }
    
    def _load_season_mapping(self) -> Dict[str, Dict[str, Any]]:
        """加载季节搭配映射"""
        return {
            '春季': {
                'colors': ['浅色系', '粉色', '绿色', '蓝色'],
                'materials': ['棉质', '针织', '雪纺'],
                'thickness': 'medium'
            },
            '夏季': {
                'colors': ['浅色系', '白色', '蓝色', '黄色'],
                'materials': ['棉质', '雪纺', '丝绸', '亚麻'],
                'thickness': 'thin'
            },
            '秋季': {
                'colors': ['暖色系', '棕色', '橙色', '深红'],
                'materials': ['针织', '羊毛', '牛仔布'],
                'thickness': 'medium'
            },
            '冬季': {
                'colors': ['深色系', '黑色', '灰色', '深蓝'],
                'materials': ['羊毛', '羽绒', '毛呢'],
                'thickness': 'thick'
            }
        }
    
    def recommend_outfit(self, clothing_items: List[Any], user_profile: Any, 
                        occasion: str = '日常', weather: str = '晴天', 
                        season: str = '春季') -> List[Dict[str, Any]]:
        """生成穿搭推荐
        
        Args:
            clothing_items: 用户的服装列表
            user_profile: 用户档案
            occasion: 场合
            weather: 天气
            season: 季节
            
        Returns:
            推荐结果列表
        """
        try:
            # 转换服装数据
            items_data = [item.to_dict() if hasattr(item, 'to_dict') else item for item in clothing_items]
            
            # 根据场合筛选合适的服装
            suitable_items = self._filter_items_by_context(items_data, occasion, season, weather)
            
            # 生成搭配组合
            outfit_combinations = self._generate_outfit_combinations(suitable_items)
            
            # 评分和排序
            scored_outfits = []
            for combination in outfit_combinations:
                score = self._calculate_outfit_score(combination, user_profile, occasion, season)
                reasoning = self._generate_reasoning(combination, occasion, season)
                
                scored_outfits.append({
                    'items': combination,
                    'confidence': score,
                    'reasoning': reasoning,
                    'style_analysis': self._analyze_outfit_style(combination)
                })
            
            # 排序并返回前5个推荐
            scored_outfits.sort(key=lambda x: x['confidence'], reverse=True)
            return scored_outfits[:5]
            
        except Exception as e:
            print(f"推荐生成错误: {str(e)}")
            return []
    
    def _filter_items_by_context(self, items: List[Dict], occasion: str, 
                                season: str, weather: str) -> List[Dict]:
        """根据上下文筛选合适的服装"""
        suitable_items = []
        
        for item in items:
            # 季节适配
            item_season = item.get('season', '通用')
            if item_season not in ['通用', season]:
                continue
            
            # 场合适配
            item_occasion = item.get('occasion', '日常')
            if occasion != '日常' and item_occasion not in ['通用', occasion]:
                continue
                
            # 天气适配（简化处理）
            if weather in ['雨天', '雪天'] and item.get('category') == '鞋子':
                if item.get('material') not in ['防水', '橡胶']:
                    continue
            
            suitable_items.append(item)
        
        return suitable_items
    
    def _generate_outfit_combinations(self, items: List[Dict]) -> List[List[Dict]]:
        """生成搭配组合"""
        # 按类别分组
        categories = {}
        for item in items:
            category = item.get('category', '其他')
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # 生成组合
        combinations = []
        
        # 基本组合：上装 + 下装
        if '上装' in categories and '下装' in categories:
            for top in categories['上装'][:5]:  # 限制数量避免组合爆炸
                for bottom in categories['下装'][:5]:
                    combination = [top, bottom]
                    
                    # 添加鞋子（如果有）
                    if '鞋子' in categories:
                        shoe = random.choice(categories['鞋子'])
                        combination.append(shoe)
                    
                    # 添加配饰（如果有）
                    if '配饰' in categories and random.random() > 0.7:
                        accessory = random.choice(categories['配饰'])
                        combination.append(accessory)
                    
                    combinations.append(combination)
        
        # 连衣裙组合
        if '连衣裙' in categories:
            for dress in categories['连衣裙']:
                combination = [dress]
                
                # 添加鞋子
                if '鞋子' in categories:
                    shoe = random.choice(categories['鞋子'])
                    combination.append(shoe)
                
                combinations.append(combination)
        
        return combinations[:20]  # 限制组合数量
    
    def _calculate_outfit_score(self, combination: List[Dict], user_profile: Any, 
                               occasion: str, season: str) -> float:
        """计算穿搭评分"""
        total_score = 0.0
        weight_sum = 0.0
        
        # 色彩和谐度 (30%)
        color_score = self._calculate_color_harmony(combination)
        total_score += color_score * 0.3
        weight_sum += 0.3
        
        # 风格一致性 (25%)
        style_score = self._calculate_style_consistency(combination)
        total_score += style_score * 0.25
        weight_sum += 0.25
        
        # 场合适配度 (20%)
        occasion_score = self._calculate_occasion_fitness(combination, occasion)
        total_score += occasion_score * 0.2
        weight_sum += 0.2
        
        # 季节适配度 (15%)
        season_score = self._calculate_season_fitness(combination, season)
        total_score += season_score * 0.15
        weight_sum += 0.15
        
        # 个人偏好 (10%)
        if user_profile:
            preference_score = self._calculate_preference_fitness(combination, user_profile)
            total_score += preference_score * 0.1
            weight_sum += 0.1
        
        return total_score / weight_sum if weight_sum > 0 else 0.0
    
    def _calculate_color_harmony(self, combination: List[Dict]) -> float:
        """计算色彩和谐度（已切换到策略实现）"""
        try:
            return self._color_strategy.score(combination, {})
        except Exception:
            return 0.5
    
    def _calculate_style_consistency(self, combination: List[Dict]) -> float:
        """计算风格一致性"""
        styles = [item.get('style', '休闲') for item in combination]
        unique_styles = set(styles)
        
        if len(unique_styles) == 1:
            return 1.0
        elif len(unique_styles) == 2:
            return 0.7
        else:
            return 0.4
    
    def _calculate_occasion_fitness(self, combination: List[Dict], occasion: str) -> float:
        """计算场合适配度"""
        if occasion not in self.occasion_mapping:
            return 0.5
        
        occasion_styles = self.occasion_mapping[occasion]['styles']
        formality = self.occasion_mapping[occasion]['formality']
        
        style_match = 0.0
        for item in combination:
            item_style = item.get('style', '休闲')
            if any(style in item_style for style in occasion_styles):
                style_match += 1.0
            else:
                style_match += 0.3
        
        return style_match / len(combination) if combination else 0.0
    
    def _calculate_season_fitness(self, combination: List[Dict], season: str) -> float:
        """计算季节适配度"""
        if season not in self.season_mapping:
            return 0.5
        
        season_info = self.season_mapping[season]
        fitness_score = 0.0
        
        for item in combination:
            item_season = item.get('season', '通用')
            if item_season in ['通用', season]:
                fitness_score += 1.0
            else:
                fitness_score += 0.3
        
        return fitness_score / len(combination) if combination else 0.0
    
    def _calculate_preference_fitness(self, combination: List[Dict], user_profile: Any) -> float:
        """计算个人偏好适配度"""
        try:
            profile_dict = user_profile.to_dict() if hasattr(user_profile, 'to_dict') else user_profile
            preferred_colors = profile_dict.get('preferred_colors', [])
            preferred_styles = profile_dict.get('preferred_styles', [])
            
            color_match = 0.0
            style_match = 0.0
            
            for item in combination:
                # 颜色偏好匹配
                item_color = item.get('color', '')
                if item_color in preferred_colors:
                    color_match += 1.0
                else:
                    color_match += 0.5
                
                # 风格偏好匹配
                item_style = item.get('style', '')
                if item_style in preferred_styles:
                    style_match += 1.0
                else:
                    style_match += 0.5
            
            total_items = len(combination)
            return (color_match + style_match) / (2 * total_items) if total_items > 0 else 0.5
            
        except Exception:
            return 0.5
    
    def _generate_reasoning(self, combination: List[Dict], occasion: str, season: str) -> str:
        """生成推荐理由"""
        reasons = []
        
        # 分析颜色搭配
        colors = [item.get('color', '未知') for item in combination]
        if len(set(colors)) <= 2:
            reasons.append("色彩搭配简洁和谐")
        
        # 分析风格
        styles = [item.get('style', '休闲') for item in combination]
        if len(set(styles)) == 1:
            reasons.append(f"整体风格统一({styles[0]})")
        
        # 分析场合适配
        if occasion in self.occasion_mapping:
            reasons.append(f"适合{occasion}场合")
        
        # 分析季节适配
        if season in self.season_mapping:
            reasons.append(f"符合{season}季节特点")
        
        return "；".join(reasons) if reasons else "基于您的衣橱进行智能搭配"
    
    def _analyze_outfit_style(self, combination: List[Dict]) -> Dict[str, Any]:
        """分析穿搭风格"""
        styles = [item.get('style', '休闲') for item in combination]
        colors = [item.get('color', '未知') for item in combination]
        categories = [item.get('category', '其他') for item in combination]
        
        return {
            'dominant_style': max(set(styles), key=styles.count),
            'color_palette': list(set(colors)),
            'categories': categories,
            'formality_level': self._estimate_formality(combination)
        }
    
    def _estimate_formality(self, combination: List[Dict]) -> str:
        """估算正式程度"""
        formal_styles = ['正式', '商务', '优雅']
        casual_styles = ['休闲', '运动', '街头']
        
        formal_count = sum(1 for item in combination 
                          if any(style in item.get('style', '') for style in formal_styles))
        casual_count = sum(1 for item in combination 
                          if any(style in item.get('style', '') for style in casual_styles))
        
        if formal_count > casual_count:
            return '正式'
        elif casual_count > formal_count:
            return '休闲'
        else:
            return '半正式'
    
    def analyze_wardrobe_gaps(self, clothing_items: List[Any], user_profile: Any) -> List[Dict[str, Any]]:
        """分析衣橱缺失，提供购买建议"""
        try:
            items_data = [item.to_dict() if hasattr(item, 'to_dict') else item for item in clothing_items]
            
            # 分析现有衣橱
            categories = {}
            colors = {}
            styles = {}
            
            for item in items_data:
                category = item.get('category', '其他')
                color = item.get('color', '未知')
                style = item.get('style', '休闲')
                
                categories[category] = categories.get(category, 0) + 1
                colors[color] = colors.get(color, 0) + 1
                styles[style] = styles.get(style, 0) + 1
            
            suggestions = []
            
            # 基础单品建议
            essential_items = {
                '上装': ['白衬衫', '基础T恤', '针织衫'],
                '下装': ['黑色裤子', '牛仔裤', 'A字裙'],
                '鞋子': ['黑色平底鞋', '运动鞋', '高跟鞋'],
                '外套': ['风衣', '西装外套', '针织开衫']
            }
            
            for category, items in essential_items.items():
                if categories.get(category, 0) < 3:
                    for item in items:
                        suggestions.append({
                            'type': '基础单品',
                            'item': item,
                            'category': category,
                            'reason': f'增加{category}的基础选择',
                            'priority': 'high'
                        })
            
            # 色彩平衡建议
            if colors.get('黑色', 0) == 0:
                suggestions.append({
                    'type': '色彩补充',
                    'item': '黑色基础单品',
                    'category': '任意',
                    'reason': '增加经典黑色单品，提升搭配灵活性',
                    'priority': 'medium'
                })
            
            if colors.get('白色', 0) == 0:
                suggestions.append({
                    'type': '色彩补充',
                    'item': '白色基础单品',
                    'category': '任意',
                    'reason': '白色是万能搭配色，建议添加',
                    'priority': 'medium'
                })
            
            # 风格平衡建议
            if styles.get('正式', 0) == 0 and styles.get('商务', 0) == 0:
                suggestions.append({
                    'type': '风格补充',
                    'item': '正式商务装',
                    'category': '套装',
                    'reason': '增加正式场合的穿搭选择',
                    'priority': 'low'
                })
            
            return suggestions[:10]  # 返回前10个建议
            
        except Exception as e:
            print(f"衣橱分析错误: {str(e)}")
            return []