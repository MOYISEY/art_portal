from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager

from users.models import CustomUser
from categories.models import Category

class Project(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    description = models.TextField(verbose_name="Краткое описание")
    content = RichTextUploadingField(verbose_name="Содержание")
    thumbnail = models.ImageField(upload_to='project_thumbnails/', verbose_name="Обложка")
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='projects', verbose_name="Автор")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='projects', verbose_name="Категория")
    tags = TaggableManager(verbose_name="Теги", blank=True)
    views_count = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    likes_count = models.PositiveIntegerField(default=0, verbose_name="Лайки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])

class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images', verbose_name="Проект")
    image = models.ImageField(upload_to='project_images/', verbose_name="Изображение")
    caption = models.CharField(max_length=255, blank=True, verbose_name="Подпись")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    
    class Meta:
        verbose_name = "Изображение проекта"
        verbose_name_plural = "Изображения проектов"
        ordering = ['order']
    
    def __str__(self):
        return f"Изображение для {self.project.title}"

class ProjectLike(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='liked_projects', verbose_name="Пользователь")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='likes', verbose_name="Проект")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Лайк проекта"
        verbose_name_plural = "Лайки проектов"
        unique_together = ('user', 'project')
    
    def __str__(self):
        return f"{self.user.username} лайкнул {self.project.title}"

