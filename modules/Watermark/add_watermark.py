########################
## 给你的图片加上文字水印 ##
########################
from matplotlib import font_manager
import os
from fontTools.ttLib import TTFont
from PIL import ImageDraw, ImageFont
import torchvision.transforms.functional as F

class ColorMap:
    def __init__(self):
        self.data = {}

    def add_mapping(self, key, value):
        self.data[key] = value

    def get_value(self, key):
        return self.data.get(key, None)

# 示例用法
color_map = ColorMap()

# 添加映射
color_map.add_mapping("白", (255, 255, 255))
color_map.add_mapping("黑", (0, 0, 0))
color_map.add_mapping("红", (255, 0, 0))
color_map.add_mapping("绿", (0, 255, 0))
color_map.add_mapping("蓝", (0, 0, 255))
color_map.add_mapping("黄", (255, 255, 0))

color_names = list(color_map.data.keys())
print(f'color_names: {color_names}')

class FontUtils:

    @staticmethod
    def __get_font_name(font_path):
        try:
            # 尝试以字体集合的方式打开字体文件
            try:
                font_collection = TTFont(font_path, fontNumber=0)
                fonts_in_collection = font_collection.reader.numFonts
            except AttributeError:
                # 如果不是字体集合，则按单个字体处理
                fonts_in_collection = 1

            for font_index in range(fonts_in_collection):
                font = TTFont(font_path, fontNumber=font_index)
                for record in font['name'].names:
                    if record.nameID == 1 and record.platformID == 3:  # Windows Unicode
                        name = record.string.decode('utf-16-be').strip()
                        if name:
                            return name
                    elif record.nameID == 1 and record.platformID == 1:  # Macintosh Roman
                        name = record.string.decode('mac-roman').strip()
                        if name:
                            return name
        except Exception as e:
            print(f"Error processing {font_path}: {e}")
            return None

    @staticmethod
    def __to_specified_font_name(font_name):
        if font_name == 'Microsoft YaHei':
            return '微软雅黑'
        return font_name

    @staticmethod
    def __is_chinese_font(font_path):
        try:
            # 尝试用字体渲染一个常见的中文字符
            font = ImageFont.truetype(font_path, 12)
            bbox = font.getbbox("汉")  # 使用 getbbox 替代 getsize
            return bbox is not None and (bbox[2] - bbox[0]) > 0 and (bbox[3] - bbox[1]) > 0
        except IOError:
            return False

    @staticmethod
    def list_fonts():
        font_files = font_manager.findSystemFonts()
        font_dict = {}

        for font_file in font_files:
            font_name = os.path.basename(font_file).split('.')[0]

            is_chinese = FontUtils.__is_chinese_font(font_file)

            if is_chinese:
                chinese_font_name = FontUtils.__get_font_name(font_file)
                if chinese_font_name:
                    is_chinese = True
                else:
                    is_chinese = False

            if is_chinese:
                font_dict[FontUtils.__to_specified_font_name(chinese_font_name)] = font_file
            else:
                font_dict[font_name] = font_file

        return font_dict

fonts = FontUtils.list_fonts()

class AddWatermark:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        inputs = {
            "required":
                {
                    "images": ("IMAGE", ),
                    # "enable": ("BOOLEAN", {"default": True, "label_on": "True", "label_off": "False"}),
                    "text": (
                        "STRING", {"default": "瑆皓科技"}
                    ),
                    # TODO: 增加自定义位置
                    "position": (["center", "left-top", "left-bottom", "right-top", "right-bottom"], {"default": "center"}),
                    "save_dir_path": (
                        "STRING", {"default": "E:/"}
                    ),
                    "filename_prefix": (
                        "STRING", {"default": "gen-images"}
                    ),
                    "font": (
                        list(fonts.keys()), {"default": "微软雅黑"}
                    ),
                    "font_size": ("INT", {"default": 12, "min": 12, "max": 60}),
                    "text_color": (color_names, {"default": color_names[0]}),
                },
            "optional": {
                "letter_spacing": (
                    "INT", {"default": 2}
                ),
                "direction": (
                    ["horizontal", "vertical"], {"default": "horizontal"}
                ),
            }
        }

        return inputs

    RETURN_TYPES = ("IMAGE", )
    FUNCTION = "add_watermark"

    # OUTPUT_NODE = True
    CATEGORY = "JK Nodes/addWatermark"

    # TODO: 后续支持字符之间的间距以及垂直排列
    def add_watermark(self, images, text, position, save_dir_path, filename_prefix, font, font_size, text_color, letter_spacing, direction):

        # 打开原始图片
        print('start add watermark')

        # 打开原图
        original_images = images

        idx = 0
        font_path = fonts[font]

        result_images = []

        for tensor_image in original_images:
            print(type(tensor_image))
            print(tensor_image.shape)
            original_image = tensor_image.permute(2, 0, 1)

            # Convert torch.Tensor to PIL Image
            pil_image = F.to_pil_image(original_image)

            pil_image = pil_image.convert("RGB")
            draw = ImageDraw.Draw(pil_image)

            # 设置字体
            font = ImageFont.truetype(font_path, font_size)

            # 获取图片大小
            _, image_height, image_width = original_image.shape

            left, top = calc_position(position, image_width, image_height, text, font_size)

            color = color_map.get_value(text_color)

            print(f"""
            image_width: {image_width}
            image_height: {image_height}
            position: {position}
            direction: {direction}
            text: {text}
            font: {font}
            font_size: {font_size}
            color: {color}
            """)

            if direction == "vertical":  # 竖直排列文字
                x = left
                y = top
                for char in text:
                    char_bbox = font.getbbox(char)
                    draw.text((x, y), char, font=font, fill=color)
                    y += char_bbox[3] + letter_spacing
            elif direction == "horizontal":  # 水平排列文字
                x = left
                y = top
                for char in text:
                    char_bbox = font.getbbox(char)
                    draw.text((x, y), char, font=font, fill=color)
                    x += char_bbox[2] + letter_spacing
            else:
                raise Exception(f'Unknown direction: {direction}')

            # Convert PIL Image back to torch.Tensor
            tensor_with_watermark = F.to_tensor(pil_image).permute(1, 2, 0)
            result_images.append(tensor_with_watermark)

            # 保存带水印的图片
            pil_image.save(f'{save_dir_path}/{filename_prefix}-{idx}.png')
            idx += 1

        return (images,)

def calc_position(position, image_width, image_height, text, font_size):
    length = len(text)

    left = 20
    right = 20
    top = 20
    bottom = 20

    if position == "center":
        return (image_width - length * font_size) / 2, (image_height) / 2
    elif position == "left-top":
        return left, top
    elif position == "left-bottom":
        return left, image_height - font_size - bottom
    elif position == "right-top":
        return image_width - length * font_size - right, top
    elif position == "right-bottom":
        return image_width - length * font_size - right, image_height - font_size - bottom
    else:
        raise Exception(f'Unknown position: {position}')