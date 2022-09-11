from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API Routes
    path("create", views.create, name="create"),
    path("posts/<str:view>/<int:page>", views.posts, name="posts"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("follow", views.follow, name="profile"),
    path("edit/<int:post_id>", views.edit, name="edit"),
    path("like", views.like, name="like")
]
