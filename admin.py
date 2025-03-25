from django.contrib import admin
from .models import Project, ProjectImage, ProjectLike

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'views_count', 'likes_count')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProjectImageInline]

@admin.register(ProjectLike)
class ProjectLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'project__title')

