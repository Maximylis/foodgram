from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingCartSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserSerializer,
    UserWithRecipesSerializer,
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscription

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Пользователи."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Список подписок текущего пользователя."""

        authors = User.objects.filter(
            subscribers__user=request.user,
        )
        page = self.paginate_queryset(authors)
        serializer_context = {
            **self.get_serializer_context(),
            'recipes_limit': request.query_params.get('recipes_limit'),
        }
        if page is not None:
            serializer = UserWithRecipesSerializer(
                page,
                many=True,
                context=serializer_context,
            )
            return self.get_paginated_response(serializer.data)
        serializer = UserWithRecipesSerializer(
            authors,
            many=True,
            context=serializer_context,
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        """Подписка и отписка от автора."""

        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data={
                    'user': request.user.id,
                    'author': author.id,
                },
                context=self.get_serializer_context(),
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        subscription = Subscription.objects.filter(
            user=request.user,
            author=author,
        )
        if not subscription.exists():
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('put', 'delete'),
        url_path='me/avatar',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def avatar(self, request):
        """Загрузка и удаление аватара текущего пользователя."""

        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(
                user,
                data=request.data,
                context=self.get_serializer_context(),
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        if user.avatar:
            user.avatar.delete(save=False)
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Теги."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Ингредиенты."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        return Recipe.objects.select_related(
            'author',
        ).prefetch_related(
            'tags',
            'recipe_ingredients__ingredient',
        )

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action in (
            'create',
            'partial_update',
            'update',
            'destroy',
            'favorite',
            'shopping_cart',
            'download_shopping_cart',
        ):
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()

    def create_relation(self, request, pk, serializer_class):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = serializer_class(
            data={
                'user': request.user.id,
                'recipe': recipe.id,
            },
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def delete_relation(self, request, pk, model):
        recipe = get_object_or_404(Recipe, pk=pk)
        relation = model.objects.filter(
            user=request.user,
            recipe=recipe,
        )
        if not relation.exists():
            return Response(
                {'errors': 'Рецепт не был добавлен.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        """Добавление рецепта в избранное и удаление из избранного."""

        if request.method == 'POST':
            return self.create_relation(
                request,
                pk,
                FavoriteSerializer,
            )
        return self.delete_relation(
            request,
            pk,
            Favorite,
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Добавление рецепта в список покупок и удаление из него."""

        if request.method == 'POST':
            return self.create_relation(
                request,
                pk,
                ShoppingCartSerializer,
            )
        return self.delete_relation(
            request,
            pk,
            ShoppingCart,
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок."""

        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user,
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(
            amount=Sum('amount'),
        ).order_by(
            'ingredient__name',
        )
        lines = ['Список покупок Foodgram:\n']
        for ingredient in ingredients:
            lines.append(
                f"{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) — "
                f"{ingredient['amount']}"
            )

        content = '\n'.join(lines)
        response = HttpResponse(
            content,
            content_type='text/plain; charset=utf-8',
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response

    @action(
        detail=True,
        methods=('get',),
        url_path='get-link',
        permission_classes=(permissions.AllowAny,),
    )
    def get_link(self, request, pk=None):
        """Получить короткую ссылку на рецепт."""

        recipe = get_object_or_404(Recipe, pk=pk)
        short_link = request.build_absolute_uri(f'/recipes/{recipe.id}/')
        return Response({'short-link': short_link})
