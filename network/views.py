from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator

from .models import User, Post

from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return render(request, "network/index.html")

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@csrf_exempt
@login_required(login_url='login')
def create(request):

    # Creating a new post must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Get post's body
    data = json.loads(request.body)
    body = data.get("body", "")

    # Create a post
    new_post = Post(
        poster=request.user, 
        body=body
    )

    # TODO, May be missing likes field
    new_post.save()
    
    return JsonResponse({"message": "New post created successfully."}, status=201)


def posts(request, view, page):

    # Depending on view request
    try:

        # Get profile's posts
        profile = User.objects.get(username=view)
        posts = Post.objects.filter(poster=profile)
    except User.DoesNotExist:
        
        # Get all posts
        if view == "all posts":
            posts = Post.objects.all()
        
        # Get posts from followed users
        elif view == "following":
            if request.user.is_authenticated:
                
                # TODO
                following = request.user.get_following()
                posts = Post.objects.filter(poster__in=following)
            
            else:
                return HttpResponseRedirect(reverse("login"))
        else:
            return JsonResponse({"error": "Invalid view."}, status=400)
        
        # Bug: this will cause collisions if any usernames == "all posts" or "following"
        # TODO model validator that prevents such collisions
    
    # Paginaton - returns a json with at most 10 posts + prev and next booleans that indicate if such pages exist
    posts = Paginator(posts, 10).page(page)

    d = [post.serialize() for post in posts]
    d.append({"prev": posts.has_previous()})
    d.append({"next": posts.has_next()})

    return JsonResponse(d, safe=False)


def profile(request, username):

    try:
        # Get profile data
        profile = User.objects.get(username=username)
        d = profile.serialize()
        try:
            if request.user in profile.get_followers():
                d["followed"] = "True"
            elif request.user.is_authenticated:
                d["followed"] = "False"
        except:
            pass
        return JsonResponse([d], safe=False)

    except:
        return JsonResponse({"error": "Profile does not exist."}, status=400)


@csrf_exempt
@login_required(login_url='login')
def follow(request):

    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)

    data = json.loads(request.body)
    username = data.get("username")

    try:
        usr = User.objects.get(username=username)
    except:
        return JsonResponse({"error": "Profile does not exist."}, status=400)
    
    d = usr.serialize()
    if request.user in usr.get_followers():
        usr.followers.remove(request.user)
    else:
        usr.add_follower(request.user)
    
    usr.save()
    return JsonResponse([d], safe=False)

@csrf_exempt
@login_required(login_url='login')
def edit(request, post_id):

    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)

    data = json.loads(request.body)
    body = data.get("body")
    
    post = Post.objects.get(id=post_id)
    post.body = body
    post.save()

    return HttpResponse(status=204)

@csrf_exempt
@login_required(login_url='login')   
def like(request):

    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)
    
    data = json.loads(request.body)
    post_id = data.get("post_id")

    post = Post.objects.get(id=post_id)

    if request.user in post.likes.all():
        post.likes.remove(request.user.id)
    else:
        post.likes.add(request.user.id)
 
    post.save()

    return JsonResponse(post.serialize())