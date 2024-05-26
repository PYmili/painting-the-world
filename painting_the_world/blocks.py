from typing import Tuple, Union, Any
from collections import namedtuple
from scipy.spatial import cKDTree
from skimage import color as skimageColor
import numpy as np

# 定义颜色和块名的映射
BlockColor = namedtuple("BlockColor", ["name", "rgb"])
COLOR_TO_BLOCK = {
    # 羊毛块
    (0, 0, 0): "black_wool",                # 黑色羊毛
    (255, 255, 255): "white_wool",          # 白色羊毛
    (255, 0, 0): "red_wool",                # 红色羊毛
    (255, 0, 255): "magenta_wool",          # 品红色羊毛
    (0, 255, 0): "lime_wool",               # 绿色羊毛
    (0, 0, 255): "blue_wool",               # 蓝色羊毛
    (255, 165, 0): "orange_wool",           # 橙色羊毛
    (255, 192, 203): "pink_wool",           # 粉色羊毛
    (128, 0, 128): "purple_wool",           # 紫色羊毛
    (165, 42, 42): "brown_wool",            # 棕色羊毛
    (128, 128, 128): "gray_wool",           # 灰色羊毛
    (192, 192, 192): "light_gray_wool",     # 浅灰色羊毛
    (0, 255, 255): "cyan_wool",             # 青色羊毛
    (255, 255, 0): "yellow_wool",           # 黄色羊毛
    (173, 216, 230): "light_blue_wool",     # 浅蓝色羊毛
}


class rgbToSpace:
    @staticmethod
    def to(rgb: Tuple[int, int, int], to_func: Any) -> Tuple[float, float, float]:
        """
        Convert RGB to another color space.
        :param rgb: Tuple[int, int, int], RGB values
        :param to_func: Function to convert RGB to the target color space
        :return: Tuple[float, float, float]
        """
        rgb = np.array(rgb, dtype=np.uint8).reshape((1, 1, 3))
        space = to_func(rgb / 255.0)
        return tuple(space[0, 0])

# 构建KD树
RGB_COLORS = list(COLOR_TO_BLOCK.keys())

class BlocksLibrary:
    """
    将RGB颜色映射到Minecraft块名称。
    """

    @staticmethod
    def get_block_name_by_color(rgb: Tuple[int, int, int] = (0, 0, 0), color_space: str = 'rgb') -> Union[str, None]:
        """
        给定一个RGB元组，返回相应的Minecraft块名。
        如果没有精确匹配，返回最接近的颜色的块名。
        :param rgb: RGB颜色元组
        :param color_space: 颜色空间，可以是'rgb'、'lab'、'hsv'、'yuv'、'yiq'或'ycbcr'
        :return: 对应的Minecraft块名或最近似的块名
        """
        toSpaceFunc = None
        if color_space == 'lab':
            toSpaceFunc = skimageColor.rgb2lab
        elif color_space == 'hsv':
            toSpaceFunc = skimageColor.rgb2hsv
        elif color_space == 'yuv':
            toSpaceFunc = skimageColor.rgb2yuv
        elif color_space == 'yiq':
            toSpaceFunc = skimageColor.rgb2yiq
        elif color_space == 'ycbcr':
            toSpaceFunc = skimageColor.rgb2ycbcr

        if toSpaceFunc is None:
            color_tree = cKDTree(RGB_COLORS)
            rgb_space = rgb
        else:
            transformed_colors = [rgbToSpace.to(rcolor, toSpaceFunc) for rcolor in RGB_COLORS]
            color_tree = cKDTree(transformed_colors)
            rgb_space = rgbToSpace.to(rgb, toSpaceFunc)

        _, idx = color_tree.query(rgb_space)
        closest_rgb = RGB_COLORS[idx]
        return COLOR_TO_BLOCK.get(closest_rgb)

