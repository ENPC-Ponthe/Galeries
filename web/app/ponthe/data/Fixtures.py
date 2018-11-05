from ponthe.models import User, Event, Year, File, Gallery, Category

class Fixtures():
    user_philippe = User(
        gender="M",
        firstname="Philippe",
        lastname="Ferreira De Sousa",
        username="philippe.ferreira-de-sousa",
        origin="Concours Commun",
        department="IMI",
        promotion="019",
        password="password",
        admin=True,
        email_confirmed=True
    )
    user_ponthe = User(
        firstname="Ponthe",
        lastname="ENPC",
        username="ponthe.enpc",
        password="password",
        email="ponthe@liste.enpc.fr",
        admin=False,
        email_confirmed=True
    )

    event_admissibles = Event(
        name="Admissibles",
        author=user_philippe,
        category=Category.query.filter_by(slug="vie-associative").one(),
        description="Retour en enfance !"
    )
    event_coupe_de_l_X = Event(
        name="Coupe de l'X",
        author=user_ponthe,
        category=Category.query.filter_by(slug="sports").one(),
        description="Tournoi sportif majeur de la vie des écoles d'ingénieur ! Et les Ponts ont fait pas mal de perf' !"
    )
    event_random = Event(
        name="Evenement random",
        author=user_philippe,
        category=Category.query.filter_by(slug="sports").one(),
        description="Galeries diverses"
    )

    year_2016 = Year(
        description="Une année riche en victoires !",
        author=user_philippe,
        value=2016
    )
    year_2017= Year(
        description="Une année de folie !",
        author=user_philippe,
        value=2017
    )

    gallery1 = Gallery(
        name="Les admissibles des RasPonts'",
        slug="les-admissibles-des-rasponts",
        year=year_2016,
        event=event_admissibles
    )
    gallery2 = Gallery(
        name="La coupe de l'X 2017 du turfu",
        slug="la-coupe-de-l-x-2017-du-turfu",
        year=year_2017,
        event=event_coupe_de_l_X
    )
    gallery3 = Gallery(
        name="Fillers",
        slug="fillers",
        year=year_2017,
        event=event_random
    )
    gallery4 = Gallery(
        name="Portfolio",
        slug="portfolio",
        year=year_2016,
        event=event_random,
        private=True
    )
    gallery5 = Gallery(
        name="Profiles",
        slug="profiles",
        year=year_2017,
        event=event_random,
        private=True
    )
    gallery6 = Gallery(
        name="Slides",
        slug="slides",
        event=event_random
    )
    gallery7 = Gallery(
        name="Thumbsgallery",
        slug="thumbsgallery",
        year=year_2017,
    )

    file1 = File(
        type="IMAGE",
        name="Hey !",
        author=user_philippe,
        gallery=gallery1,
        filename="jUpIiqdBWQ9VpXVMzgjV.bmp",
        pending=False
    )
    file2 = File(
        type="IMAGE",
        name="Keur",
        author=user_philippe,
        gallery=gallery1,
        filename="t3dn23iQCa4aEDu7nNXB.jpg",
        pending=False
    )
    file3 = File(
        type="IMAGE",
        name="Champions du monde !",
        author=user_philippe,
        gallery=gallery1,
        filename="XbcoWxBD5PPzc941hXVM.jpg",
        pending=True
    )
    file4 = File(
        type="IMAGE",
        name=None,
        author=user_philippe,
        gallery=gallery2,
        filename="EKMRZkewtLHvD01TQXrU.jpg",
        pending=False
    )
    file5 = File(
        type="IMAGE",
        name="Oh !",
        author=user_philippe,
        gallery=gallery2,
        filename="8WsJH3V5D2nY3JxvkEJY.png",
        pending=True
    )
    file6 = File(
        type="IMAGE",
        name="Bouilla !",
        author=user_ponthe,
        gallery=gallery2,
        filename="b4iryeMgCfPsN7Egq8Z9.jpg",
        pending=True
    )
    file7 = File(
        type="IMAGE",
        author=user_philippe,
        gallery=gallery3,
        filename="aboutme.jpg"
    )
    file8 = File(
        type="IMAGE",
        author=user_philippe,
        gallery=gallery3,
        filename="filler1.jpg",
        pending=False
    )
    file9 = File(
        type="IMAGE",
        author=user_philippe,
        gallery=gallery3,
        filename="filler2.jpg",
        pending=False
    )
    file10 = File(
        type="IMAGE",
        author=user_philippe,
        gallery=gallery3,
        filename="filler3.jpg",
        pending=True
    )
    file11 = File(
        type="IMAGE",
        author=user_philippe,
        gallery=gallery3,
        filename="filler4.jpg",
        pending=False
    )
    file12 = File(
        type="IMAGE",
        author=user_philippe,
        gallery=gallery4,
        filename="image7.jpg",
        pending=False
    )
    file13 = File(
        type="IMAGE",
        author=user_philippe,
        gallery=gallery4,
        filename="image8.jpg",
        pending=False
    )
    file14 = File(
        type="IMAGE",
        author=user_philippe,
        gallery=gallery4,
        filename="image10.jpg",
        pending=False
    )
    file15 = File(
        type="IMAGE",
        author=user_philippe,
        gallery=gallery4,
        filename="image12.jpg",
        pending=False
    )
    file16 = File(
        type="IMAGE",
        author=user_philippe,
        gallery=gallery5,
        filename="37.jpg",
        pending=False
    )
    file17 = File(
        type="IMAGE",
        author=user_philippe,
        gallery=gallery5,
        filename="53.jpg",
        pending=False
    )
    file18 = File(
        type="IMAGE",
        author=user_philippe,
        gallery=gallery5,
        filename="78.jpg",
        pending=False
    )
    file19 = File(
        type="IMAGE",
        author=user_philippe,
        gallery=gallery5,
        filename="84.jpg",
        pending=False
    )
    file20 = File(
        type="IMAGE",
        author=user_philippe,
        gallery=gallery5,
        filename="87.jpg",
        pending=False
    )
    file21 = File(
        type="IMAGE",
        author=user_philippe,
        gallery=gallery5,
        filename="99.jpg",
        pending=False
    )
    file22 = File(
        type="IMAGE",
        author=user_ponthe,
        gallery=gallery6,
        filename="slide1.jpg",
        pending=False
    )
    file23 = File(
        type="IMAGE",
        author=user_ponthe,
        gallery=gallery6,
        filename="slide2.jpg",
        pending=False
    )
    file24 = File(
        type="IMAGE",
        author=user_ponthe,
        gallery=gallery6,
        filename="slide3.jpg",
        pending=False
    )
    file25 = File(
        type="IMAGE",
        author=user_ponthe,
        gallery=gallery6,
        filename="slide4.jpg",
        pending=False
    )
    file26 = File(
        type="IMAGE",
        author=user_ponthe,
        gallery=gallery7,
        filename="image01.jpg",
        pending=False
    )
    file27 = File(
        type="IMAGE",
        author=user_ponthe,
        gallery=gallery7,
        filename="image02.jpg",
        pending=False
    )
    file28 = File(
        type="IMAGE",
        author=user_ponthe,
        gallery=gallery7,
        filename="image03.jpg",
        pending=False
    )
    file29 = File(
        type="IMAGE",
        author=user_ponthe,
        gallery=gallery7,
        filename="image04.jpg",
        pending=False
    )
    file30 = File(
        type="IMAGE",
        author=user_ponthe,
        gallery=gallery7,
        filename="image05.jpg",
        pending=True
    )
    file31 = File(
        type="IMAGE",
        author=user_ponthe,
        gallery=gallery7,
        filename="image06.jpg",
        pending=True
    )
    file32 = File(
        type="IMAGE",
        author=user_ponthe,
        gallery=gallery7,
        filename="image07.jpg",
        pending=False
    )
    file33 = File(
        type="IMAGE",
        author=user_ponthe,
        gallery=gallery7,
        filename="image08.jpg",
        pending=False
    )
    file34 = File(
        type="IMAGE",
        author=user_ponthe,
        gallery=gallery7,
        filename="image09.jpg",
        pending=False
    )