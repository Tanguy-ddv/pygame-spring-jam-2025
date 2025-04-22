from pygamelib import *
from assets.image_caching import *

Images = image_manager.ImageManager()
Images.load_json("assets/jsons/images.json")
cache_size_variants(Images.get_image("star"), "star", Images, 50)
cache_size_variants(Images.get_image("shooting_star"), "shooting_star", Images, 25)