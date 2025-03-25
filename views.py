from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Project, ProjectLike
from .forms import ProjectForm, ProjectImageFormSet
from comments.forms import CommentForm
from comments.models import Comment

def home(request):
    featured_projects = Project.objects.order_by('-views_count')[:6]
    latest_projects = Project.objects.order_by('-created_at')[:8]
    
    context = {
        'featured_projects': featured_projects,
        'latest_projects': latest_projects,
    }
    return render(request, 'projects/home.html', context)

def project_list(request):
    projects = Project.objects.all()
    
    # Поиск
    query = request.GET.get('q')
    if query:
        projects = projects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    
    # Фильтрация по категории
    category = request.GET.get('category')
    if category:
        projects = projects.filter(category__slug=category)
    
    # Сортировка
    sort = request.GET.get('sort', '-created_at')
    projects = projects.order_by(sort)
    
    # Пагинация
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'projects/project_list.html', context)

def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    
    # Увеличиваем счетчик просмотров
    project.increment_views()
    
    # Проверяем, лайкнул ли пользователь проект
    user_liked = False
    if request.user.is_authenticated:
        user_liked = ProjectLike.objects.filter(user=request.user, project=project).exists()
    
    # Комментарии
    comments = Comment.objects.filter(project=project).order_by('-created_at')
    comment_form = CommentForm()
    
    # Похожие проекты
    similar_projects = Project.objects.filter(category=project.category).exclude(id=project.id)[:4]
    
    context = {
        'project': project,
        'user_liked': user_liked,
        'comments': comments,
        'comment_form': comment_form,
        'similar_projects': similar_projects,
    }
    return render(request, 'projects/project_detail.html', context)

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        formset = ProjectImageFormSet(request.POST, request.FILES)
        
        if form.is_valid() and formset.is_valid():
            project = form.save(commit=False)
            project.author = request.user
            project.save()
            form.save_m2m()  # Сохраняем теги
            
            formset.instance = project
            formset.save()
            
            messages.success(request, 'Проект успешно создан!')
            return redirect('project_detail', slug=project.slug)
    else:
        form = ProjectForm()
        formset = ProjectImageFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'is_create': True,
    }
    return render(request, 'projects/project_form.html', context)

@login_required
def project_update(request, slug):
    project = get_object_or_404(Project, slug=slug)
    
    # Проверяем, является ли пользователь автором проекта
    if request.user != project.author:
        messages.error(request, 'Вы не можете редактировать этот проект!')
        return redirect('project_detail', slug=project.slug)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        formset = ProjectImageFormSet(request.POST, request.FILES, instance=project)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Проект успешно обновлен!')
            return redirect('project_detail', slug=project.slug)
    else:
        form = ProjectForm(instance=project)
        formset = ProjectImageFormSet(instance=project)
    
    context = {
        'form': form,
        'formset': formset,
        'project': project,
        'is_create': False,
    }
    return render(request, 'projects/project_form.html', context)

@login_required
def project_delete(request, slug):
    project = get_object_or_404(Project, slug=slug)
    
    # Проверяем, является ли пользователь автором проекта
    if request.user != project.author:
        messages.error(request, 'Вы не можете удалить этот проект!')
        return redirect('project_detail', slug=project.slug)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Проект успешно удален!')
        return redirect('project_list')
    
    return render(request, 'projects/project_confirm_delete.html', {'project': project})

@login_required
@require_POST
def project_like(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Проверяем, лайкнул ли пользователь проект
    like, created = ProjectLike.objects.get_or_create(user=request.user, project=project)
    
    if not created:
        # Если лайк уже существует, удаляем его (отменяем лайк)
        like.delete()
        project.likes_count -= 1
        project.save()
        return JsonResponse({'status': 'unliked', 'likes_count': project.likes_count})
    else:
        # Если лайк создан, увеличиваем счетчик лайков
        project.likes_count += 1
        project.save()
        return JsonResponse({'status': 'liked', 'likes_count': project.likes_count})

