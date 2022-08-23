from django.urls import path

from . import views

#app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/search", views.search,  name="search"),
    path("wiki/create", views.create, name="create"),
    path("wiki/edit", views.edit, name="edit"),
    path("wiki/random", views.random, name="random"),
    path("wiki/<str:TITLE>", views.entry, name="entry")
]
