from django.urls import path
from .views import sudoku_view, sudoku_explanation_view

urlpatterns = [
    path('', sudoku_view, name='sudoku'),
    path('sudoku/how-it-works/', sudoku_explanation_view, name='sudoku_explanation'),
]
