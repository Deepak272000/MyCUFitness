from django.urls import path
from chatbot.views import chatbot_response, log_fitness_progress, get_progress_chart

urlpatterns = [

    path('chat/', chatbot_response, name='chatbot'),
    path('log-progress/', log_fitness_progress, name="log_fitness_progress"),
    path('progress-chart/', get_progress_chart, name="progress_chart"),
]
