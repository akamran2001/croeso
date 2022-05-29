from django.contrib import admin
from .models import Site, Tag, SiteImage, Review

admin.site.register(Site)
admin.site.register(Tag)
admin.site.register(SiteImage)
admin.site.register(Review)