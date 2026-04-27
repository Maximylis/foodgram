from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    """Фильтр ингредиентов по началу названия."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтр рецептов."""

    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset.none() if value else queryset
        if value:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset.none() if value else queryset
        if value:
            return queryset.filter(shopping_cart__user=user)
        return queryset
