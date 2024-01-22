import os
import sys

from .modules.Watermark.add_watermark import AddWatermark

python = sys.executable

# User extension files in custom_nodes
extension_folder = os.path.dirname(os.path.realpath(__file__))

DEBUG = False

def log(*text):
    if DEBUG:
        print(''.join(map(str, text)))


# def installNodes():
#     log(f"\n-------> JK Node Installing [DEBUG] <-------")
# installNodes()

NODE_CLASS_MAPPINGS = {
    "JK_AddWatermark": AddWatermark,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "JK_AddWatermark": "✈️JK Add Watermark",
    # "JK_ImgToImg": "✈️JK Img to Img",
    # "JK_TxtToImg": "✈️JK Txt to Img",
    # # "JK_RmBg": "JK Remove bg",
    # # "JK_RmBgMask": "JK Remove bg mask",
    # "JK_MaskToImg": "✈️JK Mask to Img",
    # "JK_ImageToInt": "✈️JK Image To Int",
    # "JK_SaveImage": "✈️JK Save Image & Upload to OSS",
    # "JK_SaveImageBridge": "✈️JK Save Image & Upload to OSS Bridge",
    # "JK_ImagesToGrid": "✈️JK Images to Grid",
    # 'JK_MediaUpdate': '✈️JK Media Update Node',
}

WEB_DIRECTORY = "js"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

