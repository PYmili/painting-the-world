from PIL import Image
import numpy as np

class ImagePixelExtractor:
    def __init__(self, image_path):
        """
        初始化方法，加载图片并转换为RGB模式及numpy数组形式。
        
        :param image_path: 图片文件的路径
        """
        self.image_path = image_path

    def _load_and_convert_to_matrix(self, resize_multiple: int):
        """
        加载图片，调整尺寸，并转换为RGB模式的numpy数组。
        
        :return: 转换后的像素矩阵（numpy数组）
        """
        img = Image.open(self.image_path)
        img = img.resize((img.width // resize_multiple, img.height // resize_multiple), resample=Image.LANCZOS)
        # img.show()
        return np.array(img.convert('RGB'))

    def extract_pixel_matrix(self, resize_multiple: int = 8):
        """
        返回图片像素的RGB值矩阵。
        
        :return: 包含每个像素RGB值的numpy数组（矩阵形式）
        """
        return self._load_and_convert_to_matrix(resize_multiple)


if __name__ in "__main__":
    # 使用示例
    extractor = ImagePixelExtractor("test.jpg")
    pixel_matrix = extractor.extract_pixel_matrix()
    print(pixel_matrix.shape)  # 打印矩阵的形状（宽度、高度、通道数）