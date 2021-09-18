from django.urls import path
from . import views as classviews

urlpatterns = [
    path('assignment/', classviews.AssignmentCreateFilter.as_view()),
    path('assignment/submission/<int:pk>',classviews.Submissions.as_view()),
    path('assignment/<int:pk>',classviews.AssignmentOperations.as_view())
]
