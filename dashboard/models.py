from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator

class Department(models.Model):
  name = models.CharField(max_length=100)
  code = models.CharField(max_length=10)

  def __str__(self):
    return f"{self.code} - {self.name}"

class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  image = models.ImageField(default='default.jpg', upload_to='profile_pics')
  bio = models.TextField(blank=True, null=True, max_length=500)
  cgpa = models.FloatField(
    blank=True,
    null=True,
    validators=[MinValueValidator(0.0), MaxValueValidator(4.0)]
  )
  credits_completed = models.IntegerField(default=0)
  department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
  is_studying = models.BooleanField(default=False)
  reputation = models.IntegerField(default=0)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return f'{self.user.username} Profile'

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
  if created:
    Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
  instance.profile.save()

class Subject(models.Model):
  name = models.CharField(max_length=200)
  code = models.CharField(max_length=20, unique=True)
  department = models.ForeignKey(Department, on_delete=models.CASCADE)
  description = models.TextField(blank=True, null=True)

  def __str__(self):
    return f"{self.code} - {self.name}"

class Material(models.Model):
  MATERIAL_TYPES = [
    ('note', 'Class Note'),
    ('slide', 'Presentation Slide'),
    ('assignment', 'Assignment'),
    ('book', 'Reference Book'),
    ('question', 'Previous Question'),
    ('other', 'Other'),
  ]

  title = models.CharField(max_length=200)
  description = models.TextField()
  file = models.FileField(upload_to='materials/%Y/%m/%d/')
  uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
  subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
  material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES, default='note')
  tags = models.CharField(max_length=200, blank=True)
  upload_date = models.DateTimeField(auto_now_add=True)
  is_approved = models.BooleanField(default=True)
  reports = models.IntegerField(default=0)
  downloads = models.IntegerField(default=0)
  views = models.IntegerField(default=0)

  def __str__(self):
    return self.title

class Rating(models.Model):
  material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='ratings')
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  score = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    unique_together = ('material', 'user')

  def __str__(self):
    return f'{self.score}/5 by {self.user.username}'

class Comment(models.Model):
  material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='comments')
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  content = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  upvotes = models.IntegerField(default=0)
  downvotes = models.IntegerField(default=0)
  is_reported = models.BooleanField(default=False)

  def __str__(self):
    return f'Comment by {self.user.username}'

class SavedMaterial(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  material = models.ForeignKey(Material, on_delete=models.CASCADE)
  saved_at = models.DateTimeField(auto_now_add=True)
  note = models.TextField(blank=True, null=True)

  class Meta:
    unique_together = ('user', 'material')

  def __str__(self):
    return f'{self.user.username} saved {self.material.title}'

class Post(models.Model):
  POST_TYPES = [
    ('personal', 'Personal'),
    ('discussion', 'Discussion'),
    ('question', 'Question'),
    ('announcement', 'Announcement'),
    ('resource', 'Resource Sharing'),
  ]

  user = models.ForeignKey(User, on_delete=models.CASCADE)
  title = models.CharField(max_length=200)
  content = models.TextField()
  post_type = models.CharField(max_length=20, choices=POST_TYPES, default='discussion')
  subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
  tags = models.CharField(max_length=200, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  upvotes = models.IntegerField(default=0)
  downvotes = models.IntegerField(default=0)
  is_reported = models.BooleanField(default=False)
  is_pinned = models.BooleanField(default=False)

  def __str__(self):
    return self.title

class PostComment(models.Model):
  post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comments')
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  content = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  upvotes = models.IntegerField(default=0)
  downvotes = models.IntegerField(default=0)
  is_reported = models.BooleanField(default=False)

  def __str__(self):
    return f'Comment by {self.user.username}'

class StudyGroup(models.Model):
  name = models.CharField(max_length=200)
  description = models.TextField()
  subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
  created_by = models.ForeignKey(User, on_delete=models.CASCADE)
  members = models.ManyToManyField(User, related_name='study_groups')
  created_at = models.DateTimeField(auto_now_add=True)
  is_public = models.BooleanField(default=True)
  max_members = models.IntegerField(default=10)

  def __str__(self):
    return self.name