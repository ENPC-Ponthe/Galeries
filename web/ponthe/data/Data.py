# coding=utf-8
from ponthe.models import Category, File, Gallery
from .. import db
class Data():
    category_gallery = Gallery(
        name="Photos de couverture des catégories",
        slug="photos-de-couverture-des-categories",
        private=True
    )
    sports_cover_image = File(
        type="IMAGE",
        name="Sports Cover",
        filename="sports-cover.jpg",
        gallery=category_gallery,
        pending=False
    )
    vie_associative_cover_image = File(
        type="IMAGE",
        name="Vie associative Cover",
        filename="vie-associative-cover.jpg",
        gallery=category_gallery,
        pending=False
    )
    films_cover_image = File(
        type="IMAGE",
        name="Films Cover",
        filename="films-cover.jpg",
        gallery=category_gallery,
        pending=False
    )
    voyages_cover_image = File(
        type="IMAGE",
        name="Voyages Cover",
        filename="voyages-cover.jpg",
        gallery=category_gallery,
        pending=False
    )

    category_sports = Category(
        name="Sports",
        description="Tout sur la vie sportive : tournois, show pom pom, évènements...",
        cover_image=sports_cover_image
    )
    category_vie_associative = Category(
        name="Vie associative",
        description="La meilleure vie associative de l'Est parisien !",
        cover_image=vie_associative_cover_image
    )
    category_films = Category(
        name="Films",
        description="Réalisations du club : films admissibles, de voyage, de tournois, de campagnes and more",
        cover_image=films_cover_image
    )
    category_voyages = Category(
        name="Voyages",
        description="Les Ponts autour du monde",
        cover_image=voyages_cover_image
    )

    template_gallery = Gallery(
        name="Photos du template",
        slug="photos-du-template",
        private=True
    )

    default_image = File(
        type="IMAGE",
        name="Default image",
        filename="default-image.jpg",
        gallery=template_gallery,
        pending=False
    )
    elements = [default_image, template_gallery, category_voyages, category_films, category_vie_associative, category_sports, voyages_cover_image, films_cover_image, vie_associative_cover_image, sports_cover_image, category_gallery]
    for element in elements:
        db.session.add(element)
        db.session.commit()
