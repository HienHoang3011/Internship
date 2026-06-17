from django.urls import path
from .views import TestListCreateView, TestDetailView, TestResultListCreateView, TestAnalyzeView

urlpatterns = [
    path('', TestListCreateView.as_view(), name='test-list-create'),
    path('<int:pk>/', TestDetailView.as_view(), name='test-detail'),
    path('results/', TestResultListCreateView.as_view(), name='test-result-list-create'),
    path('results/<int:result_id>/analyze/', TestAnalyzeView.as_view(), name='test-result-analyze'),
]
