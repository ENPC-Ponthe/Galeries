import os

from ..models import User, Gallery
from ..file_helper import delete_folder
from .FileService import FileService
from ..dao import GalleryDAO, YearDAO, EventDAO, FileDAO
from .. import app, db

UPLOAD_FOLDER = app.config['MEDIA_ROOT']
THUMB_FOLDER = app.config['THUMBNAIL_MEDIA_THUMBNAIL_ROOT']


class GalleryService:
    @staticmethod
    def delete(gallery_slug: str):
        gallery = GalleryDAO().find_by_slug(gallery_slug)
        for file in gallery.files:
            FileDAO.delete(file)
        db.session.delete(gallery)
        db.session.commit()
        gallery_path = os.path.join(UPLOAD_FOLDER, gallery_slug)
        thumb_path = os.path.join(THUMB_FOLDER, gallery_slug)
        delete_folder(gallery_path)
        delete_folder(thumb_path)

    @staticmethod
    def make_private(slug):
        gallery = GalleryDAO().find_by_slug(slug)
        if GalleryDAO.has_right_on(gallery):
            gallery.private = True
            db.session.add(gallery)
            db.session.commit()

    @staticmethod
    def make_public(slug):
        gallery = GalleryDAO().find_by_slug(slug)
        if GalleryDAO.has_right_on(gallery):
            gallery.private = False
            db.session.add(gallery)
            db.session.commit()

    @staticmethod
    def create(name: str, author: User, description: str, private: bool, year_slug: str, event_slug: str):
        gallery = Gallery(name=name, author=author)
        if year_slug:
            year = YearDAO().find_by_slug(slug=year_slug)
            gallery.year = year
        if event_slug:
            event = EventDAO().find_by_slug(event_slug)
            gallery.event = event
        if description:
            gallery.description = description
        if private:
            gallery.private = True

        db.session.add(gallery)
        db.session.commit()

    @staticmethod
    def get_galleries_by_year():
        galleries_by_year = {
            year: {
                'public': GalleryDAO.find_public_by_year(year),
                'private': GalleryDAO.find_private_by_year(year),
            } for year in YearDAO.find_all_ordered_by_value()
        }
        for year, galleries in list(galleries_by_year.items()):
            if not galleries['public'] and not galleries['private']:
                del galleries_by_year[year]

        return galleries_by_year

    @staticmethod
    def get_own_pending_and_approved_files_by_gallery(author: User):
        pending_files_by_gallery = {}
        confirmed_files_by_gallery = {}
        for gallery in GalleryDAO().find_all():
            for file in gallery.files:
                if file.author != author:
                    continue
                if file.pending:
                    if gallery not in pending_files_by_gallery:
                        pending_files_by_gallery[gallery] = []
                    pending_files_by_gallery[gallery].append(file)
                else:
                    if gallery not in confirmed_files_by_gallery:
                        confirmed_files_by_gallery[gallery] = []
                    confirmed_files_by_gallery[gallery].append(file)

        return pending_files_by_gallery, confirmed_files_by_gallery

    @staticmethod
    def get_pending_files_by_gallery():
        pending_files_by_gallery = {}
        for pending_gallery in filter(lambda gallery: gallery.is_pending, GalleryDAO().find_all()):
            pending_files_by_gallery[pending_gallery] = [file for file in pending_gallery.files if file.pending]

        return pending_files_by_gallery

    @staticmethod
    def approve(gallery_slug):
        gallery = GalleryDAO().find_by_slug(gallery_slug)
        for file in gallery.files:
            FileService.approve(file)
