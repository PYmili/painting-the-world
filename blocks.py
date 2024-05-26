from typing import Tuple, Union, Dict
from collections import namedtuple

# 定义颜色和块名的映射
BlockColor = namedtuple("BlockColor", ["name", "rgb"])
COLOR_TO_BLOCK: Dict[Tuple[int, int, int], str] = {
    # 羊毛块
    (0, 0, 0): "black_wool",                # 黑色羊毛
    (255, 255, 255): "white_wool",          # 白色羊毛
    (255, 0, 0): "red_wool",                # 红色羊毛
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
    (144, 238, 144): "lime_wool",           # 亮绿色羊毛
    (210, 105, 30): "brown_wool",           # 巧克力色羊毛
    (105, 105, 105): "gray_wool",           # 暗灰色羊毛
    (245, 245, 245): "white_wool",          # 烟白色羊毛
    (72, 61, 139): "purple_wool",           # 暗紫色羊毛
    (255, 20, 147): "pink_wool",            # 深粉红羊毛
}

# 用于存储颜色和块名的映射列表
BLOCK_COLORS = [BlockColor(name, rgb) for rgb, name in COLOR_TO_BLOCK.items()]

class BlocksLibrary:
    """
    将RGB颜色映射到Minecraft块名称。
    """

    @staticmethod
    def get_block_name_by_color(rgb: Tuple[int, int, int] = (0, 0, 0)) -> Union[str, None]:
        """
        给定一个RGB元组，返回相应的Minecraft块名。
        如果没有精确匹配，返回最接近的颜色的块名。
        :param rgb: RGB颜色元组
        :return: 对应的Minecraft块名或最近似的块名
        """
        # 首先尝试精确匹配
        if rgb in COLOR_TO_BLOCK:
            return COLOR_TO_BLOCK[rgb]
        
        # 如果没有精确匹配，找到最接近的颜色
        closest_block = min(BLOCK_COLORS, key=lambda block: BlocksLibrary.color_distance(rgb, block.rgb))
        return closest_block.name

    @staticmethod
    def color_distance(c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> float:
        """
        计算两个RGB颜色之间的欧氏距离
        :param c1: 第一个RGB颜色元组
        :param c2: 第二个RGB颜色元组
        :return: 颜色之间的距离
        """
        return ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2) ** 0.5