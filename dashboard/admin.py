from django.contrib import admin
from .models import (
  Department, Profile, Subject, Material,
  Rating, Comment, SavedMaterial, Post,
  PostComment, StudyGroup
)

admin.site.register(Department)
admin.site.register(Profile)
admin.site.register(Subject)
admin.site.register(Material)
admin.site.register(Rating)
admin.site.register(Comment)
admin.site.register(SavedMaterial)
admin.site.register(Post)
admin.site.register(PostComment)
admin.site.register(StudyGroup)