import os
import json

from .. import app

ASSET_FOLDER = app.config['ASSET_ROOT']

DATA_FOLDER = os.path.join(ASSET_FOLDER, 'data')
CGU_FILE = 'cgu.json'
CGU_PATH = os.path.join(DATA_FOLDER, CGU_FILE)
MEMBERS_FILE = 'members.json'
MEMBERS_PATH = os.path.join(DATA_FOLDER, MEMBERS_FILE)
USEFUL_LINKS_FILE = 'useful-links.json'
USEFUL_LINKS_PATH = os.path.join(DATA_FOLDER, USEFUL_LINKS_FILE)
ADMIN_TUTORIALS_FILE = 'admin-tutorials.json'
ADMIN_TUTORIALS_PATH = os.path.join(DATA_FOLDER, ADMIN_TUTORIALS_FILE)
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)


def load_json(path):
    if not os.path.exists(path):
        with open(path, 'w'):
            pass
    with open(path) as json_file:
        return json.load(json_file, strict=False)


def edit_json(path, content):
    with open(path, 'w', encoding='utf-8') as json_file:
        json.dump(content, json_file, ensure_ascii=False, indent=4)


class AssetService:
    @staticmethod
    def get_cgu():
        return load_json(CGU_PATH)

    @staticmethod
    def edit_cgu(new_cgu):
        edit_json(CGU_PATH, new_cgu)

    @staticmethod
    def get_members():
        return load_json(MEMBERS_PATH)

    @staticmethod
    def edit_members(new_members):
        edit_json(MEMBERS_PATH, new_members)

    @staticmethod
    def get_useful_links():
        return load_json(USEFUL_LINKS_PATH)

    @staticmethod
    def edit_useful_links(new_useful_links):
        edit_json(USEFUL_LINKS_PATH, new_useful_links)

    @staticmethod
    def get_admin_tutorials():
        return load_json(ADMIN_TUTORIALS_PATH)

    @staticmethod
    def edit_admin_tutorials(new_admin_tutorials):
        edit_json(ADMIN_TUTORIALS_PATH, new_admin_tutorials)
