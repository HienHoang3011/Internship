from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("app.api.auth.urls")),
    path("api/diaries/", include("app.api.diary.urls")),
    path("api/lessons/", include("app.api.lesson.urls")),
    path("api/tests/", include("app.api.test.urls")),
    path('api/chat/', include('app.api.chat.urls')),
]
