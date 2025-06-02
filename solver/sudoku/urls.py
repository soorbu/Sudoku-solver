from django.urls import path
from .views import sudoku_view

urlpatterns = [
    path('', sudoku_view, name='sudoku'),
]
