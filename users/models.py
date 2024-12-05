from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=15, unique=True)
    password = models.TextField()
    avatar = models.ImageField(upload_to='images/avatars', default="default_avatar.jpg")
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    groups = models.ManyToManyField('auth.Group', related_name='custom_user_groups', blank=True,)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_permissions', blank=True,)

class Publication(models.Model):
    image = models.ImageField(upload_to='images/user_publications')
    title = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_publications')

    def __str__(self):
        return self.title

"""#############################################################################################################################################################################################"""

class LikesPublication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="liked_publications")
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name="liked_publications")

    class Meta:
        unique_together = ('user', 'publication')



class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()

class Subscription(models.Model):
    subscriber = models.ForeignKey(User, related_name='subscriptions', on_delete=models.CASCADE)
    subscribed_to = models.ForeignKey(User, related_name='subscribers', on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('subscriber', 'subscribed_to')