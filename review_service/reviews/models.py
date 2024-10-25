from django.db import models
from releases.models import Release
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
   user_id = models.IntegerField(blank=False)
   release = models.ForeignKey(Release, on_delete=models.CASCADE, related_name='reviews')
   review_text = models.CharField(max_length=255, default="", blank=True)
   review_mark = models.IntegerField(
      validators=[MinValueValidator(1), MaxValueValidator(10)]
   )

