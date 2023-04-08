from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator

from .models import User, Match

from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

def index(request):
    return render(request, "board/index.html")

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
            return render(request, "board/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "board/login.html")

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
            return render(request, "board/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "board/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "board/register.html")

@csrf_exempt
@login_required(login_url='login')
def new(request):
    """Create a new match"""
    
    # Creating a new post must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Get post's body
    data = json.loads(request.body)
    board_str = data.get("board_str") # Unnecessary

    # Create a match
    new_match = Match(
        white_player = request.user, 
        black_player = request.user, # TODO matchmaking with other users websockets
        board = "RNBQKBNRPPPPPPPP                                pppppppprnbqkbnr",
        w_turn = True,
        winner = None
    )
    
    new_match.save()
    
    return JsonResponse(new_match.serialize(), status=201)

@csrf_exempt
@login_required(login_url='login')
def load_match(request, match_id):

    try:

        game = Match.objects.get(id = match_id)
        if request.user == game.black_player or request.user == game.white_player:
            return JsonResponse(game.serialize())
    
    except:

        return JsonResponse({"error": "Invalid match."}, status=400)

@csrf_exempt
@login_required(login_url='login')
def list_matches(request, page):
    try:
        player = User.objects.get(username=request.user)

        wMatches = Match.objects.filter(white_player=player)
        bMatches = Match.objects.filter(black_player=player)
        list_my_games = [x for x in wMatches]
        list_my_games.extend([x for x in bMatches if x not in wMatches])
        
        list_my_games = Paginator(list_my_games, 10).page(page)
        d = [match.serialize() for match in list_my_games]
        d.append({"prev": list_my_games.has_previous()})
        d.append({"next": list_my_games.has_next()})

        return JsonResponse(d, safe=False)
    except:
        return  JsonResponse({"error": "Invalid match list."}, status=400)

@csrf_exempt
@login_required(login_url='login')
def move(request, match_id):

    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)
    
    data = json.loads(request.body)
    board_str = data.get("board_str")
    en_passant = data.get("en_passant")
    w_turn = data.get("w_turn")
    w_castle = data.get("w_castle")
    b_castle = data.get("b_castle")
    wk_check = data.get("wk_check")
    bk_check = data.get("bk_check")
    winner = data.get("winner")

    match = Match.objects.get(id=match_id)
    match.board = board_str
    match.en_passant = en_passant
    match.w_turn = w_turn
    match.w_castle = w_castle
    match.b_castle = b_castle
    match.wk_check = wk_check
    match.bk_check = bk_check
    match.winner = winner
    match.save()

    return HttpResponse(status=204)