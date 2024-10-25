from django.db import models
import random
import string


class Release(models.Model):
    def generate_identifier():
        return ''.join(random.choices(str.lower(string.hexdigits), k=8))
    
    release_name = models.CharField(max_length=150)
    artist_name = models.CharField(max_length=150)
    discussion_identifier = models.CharField(max_length=8,unique=True, default=generate_identifier)

