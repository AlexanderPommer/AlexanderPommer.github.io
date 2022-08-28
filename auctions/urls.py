from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<int:listing_id>", views.listing_view, name="listing"),
    path("create", views.create, name="create"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("<int:listing_id>/comment", views.comment, name="comment"),
    path("<int:listing_id>/close", views.close, name="close"),
    path("<int:listing_id>/bid", views.bid, name="bid"),
    path("categories", views.categories, name="categories"),
    path("category/<str:abbreviation>", views.category, name="category")
]
