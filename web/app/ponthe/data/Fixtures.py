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

    file1 = File(
        type="IMAGE",
        slug="jUpIiqdBWQ9VpXVMzgjV",
        name="Hey !",
        author=user_philippe,
        gallery=gallery1,
        filename="jUpIiqdBWQ9VpXVMzgjV.bmp",
        pending=False
    )
    file2 = File(
        type="IMAGE",
        slug="t3dn23iQCa4aEDu7nNXB",
        name="Keur",
        author=user_philippe,
        gallery=gallery1,
        filename="t3dn23iQCa4aEDu7nNXB.jpg",
        pending=False
    )
    file3 = File(
        type="IMAGE",
        slug="XbcoWxBD5PPzc941hXVM",
        name="Champions du monde !",
        author=user_philippe,
        gallery=gallery1,
        filename="XbcoWxBD5PPzc941hXVM.jpg",
        pending=True
    )
    file4 = File(
        type="IMAGE",
        slug="EKMRZkewtLHvD01TQXrU",
        name=None,
        author=user_philippe,
        gallery=gallery2,
        filename="EKMRZkewtLHvD01TQXrU.jpg",
        pending=False
    )
    file5 = File(
        type="IMAGE",
        slug="8WsJH3V5D2nY3JxvkEJY",
        name="Oh !",
        author=user_philippe,
        gallery=gallery2,
        filename="8WsJH3V5D2nY3JxvkEJY.png",
        pending=True
    )
    file6 = File(
        type="IMAGE",
        slug="b4iryeMgCfPsN7Egq8Z9",
        name="Bouilla !",
        author=user_ponthe,
        gallery=gallery2,
        filename="b4iryeMgCfPsN7Egq8Z9.jpg",
        pending=True
    )
