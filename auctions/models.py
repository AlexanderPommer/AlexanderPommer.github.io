from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy

def validate_positive(number):
    if number <= 0:
        raise ValidationError(gettext_lazy('%(number)s is not an positive number'), params={'number': number},)

class User(AbstractUser):
    pass

class Comment(models.Model):
    text = models.TextField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")

class Listing(models.Model):
    category_choices = [
        ('HM', 'Home'),
        ('FA', 'Fashion'),
        ('TY', 'Toys'),
        ('EX', 'Electronics')
    ]
    starting_bid = models.IntegerField(validators=[validate_positive])
    item_name = models.CharField(max_length=64)
    item_description = models.TextField(max_length=500)
    image_url = models.URLField(help_text="url of an image of the item to list")
    creation_datetime = models.DateTimeField(auto_now_add=True, auto_created=True)
    category = models.CharField(max_length=2, choices=category_choices)
    is_closed = models.BooleanField(default=False, editable=True, auto_created=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctioneer")
    watchers = models.ManyToManyField(User, blank=True, related_name="watcher")
    comments =  models.ManyToManyField(Comment, blank=True, related_name="comment")

class Bid(models.Model):
    price = models.IntegerField(validators=[validate_positive])
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bid_item")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
