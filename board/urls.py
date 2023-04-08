from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API Routes
    path("new", views.new, name="new"),
    path("match/<int:match_id>", views.load_match, name="match"),
    path("list/<int:page>", views.list_matches, name="list"),
    path("move/<int:match_id>", views.move, name="move")
]