from django.contrib import admin
from .models import User, Publication
# Register your models here.
@admin.register(User)
class ProductCategory(admin.ModelAdmin):
    list_display = ['username', 'password']

@admin.register(Publication)
class ProductCategory(admin.ModelAdmin):
    list_display = ['image', 'title', 'author', 'date']
