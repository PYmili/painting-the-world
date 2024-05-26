import os
from typing import Union

from rcon import Client
from .image_pixel_extractor import ImagePixelExtractor
from .blocks import BlocksLibrary

Minecraft_RGB_BlOCK_CACHE_DIR = os.path.join(os.getcwd(), "cache")


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
                self.block_array[count].append(BlocksLibrary.get_block_name_by_color(i))
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
        
        # if self.is_save:
        #     # 创建缓存文件的路径
        #     cache_file = os.path.join(
        #         Minecraft_RGB_BlOCK_CACHE_DIR,
        #         os.path.split(file_path)[-1].split('.')[0]
        #     ) + ".mrgbb"

        #     # 写入文件
        #     with open(cache_file, "w+", encoding="utf-8") as wfp:
        #         wfp.write(generate_result)
        
        return True

    def set(
            self,
            _file_path: str,
            _base_x: int = 0,
            _base_y: int = 100,
            _base_z: int = 0,
            _color_space: str = 'rgb',
            _is_save: bool = True,
            _resize_multiple: int = 8
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

    def generate(self) -> bool:
        """
        开始生成
        :return bool
        """
        open_result = self.open_image_file()
        if not open_result:
            raise Exception(f"读取文件错误！： {self.file_path}")
        
        self.loginfo("创建建筑")
        
        # 从基点开始，遍历block_array以放置方块
        for y_index, row in enumerate(self.block_array):
            for x_index, block in enumerate(row):
                # 计算当前方块相对于基点的坐标
                current_x = self.base_x + x_index
                current_y = self.base_y
                current_z = self.base_z + y_index
                
                # 执行命令放置方块
                self.run(f"setblock {current_x} {current_y} {current_z} {block}")

        return True
    
    def delete_generated(self) -> bool:
        """
        开始删除之前生成的结构
        :return bool
        """
        generatorResult = self.GenerateMinecraftRGBBlock()
        if not generatorResult:
            raise Exception(f"加载文件错误！{self.file_path}")

        self.loginfo("删除建筑：")
        
        # 从基点开始，遍历block_array以移除之前放置的方块
        for y_index, row in enumerate(self.block_array):
            for x_index, _ in enumerate(row):  # 用空气方块替换
                # 计算当前方块相对于基点的坐标
                current_x = self.base_x + x_index
                current_y = self.base_y
                current_z = self.base_z + y_index
                
                # 执行命令移除方块，使用空气方块替换
                self.run(f"setblock {current_x} {current_y} {current_z} air")

        return True
    
    def loginfo(self, msg: str) -> None:
        """
        print info
        :return None
        """
        # 获取图片的宽度（每行方块数）和高度（行数）
        width = len(self.block_array[0]) if self.block_array else 0
        height = len(self.block_array)
        
        print(
            f"{msg}:\n\t - 高度: {height}\n\t - 宽度：{width}" +
            f"\n\t - 坐标: {self.base_x}, {self.base_y}, {self.base_z}" + 
            f"\n\t - 缩小: {self.resize_multiple}倍" + 
            f"\n\t - 颜色: {self.color_space}"
        )
