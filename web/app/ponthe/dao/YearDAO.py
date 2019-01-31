from .ResourceDAO import ResourceDAO
from .. import db
from ..models import Year
from .FileDAO import FileDAO


class YearDAO(ResourceDAO):
    def __init__(self):
        super().__init__(Year)

    def delete_detaching_galleries(self, slug):
        year = self.find_by_slug(slug)
        for gallery in year.galleries:
            gallery.year = None
        db.session.commit()
        db.session.delete(year)
        db.session.commit()


    def serialize(self, slug):
        year = self.find_by_slug(slug)
        file_dao = FileDAO()
        if year.cover_image is not None:
            url_to_image = cover_image.file_path()
        elif year.cover_image_id is not None:
            image_file = file_dao.find_by_id(cover_image_id)
            url_to_image = image_file.file_path()
        else:
            url_to_image = "not specified"
        return  {
                    'year_id': year.id,
                    'cover_image_url': url_to_image,
                    'year_slug': year.value
                }


    @staticmethod
    def find_all_ordered_by_value():
        return Year.query.order_by(-Year.value).all()
