from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField("self", related_name="followed_by", symmetrical=False, blank=True, auto_created=True, default=None)

    def count_followers(self):
        return self.followers.count()
    
    def count_following(self):
        return User.objects.filter(followers=self).count()

    def get_followers(self):
        return self.followers.all()
    
    def get_following(self):
        return User.objects.filter(followers=self).all()

    def add_follower(self, follower):
        try:
            if follower != self:
                self.followers.add(follower)
        except:
            pass
        return
    '''
    def __str__(self):
          return f"{self.user.username}"
    '''
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "followers": self.count_followers(),
            "following": self.count_following()
        }

class Post(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField(editable=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # One user can like may posts and one post can be liked by many users so ManyToMany
    #likes = models.ManyToManyField(User, default=None, auto_created=True, related_name="liker", blank=True)
    likes = models.ManyToManyField(User, auto_created=True, related_name="liker", blank=True)

    def count_likes(self):
        return self.likes.count()

    def serialize(self):
        return {
            "id": self.id,
            "poster": self.poster.username,
            "body": self.body,
            "likes": self.count_likes(),
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p")
        }
        
    # Helps render posts in reverse chronologial order, I hope

    class Meta:
        ordering = ['-timestamp']
