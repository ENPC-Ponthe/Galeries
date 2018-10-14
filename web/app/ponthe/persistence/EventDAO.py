from ..models import Event, File


class EventDAO:
    @staticmethod
    def find_by_year(year):
        Event.query.filter(File.query.filter_by(year=year, event_id=Event.id).exists()).all()