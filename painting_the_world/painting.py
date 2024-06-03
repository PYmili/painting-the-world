import os
import time
from typing import Union

from rcon import Client
from .image_pixel_extractor import ImagePixelExtractor
from .blocks import *

Minecraft_RGB_BlOCK_CACHE_DIR = os.path.join(os.getcwd(), "cache")


def vertical(
        height_layers: int,
        base_x: int, base_y: int, base_z: int, 
        block_array: list, 
        runCommand: callable
    ) -> bool:
    """
    垂直方向上结构，沿z轴生成
    :return bool
    """
    # 确保图片的排列与游戏内坐标系一致，可能需要翻转block_array
    block_array_flipped = [row[::-1] for row in block_array]  # 这里翻转数组以修正图片方向

    # 遍历高度层
    for layer in range(height_layers):
        adjusted_base_z = base_z + layer * len(block_array_flipped)  # 沿z轴调整每层的起始坐标
        # 对于每一层，遍历x和z坐标放置方块
        for y_index, row in enumerate(block_array_flipped):  # 使用翻转后的数组
            for x_index, block in enumerate(row):
                # 计算当前方块相对于基点的坐标
                current_x = base_x + x_index
                current_y = base_y + y_index  # y坐标随原图片的行进
                current_z = adjusted_base_z  # z轴位置固定在本层
                # 放置命令
                runCommand(f"setblock {current_x} {current_y} {current_z} {block}")

    return True


class Painting(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if os.path.isdir(Minecraft_RGB_BlOCK_CACHE_DIR) is False:
            try:
                os.makedirs(Minecraft_RGB_BlOCK_CACHE_DIR)
            except Exception as e:
                raise e
            
        self.block_array = []   # 存放当前需要生成方块数据
        self.color_space = 'rbg'
        self.base_x = 0
        self.base_y = 100
        self.base_z = 0
        self.is_save = True
        self.resize_multiple = 8
        self.color_blocks = COLOR_TO_CONCRETE_BLOCK
        self.height_layers = 1
        self.vertical = False

    def GenerateMinecraftRGBBlock(self) -> bool:
        """
        生成Minecraft RGB 方块文件
        :param file_path: str 文件路径
        :return bool
        """
        # 解析rgb并生成数组
        extractor = ImagePixelExtractor(self.file_path)
        rgb_array = extractor.extract_pixel_matrix(self.resize_multiple)
        if not rgb_array.tolist():
            raise Exception("解析图片的RGB错误！")

        # 将rgb转换为Minecraft的方块
        count = 0
        for line in rgb_array.tolist():
            self.block_array.append([])
            for i in line:
                i = tuple(i)
                self.block_array[count].append(
                    BlocksLibrary.get_block_name_by_color(
                        rgb=i,
                        color_blocks=self.color_blocks
                    )
                )
            count += 1
        
        return True

    def open_image_file(self) -> Union[bool, None]:
        """
        打开图片文件
        :param file_path: str 文件路径
        :param is_save: bool 是否保存缓存
        :return Union[bool, None]
        """
        generate_result = self.GenerateMinecraftRGBBlock()
        if not generate_result:
            raise OSError(f"打开文件：{self.file_path}，出现错误！")
        
        return True

    def set(
            self,
            _file_path: str,
            _base_x: int = 0,
            _base_y: int = 100,
            _base_z: int = 0,
            _color_space: str = 'rgb',
            _is_save: bool = True,
            _resize_multiple: int = 8,
            _color_blocks: Union[str, None] = None,
            _vertical: bool = False
    ) -> None:
        """
        设置数据
        :return None
        """
        self.file_path = _file_path
        self.base_x = _base_x
        self.base_y = _base_y
        self.base_z = _base_z
        self.color_space = _color_space
        self.is_save = _is_save
        self.resize_multiple = _resize_multiple
        if _color_blocks == 'wool':
            self.color_blocks = COLOR_TO_WOOL_BLOCK
        self.vertical = _vertical

    def generate(self) -> bool:
        """
        开始生成
        :return bool
        """
        if not self.open_image_file():
            raise Exception(f"读取文件错误！： {self.file_path}")
        
        self.loginfo("创建建筑")

        # 垂直绘画
        if self.vertical is True:
            return vertical(
                self.height_layers,
                self.base_x, self.base_y, self.base_z,
                self.block_array[::-1], self.run  # 传递翻转后的数组
            )

        # 从基点开始，遍历block_array以放置方块
        for y_index, row in enumerate(self.block_array):
            for x_index, block in enumerate(row):
                # 计算当前方块相对于基点的坐标
                current_x = self.base_x + x_index
                current_y = self.base_y
                current_z = self.base_z + y_index
                # 放置命令
                self.run(f"setblock {current_x} {current_y} {current_z} {block}")

        return True
    
    def delete_blocks_event(self) -> Union[str, None]:
        """
        删除方块事件
        :return Union[str, None]
        """
        MAX_BLOCKS_PER_OPERATION = 32768
        
        # 计算总方块数，这里简化处理，实际应用中需要根据self.block_array动态计算
        self.block_count = len(self.block_array) ** 2  # 假设self.block_array是方形区域

        if self.block_count <= MAX_BLOCKS_PER_OPERATION:
            # 如果总数合规，尝试一次性删除
            result = self.run(
                f"fill {self.base_x} {self.base_y} {self.base_z} " + 
                f"{self.base_x + len(self.block_array) - 1} " + 
                f"{self.base_y} {self.base_z + len(self.block_array) - 1} air replace"
            )
        else:
            # 如果超过限制，一个个删除
            for y_index, row in enumerate(self.block_array):
                for x_index, _ in enumerate(row):
                    current_x = self.base_x + x_index
                    current_y = self.base_y
                    current_z = self.base_z + y_index
                    result = self.run(
                        f"setblock {current_x} {current_y} {current_z} air replace"
                    )

        return result
    
    def delete_blocks_vertical(self) -> Union[str, None]:
        """
        删除垂直方向上的方块事件
        :return Union[str, None]
        """
        MAX_BLOCKS_PER_OPERATION = 32768
        total_blocks_per_layer = len(self.block_array) ** 2
        total_layers = self.height_layers
        total_blocks = total_blocks_per_layer * total_layers  # 总方块数

        if total_blocks <= MAX_BLOCKS_PER_OPERATION:
            # 一次性删除所有层的方块
            start_z = self.base_z
            end_z = self.base_z + (total_layers - 1) * len(self.block_array[0])
            result = self.run(
                f"fill {self.base_x} {self.base_y} {start_z} " + 
                f"{self.base_x + len(self.block_array[0]) - 1} " + 
                f"{self.base_y + len(self.block_array) - 1} {end_z} air replace"
            )
        else:
            for layer in range(total_layers):
                adjusted_base_z = self.base_z + layer * len(self.block_array[0])
                for y_index, row in enumerate(self.block_array):
                    for x_index, _ in enumerate(row):
                        current_x = self.base_x + x_index
                        current_y = self.base_y + y_index
                        current_z = adjusted_base_z
                        result = self.run(f"setblock {current_x} {current_y} {current_z} air replace")

        return result
    
    def delete_generated(self) -> bool:
        """
        开始删除之前生成的结构
        :return bool
        """
        if not self.GenerateMinecraftRGBBlock():
            raise Exception(f"加载文件错误！{self.file_path}")

        self.loginfo("删除建筑")

        if self.vertical is True:
            print("返回结果：", self.delete_blocks_vertical())
            return True

        print("返回结果：", self.delete_blocks_event())

        return True
    
    def loginfo(self, msg: str) -> None:
        """
        print info
        :return None
        """
        # 获取图片的宽度（每行方块数）和高度（行数）
        width = len(self.block_array[0]) if self.block_array else 0
        height = len(self.block_array)
        
        color_block = 'concrete'
        if self.color_blocks == COLOR_TO_WOOL_BLOCK:
            color_block = 'wool'

        print(
            f"{msg}:\n\t - 高度: {height}\n\t - 宽度：{width}" +
            f"\n\t - 坐标: {self.base_x}, {self.base_y}, {self.base_z}" + 
            f"\n\t - 缩小: {self.resize_multiple}倍" + 
            f"\n\t - 颜色: {self.color_space}"
            f"\n\t - 方块：{color_block}"
        )
