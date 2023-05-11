# Mara Huldra 2023
# SPDX-License-Identifier: MIT
from itertools import product

import numpy as np
from PIL import Image
import torch

MAX_RESOLUTION = 1024


def k_centroid_downscale(images, width, height, centroids=2):
    '''k-centroid scaling, based on: https://github.com/Astropulse/stable-diffusion-aseprite/blob/main/scripts/image_server.py.'''

    downscaled = np.zeros((images.shape[0], height, width, 3), dtype=np.uint8)

    for ii, image in enumerate(images):
        i = 255. * image.cpu().numpy()
        image = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        factor = (image.width // width, image.height // height)

        for x, y in product(range(width), range(height)):
            tile = image.crop((x * factor[0], y * factor[1], (x + 1) * factor[0], (y + 1) * factor[1]))
            # quantize tile to fixed number of colors (creates palettized image)
            tile = tile.quantize(colors=centroids, method=1, kmeans=centroids)
            # get most common (median) color
            color_counts = tile.getcolors()
            most_common_idx = max(color_counts, key=lambda x: x[0])[1]
            downscaled[ii, y, x, :] = tile.getpalette()[most_common_idx*3:(most_common_idx + 1)*3]

    downscaled = downscaled.astype(np.float32) / 255.0
    return torch.from_numpy(downscaled)


class ImageKCentroidDownscale:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "width": ("INT", {"default": 64, "min": 1, "max": MAX_RESOLUTION, "step": 1}),
                "height": ("INT", {"default": 64, "min": 1, "max": MAX_RESOLUTION, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "downscale"

    CATEGORY = "image/downscaling"

    def downscale(self, image, width, height):
        s = k_centroid_downscale(image, width, height)
        return (s,)


NODE_CLASS_MAPPINGS = {
    "ImageKCentroidDownscale": ImageKCentroidDownscale,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageKCentroidDownscale": "K-Centroid Downscale"
}
