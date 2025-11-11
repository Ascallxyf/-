import cv2
import numpy as np
from PIL import Image, ImageStat
import json
from typing import Dict, List, Any, Tuple
import requests
from io import BytesIO
import colorsys

class StyleAnalyzer:
    """风格分析器
    
    基于图像处理和色彩分析的服装风格识别
    """
    
    def __init__(self):
        self.color_names = self._init_color_names()
        self.style_keywords = self._init_style_keywords()
        
    def _init_color_names(self) -> Dict[str, Tuple[int, int, int]]:
        """初始化颜色名称映射"""
        return {
            '黑色': (0, 0, 0),
            '白色': (255, 255, 255),
            '灰色': (128, 128, 128),
            '红色': (255, 0, 0),
            '蓝色': (0, 0, 255),
            '绿色': (0, 255, 0),
            '黄色': (255, 255, 0),
            '紫色': (128, 0, 128),
            '粉色': (255, 192, 203),
            '橙色': (255, 165, 0),
            '棕色': (165, 42, 42),
            '米色': (245, 245, 220),
            '深蓝': (0, 0, 139),
            '深绿': (0, 100, 0),
            '深红': (139, 0, 0)
        }
    
    def _init_style_keywords(self) -> Dict[str, List[str]]:
        """初始化风格关键词"""
        return {
            '商务正式': ['正装', '西装', '衬衫', '皮鞋', '领带'],
            '休闲舒适': ['T恤', '牛仔裤', '运动鞋', '卫衣', '休闲裤'],
            '时尚潮流': ['设计师', '时装', '潮牌', '街头', '前卫'],
            '甜美可爱': ['蕾丝', '碎花', '蝴蝶结', '粉色', '公主'],
            '运动活力': ['运动服', '瑜伽裤', '运动鞋', '健身', '跑步'],
            '优雅知性': ['雪纺', '真丝', '珍珠', '优雅', '知性'],
            '复古经典': ['复古', '经典', '怀旧', '古着', '传统'],
            '简约现代': ['简约', '极简', '现代', '线条', '简洁']
        }
    
    def analyze_clothing(self, image_url: str) -> Dict[str, Any]:
        """分析服装图片特征
        
        Args:
            image_url: 图片URL
            
        Returns:
            分析结果字典
        """
        try:
            # 加载图片
            image = self._load_image(image_url)
            if image is None:
                return self._get_default_features()
            
            # 色彩分析
            color_analysis = self._analyze_colors(image)
            
            # 纹理分析
            texture_analysis = self._analyze_texture(image)
            
            # 形状分析
            shape_analysis = self._analyze_shape(image)
            
            # 综合特征
            features = {
                'colors': color_analysis,
                'texture': texture_analysis,
                'shape': shape_analysis,
                'dominant_color': color_analysis.get('dominant_color', '未知'),
                'brightness': self._calculate_brightness(image),
                'contrast': self._calculate_contrast(image),
                'complexity': self._calculate_complexity(image)
            }
            
            return features
            
        except Exception as e:
            print(f"图片分析错误: {str(e)}")
            return self._get_default_features()
    
    def _load_image(self, image_url: str) -> np.ndarray:
        """加载图片"""
        try:
            if image_url.startswith('http'):
                response = requests.get(image_url, timeout=10)
                image = Image.open(BytesIO(response.content))
            else:
                image = Image.open(image_url)
            
            # 转换为RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 转换为numpy数组
            return np.array(image)
            
        except Exception as e:
            print(f"图片加载失败: {str(e)}")
            return None
    
    def _analyze_colors(self, image: np.ndarray) -> Dict[str, Any]:
        """分析图片色彩"""
        try:
            # 降采样以提高处理速度
            small_image = cv2.resize(image, (100, 100))
            
            # 转换为HSV色彩空间
            hsv_image = cv2.cvtColor(small_image, cv2.COLOR_RGB2HSV)
            
            # 获取主要颜色
            pixels = small_image.reshape(-1, 3)
            
            # 使用简单的聚类方法获取主要颜色
            dominant_colors = self._get_dominant_colors(pixels, k=5)
            
            # 映射到颜色名称
            color_names = [self._rgb_to_color_name(color) for color in dominant_colors]
            
            # 计算色彩分布
            color_distribution = self._calculate_color_distribution(hsv_image)
            
            return {
                'dominant_color': color_names[0] if color_names else '未知',
                'color_palette': color_names[:3],
                'color_distribution': color_distribution,
                'saturation': np.mean(hsv_image[:, :, 1]),
                'value': np.mean(hsv_image[:, :, 2])
            }
            
        except Exception:
            return {'dominant_color': '未知', 'color_palette': [], 'color_distribution': {}}
    
    def _get_dominant_colors(self, pixels: np.ndarray, k: int = 5) -> List[Tuple[int, int, int]]:
        """获取主要颜色（简化版K-means）"""
        try:
            # 简化的颜色聚类
            unique_colors, counts = np.unique(pixels.reshape(-1, pixels.shape[-1]), 
                                            axis=0, return_counts=True)
            
            # 按出现频率排序
            sorted_indices = np.argsort(counts)[::-1]
            dominant_colors = unique_colors[sorted_indices[:k]]
            
            return [tuple(color) for color in dominant_colors]
            
        except Exception:
            return [(128, 128, 128)]  # 默认灰色
    
    def _rgb_to_color_name(self, rgb: Tuple[int, int, int]) -> str:
        """RGB转颜色名称"""
        min_distance = float('inf')
        closest_color = '未知'
        
        for color_name, color_rgb in self.color_names.items():
            distance = sum((a - b) ** 2 for a, b in zip(rgb, color_rgb)) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_color = color_name
        
        return closest_color
    
    def _calculate_color_distribution(self, hsv_image: np.ndarray) -> Dict[str, float]:
        """计算色彩分布"""
        try:
            # 色相分布
            hue = hsv_image[:, :, 0]
            
            # 定义色相范围
            color_ranges = {
                '红色': (0, 10),
                '橙色': (10, 25),
                '黄色': (25, 35),
                '绿色': (35, 85),
                '青色': (85, 95),
                '蓝色': (95, 125),
                '紫色': (125, 155),
                '粉色': (155, 180)
            }
            
            distribution = {}
            total_pixels = hue.size
            
            for color_name, (min_hue, max_hue) in color_ranges.items():
                mask = (hue >= min_hue) & (hue <= max_hue)
                percentage = np.sum(mask) / total_pixels * 100
                distribution[color_name] = round(percentage, 2)
            
            return distribution
            
        except Exception:
            return {}
    
    def _analyze_texture(self, image: np.ndarray) -> Dict[str, Any]:
        """分析纹理特征"""
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # 计算梯度
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # 纹理特征
            texture_features = {
                'roughness': np.std(magnitude),
                'directionality': self._calculate_directionality(grad_x, grad_y),
                'uniformity': self._calculate_uniformity(gray),
                'pattern_type': self._identify_pattern(gray)
            }
            
            return texture_features
            
        except Exception:
            return {'roughness': 0, 'directionality': 0, 'uniformity': 0, 'pattern_type': '纯色'}
    
    def _calculate_directionality(self, grad_x: np.ndarray, grad_y: np.ndarray) -> float:
        """计算方向性"""
        try:
            angles = np.arctan2(grad_y, grad_x)
            hist, _ = np.histogram(angles, bins=36, range=(-np.pi, np.pi))
            # 方向性越强，直方图越不均匀
            return np.std(hist)
        except Exception:
            return 0.0
    
    def _calculate_uniformity(self, gray: np.ndarray) -> float:
        """计算均匀性"""
        try:
            hist, _ = np.histogram(gray, bins=256, range=(0, 256))
            normalized_hist = hist / np.sum(hist)
            # 计算均匀性（熵的倒数）
            entropy = -np.sum(normalized_hist * np.log2(normalized_hist + 1e-10))
            return 8.0 - entropy  # 8是最大熵值
        except Exception:
            return 0.0
    
    def _identify_pattern(self, gray: np.ndarray) -> str:
        """识别图案类型"""
        try:
            # 简化的图案识别
            variance = np.var(gray)
            
            if variance < 100:
                return '纯色'
            elif variance < 500:
                return '渐变'
            elif variance < 1000:
                return '细纹理'
            else:
                return '复杂图案'
        except Exception:
            return '纯色'
    
    def _analyze_shape(self, image: np.ndarray) -> Dict[str, Any]:
        """分析形状特征"""
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # 边缘检测
            edges = cv2.Canny(gray, 50, 150)
            
            # 轮廓检测
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            shape_features = {
                'edge_density': np.sum(edges > 0) / edges.size,
                'contour_count': len(contours),
                'shape_complexity': self._calculate_shape_complexity(contours),
                'aspect_ratio': image.shape[1] / image.shape[0]
            }
            
            return shape_features
            
        except Exception:
            return {'edge_density': 0, 'contour_count': 0, 'shape_complexity': 0, 'aspect_ratio': 1.0}
    
    def _calculate_shape_complexity(self, contours: List) -> float:
        """计算形状复杂度"""
        try:
            if not contours:
                return 0.0
            
            complexity = 0.0
            for contour in contours:
                if len(contour) > 10:  # 过滤小轮廓
                    # 计算周长和面积比
                    perimeter = cv2.arcLength(contour, True)
                    area = cv2.contourArea(contour)
                    if area > 0:
                        complexity += perimeter * perimeter / area
            
            return complexity / len(contours)
        except Exception:
            return 0.0
    
    def _calculate_brightness(self, image: np.ndarray) -> float:
        """计算亮度"""
        try:
            return np.mean(image)
        except Exception:
            return 128.0
    
    def _calculate_contrast(self, image: np.ndarray) -> float:
        """计算对比度"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            return np.std(gray)
        except Exception:
            return 0.0
    
    def _calculate_complexity(self, image: np.ndarray) -> float:
        """计算复杂度"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # 使用拉普拉斯算子计算复杂度
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            complexity = np.var(laplacian)
            
            return complexity
        except Exception:
            return 0.0
    
    def _get_default_features(self) -> Dict[str, Any]:
        """获取默认特征"""
        return {
            'colors': {
                'dominant_color': '未知',
                'color_palette': [],
                'color_distribution': {},
                'saturation': 0,
                'value': 0
            },
            'texture': {
                'roughness': 0,
                'directionality': 0,
                'uniformity': 0,
                'pattern_type': '纯色'
            },
            'shape': {
                'edge_density': 0,
                'contour_count': 0,
                'shape_complexity': 0,
                'aspect_ratio': 1.0
            },
            'dominant_color': '未知',
            'brightness': 128,
            'contrast': 0,
            'complexity': 0
        }
    
    def analyze_style(self, image_url: str) -> Dict[str, Any]:
        """分析图片整体风格"""
        try:
            # 获取基础特征
            features = self.analyze_clothing(image_url)
            
            # 风格推断
            style_scores = self._calculate_style_scores(features)
            
            # 生成风格建议
            style_suggestions = self._generate_style_suggestions(features)
            
            return {
                'features': features,
                'style_scores': style_scores,
                'predicted_style': max(style_scores, key=style_scores.get) if style_scores else '休闲',
                'suggestions': style_suggestions,
                'similar_styles': self._find_similar_styles(style_scores)
            }
            
        except Exception as e:
            print(f"风格分析错误: {str(e)}")
            return {
                'features': self._get_default_features(),
                'style_scores': {'休闲': 0.5},
                'predicted_style': '休闲',
                'suggestions': [],
                'similar_styles': []
            }
    
    def _calculate_style_scores(self, features: Dict[str, Any]) -> Dict[str, float]:
        """计算各风格的匹配分数"""
        style_scores = {}
        
        # 基于颜色判断风格
        dominant_color = features.get('dominant_color', '未知')
        brightness = features.get('brightness', 128)
        contrast = features.get('contrast', 0)
        complexity = features.get('complexity', 0)
        
        # 商务正式风格
        if dominant_color in ['黑色', '深蓝', '灰色', '白色']:
            style_scores['商务正式'] = 0.8
        else:
            style_scores['商务正式'] = 0.2
        
        # 休闲舒适风格
        if complexity < 1000 and brightness > 100:
            style_scores['休闲舒适'] = 0.7
        else:
            style_scores['休闲舒适'] = 0.4
        
        # 时尚潮流风格
        if contrast > 50 or complexity > 2000:
            style_scores['时尚潮流'] = 0.8
        else:
            style_scores['时尚潮流'] = 0.3
        
        # 甜美可爱风格
        if dominant_color in ['粉色', '白色', '米色']:
            style_scores['甜美可爱'] = 0.7
        else:
            style_scores['甜美可爱'] = 0.2
        
        # 优雅知性风格
        if brightness > 120 and contrast < 40:
            style_scores['优雅知性'] = 0.6
        else:
            style_scores['优雅知性'] = 0.3
        
        return style_scores
    
    def _generate_style_suggestions(self, features: Dict[str, Any]) -> List[str]:
        """生成风格建议"""
        suggestions = []
        
        brightness = features.get('brightness', 128)
        contrast = features.get('contrast', 0)
        dominant_color = features.get('dominant_color', '未知')
        
        if brightness < 80:
            suggestions.append("可以尝试更亮的颜色来提升整体效果")
        
        if contrast < 20:
            suggestions.append("可以增加对比色来丰富层次感")
        
        if dominant_color == '黑色':
            suggestions.append("黑色很经典，可以搭配亮色配饰来增加活力")
        
        if not suggestions:
            suggestions.append("整体搭配很不错，保持这种风格")
        
        return suggestions
    
    def _find_similar_styles(self, style_scores: Dict[str, float]) -> List[str]:
        """找到相似风格"""
        sorted_styles = sorted(style_scores.items(), key=lambda x: x[1], reverse=True)
        return [style for style, score in sorted_styles[:3] if score > 0.3]
    
    def recommend_style_for_user(self, user_profile: Any) -> Dict[str, Any]:
        """为用户推荐风格"""
        try:
            profile_dict = user_profile.to_dict() if hasattr(user_profile, 'to_dict') else user_profile
            
            # 基于用户特征推荐风格
            age = profile_dict.get('age', 25)
            lifestyle = profile_dict.get('lifestyle', '通勤族')
            work_environment = profile_dict.get('work_environment', '办公室')
            
            style_recommendations = []
            
            # 基于年龄推荐
            if age < 25:
                style_recommendations.extend(['甜美可爱', '时尚潮流', '休闲舒适'])
            elif age < 35:
                style_recommendations.extend(['时尚潮流', '优雅知性', '休闲舒适'])
            else:
                style_recommendations.extend(['优雅知性', '商务正式', '简约现代'])
            
            # 基于工作环境推荐
            if work_environment in ['办公室', '公司']:
                style_recommendations.extend(['商务正式', '优雅知性'])
            elif work_environment in ['创意行业', '自由职业']:
                style_recommendations.extend(['时尚潮流', '个性张扬'])
            
            # 去重并评分
            unique_styles = list(set(style_recommendations))
            style_scores = {style: style_recommendations.count(style) / len(style_recommendations) 
                          for style in unique_styles}
            
            return {
                'recommended_styles': unique_styles[:3],
                'style_scores': style_scores,
                'reasoning': f"基于您的年龄({age}岁)和工作环境({work_environment})推荐"
            }
            
        except Exception as e:
            print(f"用户风格推荐错误: {str(e)}")
            return {
                'recommended_styles': ['休闲舒适', '简约现代'],
                'style_scores': {'休闲舒适': 0.6, '简约现代': 0.4},
                'reasoning': "基于通用偏好推荐"
            }