from django.urls import path
from .views import HomeTemplateView, SearchView

urlpatterns = [
    path('', HomeTemplateView.as_view(), name='home'),
    path('/get_search_results/', SearchView.as_view(), name='get_search_results'),
]
