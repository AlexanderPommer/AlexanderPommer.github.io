from email.policy import default
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseBadRequest, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import Listing, User, Comment, Bid

class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, label="Comment")

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
    })


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def listing_view(request, listing_id):
    try:
        listing = Listing.objects.get(id=listing_id)
    except Listing.DoesNotExist:
        raise Http404("Listing not found.")
    is_creator = request.user == listing.user
    is_winner = False
    in_watchlist = False
    try:
        in_watchlist = listing in Listing.objects.all().filter(watchers=request.user)
    except:
        pass
    try:
        is_winner = request.user == Bid.objects.get(listing=listing_id).user
    except:
        pass
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "is_creator": is_creator,
        "comments": listing.comments.all(),
        "comment_form": CommentForm(),
        "is_winner": is_winner,
        "in_watchlist": in_watchlist
    })

class CreateForm(forms.Form):
    starting_bid = forms.IntegerField(min_value=1, max_value=99999999)
    item_name = forms.CharField(max_length=64)
    item_description = forms.CharField(max_length=500, widget=forms.Textarea)
    image_url = forms.URLField(required=False)
    category = forms.ChoiceField(choices = Listing.category_choices, required=False)

@login_required(login_url='login')
def create(request):
    user = request.user
    form = CreateForm()
    if request.method == "POST":
        form = CreateForm(request.POST)
        if form.is_valid():
            starting_bid = form.cleaned_data["starting_bid"]
            item_name = form.cleaned_data["item_name"]
            item_description = form.cleaned_data["item_description"]
            image_url = form.cleaned_data["image_url"]
            category = form.cleaned_data["category"]
            new_listing = Listing(starting_bid=starting_bid, item_name=item_name, item_description=item_description, image_url=image_url, category=category, user=user)
            new_listing.save()
            return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/create.html", {
        "form": form
        })

class WatchlistForm(forms.Form):
    in_watchlist = forms.BooleanField()

@login_required(login_url='login')
def watchlist(request):
    user = request.user
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        listing = Listing.objects.get(pk=listing_id)
        in_watchlist = False
        try:
            in_watchlist = listing in Listing.objects.all().filter(watchers=user)
        except:
            pass
        if in_watchlist:
            listing.watchers.remove(user)
        else:
            listing.watchers.add(user)
    return render(request, "auctions/watchlist.html", {
        "watchlist": Listing.objects.all().filter(watchers=user)
    })

@login_required(login_url='login')
def comment(request, listing_id):
    form = CommentForm()
    if request.method == "POST":
        try:
            user = request.user
            listing = Listing.objects.get(pk=listing_id)
            form = CommentForm(request.POST)
            if form.is_valid():
                text = form.cleaned_data["text"]
        except KeyError:
            return HttpResponseBadRequest("Bad Request: no listing chosen")
        except listing.DoesNotExist:
            return HttpResponseBadRequest("Bad Request: Listing does not exist")
        except user.DoesNotExist:
            return HttpResponseBadRequest("Bad Request: User does not exist")
        c = Comment(text=text, user=user)
        c.save()
        listing.comments.add(c)
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    return render(request, "auctions/listing.html", {
        "form": form
    })

@login_required(login_url='login')
def close(request, listing_id):
    if request.method == "POST":
        try:
            user = request.user
            listing = Listing.objects.get(pk=listing_id)
        except KeyError:
            return HttpResponseBadRequest("Bad Request: no listing chosen")
        except listing.DoesNotExist:
            return HttpResponseBadRequest("Bad Request: Listing does not exist")
        except user.DoesNotExist:
            return HttpResponseBadRequest("Bad Request: User does not exist")
        if user == listing.user:
            listing.is_closed=True
            listing.save()
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


class BidForm(forms.ModelForm):

    class Meta:
        model = Bid
        fields = ['price']

    @classmethod
    def for_listing(cls, listing, **kwargs):
        form = cls(**kwargs)
        form.fields['price'].min_value = listing.starting_bid
        return form


@login_required(login_url='login')
def bid(request, listing_id):
    if request.method == "POST":
        try:
            user = request.user
            listing = Listing.objects.get(pk=listing_id)
        except KeyError:
            return HttpResponseBadRequest("Bad Request: no listing chosen")
        except listing.DoesNotExist:
            return HttpResponseBadRequest("Bad Request: Listing does not exist")
        except user.DoesNotExist:
            return HttpResponseBadRequest("Bad Request: User does not exist")
        form = BidForm(request.POST)
        if form.is_valid():
            price = form.cleaned_data["price"]
            listing.starting_bid = price
            listing.save()
            previous_bids = Bid.objects.all().filter(listing=listing_id)
            previous_bids.delete()
            b = Bid(price=price, listing=listing, user=user)
            b.save()
        else:
            print("Error")
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

def categories(request):
    cat = Listing.category_choices
    return render(request, "auctions/categories.html", {
        "categories": cat,
    })

def category(request, abbreviation):
    try:
        category = Listing.objects.all().filter(category=abbreviation)
        return render(request, "auctions/category.html", {
            "category": category,
            "title": [b for (a,b) in Listing.category_choices if a == abbreviation][0]
        })
    except:
        return HttpResponseBadRequest("Bad Request: Category doesn't exist")