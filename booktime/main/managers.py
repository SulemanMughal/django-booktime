from django.db import models

class ActiveManager(models.Manager):
    def active(self):
        return self.filter(active=True)

class ProductTagManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)