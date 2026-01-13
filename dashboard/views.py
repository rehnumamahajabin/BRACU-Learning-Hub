from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q
from .models import (
    Profile, Material, Rating, Comment, SavedMaterial,
    Post, PostComment, StudyGroup, Subject, Department
)
from .forms import (
    UserRegisterForm, ProfileUpdateForm, MaterialUploadForm,
    MaterialUpdateForm, PostForm, CommentForm, PostCommentForm
)

# Home View
def home(request):
    recent_materials = Material.objects.filter(is_approved=True).order_by('-upload_date')[:6]
    recent_posts = Post.objects.filter(is_reported=False).order_by('-created_at')[:5]
    study_groups = StudyGroup.objects.filter(is_public=True).order_by('-created_at')[:4]
    
    context = {
        'recent_materials': recent_materials,
        'recent_posts': recent_posts,
        'study_groups': study_groups,
    }
    return render(request, 'dashboard/home.html', context)

# Registration View
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = UserRegisterForm()
    
    return render(request, 'dashboard/register.html', {'form': form})

# Profile Views
@login_required
def profile(request):
    user_materials = Material.objects.filter(uploaded_by=request.user)
    saved_materials = SavedMaterial.objects.filter(user=request.user)
    user_posts = Post.objects.filter(user=request.user)
    
    context = {
        'user_materials': user_materials,
        'saved_materials': saved_materials,
        'user_posts': user_posts,
    }
    return render(request, 'dashboard/profile.html', context)

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    
    return render(request, 'dashboard/profile_edit.html', {'form': form})

# Material Views
def material_list(request):
    materials = Material.objects.filter(is_approved=True)
    
    subject_filter = request.GET.get('subject')
    type_filter = request.GET.get('type')
    search_query = request.GET.get('q')
    
    if subject_filter:
        materials = materials.filter(subject__id=subject_filter)
    if type_filter:
        materials = materials.filter(material_type=type_filter)
    if search_query:
        materials = materials.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    subjects = Subject.objects.all()
    
    context = {
        'materials': materials,
        'subjects': subjects,
    }
    return render(request, 'dashboard/material_list.html', context)

def material_detail(request, pk):
    material = get_object_or_404(Material, pk=pk)
    material.views += 1
    material.save()
    
    comments = Comment.objects.filter(material=material)
    ratings = Rating.objects.filter(material=material)
    
    is_saved = False
    user_rating = None
    if request.user.is_authenticated:
        is_saved = SavedMaterial.objects.filter(user=request.user, material=material).exists()
        try:
            user_rating = Rating.objects.get(user=request.user, material=material)
        except Rating.DoesNotExist:
            pass
    
    avg_rating = material.ratings.aggregate(models.Avg('score'))['score__avg'] or 0
    
    context = {
        'material': material,
        'comments': comments,
        'ratings': ratings,
        'is_saved': is_saved,
        'user_rating': user_rating,
        'avg_rating': avg_rating,
    }
    return render(request, 'dashboard/material_detail.html', context)

@login_required
def material_upload(request):
    if request.method == 'POST':
        form = MaterialUploadForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.uploaded_by = request.user
            material.save()
            messages.success(request, 'Material uploaded successfully!')
            return redirect('material_detail', pk=material.pk)
    else:
        form = MaterialUploadForm()
    
    return render(request, 'dashboard/material_upload.html', {'form': form})

@login_required
def material_edit(request, pk):
    material = get_object_or_404(Material, pk=pk, uploaded_by=request.user)
    
    if request.method == 'POST':
        form = MaterialUpdateForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material updated successfully!')
            return redirect('material_detail', pk=material.pk)
    else:
        form = MaterialUpdateForm(instance=material)
    
    return render(request, 'dashboard/material_edit.html', {'form': form})

@login_required
def material_delete(request, pk):
    material = get_object_or_404(Material, pk=pk, uploaded_by=request.user)
    
    if request.method == 'POST':
        material.delete()
        messages.success(request, 'Material deleted successfully!')
        return redirect('material_list')
    
    return render(request, 'dashboard/material_confirm_delete.html', {'material': material})

@login_required
def save_material(request, pk):
    material = get_object_or_404(Material, pk=pk)
    
    if SavedMaterial.objects.filter(user=request.user, material=material).exists():
        SavedMaterial.objects.filter(user=request.user, material=material).delete()
        messages.info(request, 'Material removed from saved list.')
    else:
        SavedMaterial.objects.create(user=request.user, material=material)
        messages.success(request, 'Material saved successfully!')
    
    return redirect('material_detail', pk=material.pk)

@login_required
def rate_material(request, pk):
    material = get_object_or_404(Material, pk=pk)
    
    if request.method == 'POST':
        score = request.POST.get('score')
        if score:
            rating, created = Rating.objects.update_or_create(
                user=request.user,
                material=material,
                defaults={'score': score}
            )
            messages.success(request, 'Rating submitted successfully!')
    
    return redirect('material_detail', pk=material.pk)

@login_required
def add_comment(request, pk):
    material = get_object_or_404(Material, pk=pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.material = material
            comment.save()
            messages.success(request, 'Comment added successfully!')
    
    return redirect('material_detail', pk=material.pk)

@login_required
def saved_materials(request):
    saved_items = SavedMaterial.objects.filter(user=request.user).order_by('-saved_at')
    return render(request, 'dashboard/saved_materials.html', {'saved_items': saved_items})

# Post Views
def post_list(request):
    posts = Post.objects.filter(is_reported=False).order_by('-is_pinned', '-created_at')
    
    type_filter = request.GET.get('type')
    search_query = request.GET.get('q')
    
    if type_filter:
        posts = posts.filter(post_type=type_filter)
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    context = {
        'posts': posts,
    }
    return render(request, 'dashboard/post_list.html', context)

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = PostComment.objects.filter(post=post, is_reported=False)
    
    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'dashboard/post_detail.html', context)

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    
    return render(request, 'dashboard/post_create.html', {'form': form})

@login_required
def add_post_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        form = PostCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            messages.success(request, 'Comment added successfully!')
    
    return redirect('post_detail', pk=post.pk)

# Study Group Views
def study_group_list(request):
    study_groups = StudyGroup.objects.filter(is_public=True).order_by('-created_at')
    return render(request, 'dashboard/study_group_list.html', {'study_groups': study_groups})

def study_group_detail(request, pk):
    study_group = get_object_or_404(StudyGroup, pk=pk)
    is_member = study_group.members.filter(id=request.user.id).exists() if request.user.is_authenticated else False
    
    context = {
        'study_group': study_group,
        'is_member': is_member,
    }
    return render(request, 'dashboard/study_group_detail.html', context)

@login_required
def study_group_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        subject_id = request.POST.get('subject')
        is_public = request.POST.get('is_public') == 'on'
        max_members = request.POST.get('max_members', 10)
        
        if name and description and subject_id:
            subject = get_object_or_404(Subject, pk=subject_id)
            study_group = StudyGroup.objects.create(
                name=name,
                description=description,
                subject=subject,
                created_by=request.user,
                is_public=is_public,
                max_members=max_members
            )
            study_group.members.add(request.user)
            messages.success(request, 'Study group created successfully!')
            return redirect('study_group_detail', pk=study_group.pk)
    
    subjects = Subject.objects.all()
    return render(request, 'dashboard/study_group_create.html', {'subjects': subjects})

@login_required
def study_group_join(request, pk):
    study_group = get_object_or_404(StudyGroup, pk=pk)
    
    if study_group.members.count() < study_group.max_members:
        study_group.members.add(request.user)
        messages.success(request, 'You have joined the study group!')
    else:
        messages.error(request, 'Study group is full!')
    
    return redirect('study_group_detail', pk=study_group.pk)

# Search View
def search(request):
    query = request.GET.get('q', '')
    
    materials = Material.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(tags__icontains=query)
    ).filter(is_approved=True)[:10]
    
    posts = Post.objects.filter(
        Q(title__icontains=query) |
        Q(content__icontains=query) |
        Q(tags__icontains=query)
    ).filter(is_reported=False)[:10]
    
    subjects = Subject.objects.filter(
        Q(name__icontains=query) |
        Q(code__icontains=query) |
        Q(description__icontains=query)
    )[:10]
    
    context = {
        'query': query,
        'materials': materials,
        'posts': posts,
        'subjects': subjects,
    }
    return render(request, 'dashboard/search.html', context)

# Admin Dashboard
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    pending_materials = Material.objects.filter(is_approved=False)
    reported_posts = Post.objects.filter(is_reported=True)
    reported_comments = Comment.objects.filter(is_reported=True)
    
    context = {
        'pending_materials': pending_materials,
        'reported_posts': reported_posts,
        'reported_comments': reported_comments,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)