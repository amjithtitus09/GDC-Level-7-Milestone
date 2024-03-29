# Add all your views here
from tasks.models import Task, STATUS_CHOICES, History

from django.contrib.auth.models import User

from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django.contrib.auth.mixins import LoginRequiredMixin

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]

class TaskSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ["pk", "title", "description", "completed", "user", "status"]

class HistorySerializer(ModelSerializer):

    class Meta:
        model = History
        fields = ["pk", "task", "old_status", "new_status", "modified_date"]

from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, ChoiceFilter, DateFilter

class TaskFilter(FilterSet):
    title = CharFilter(lookup_expr="icontains")
    status = ChoiceFilter(choices=STATUS_CHOICES)

class HistoryFilter(FilterSet):
    old_status = ChoiceFilter(choices=STATUS_CHOICES)
    new_status = ChoiceFilter(choices=STATUS_CHOICES)
    modified_date = DateFilter(lookup_expr="date", label="Modified date")

class TaskViewSet(LoginRequiredMixin, ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user, completed=False)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class HistoryViewSet(LoginRequiredMixin, ReadOnlyModelViewSet):
    queryset = History.objects.all()
    serializer_class = HistorySerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = HistoryFilter

    def get_queryset(self):
        return History.objects.filter(task = self.kwargs['task_pk'], task__user=self.request.user)