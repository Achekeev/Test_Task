from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import UserSerializer
from rest_framework.exceptions import PermissionDenied
from .serializers import ArticleSerializer
from .models import Article
from rest_framework.generics import RetrieveAPIView


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ArticleUpdateView(generics.UpdateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        article = super().get_object()
        if not article.can_edit(self.request.user):
            raise PermissionDenied("You do not have permission to edit this article.")
        return article


class PublicArticleListView(generics.ListAPIView):
    queryset = Article.objects.filter(is_public=True)
    serializer_class = ArticleSerializer


class IsPublicOrAuthenticated(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.is_public:
            return True
        return request.user and request.user.is_authenticated


class ArticleDetailView(RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsPublicOrAuthenticated]