import os
import subprocess
from django.db import models
import random
import string

def get_docker_container_ip():
    ip = subprocess.check_output(['hostname', '-I']).decode('utf-8').strip()
    return ip
    

class Release(models.Model):

    def generate_identifier():
        return ''.join(random.choices(str.lower(string.hexdigits), k=8))
    
    release_name = models.CharField(max_length=150)
    artist_name = models.CharField(max_length=150)
    discussion_identifier = models.CharField(max_length=8,unique=True, default=generate_identifier)
    connect_url = models.CharField(max_length=128, blank=True)

    def save(self, *args, **kwargs):
        service_ip = get_docker_container_ip()
        service_port = os.getenv('PORT')

        self.connect_url = f"ws://localhost:{service_port}/discussions/{self.discussion_identifier}"

        super(Release, self).save(*args, **kwargs)
    