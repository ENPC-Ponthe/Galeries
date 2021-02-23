import os
import json

from .. import app

ASSET_FOLDER = app.config['ASSET_ROOT']
CGU_FILE = "data/cgu.json"


class AssetService:
    @staticmethod
    def get_cgu():
        cgu_path = os.path.join(ASSET_FOLDER, CGU_FILE)
        if not os.path.exists(cgu_path):
            with open(cgu_path, 'w'): pass
        with open(cgu_path) as cgu:
            return json.load(cgu, strict=False)

    @staticmethod
    def edit_cgu(new_cgu):
        cgu_path = os.path.join(ASSET_FOLDER, CGU_FILE)
        with open(cgu_path, "w", encoding='utf-8') as cgu:
            json.dump(new_cgu, cgu, ensure_ascii=False, indent=4)
