from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from api.fields import Base64ImageField
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


class UserCreateSerializer(serializers.ModelSerializer):
    """Регистрация пользователя."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Пользователь."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')

        if request is None or request.user.is_anonymous:
            return False

        return Subscription.objects.filter(
            user=request.user,
            author=obj,
        ).exists()


class SetPasswordSerializer(serializers.Serializer):
    """Смена пароля текущего пользователя."""

    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        user = self.context['request'].user

        if not user.check_password(value):
            raise serializers.ValidationError('Неверный текущий пароль.')

        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class AvatarSerializer(serializers.ModelSerializer):
    """Загрузка и удаление аватара пользователя."""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class TagSerializer(serializers.ModelSerializer):
    """Тег."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Ингредиент."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """Ингредиент внутри рецепта при чтении."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeIngredientWriteSerializer(serializers.Serializer):
    """Ингредиент внутри рецепта при создании/обновлении."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField(min_value=1)


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Короткое представление рецепта."""

    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    """Рецепт при чтении."""

    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')

        if request is None or request.user.is_anonymous:
            return False

        return Favorite.objects.filter(
            user=request.user,
            recipe=obj,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')

        if request is None or request.user.is_anonymous:
            return False

        return ShoppingCart.objects.filter(
            user=request.user,
            recipe=obj,
        ).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Создание и редактирование рецепта."""

    ingredients = RecipeIngredientWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Нужно добавить хотя бы один ингредиент.'
            )

        ingredient_ids = [item['id'].id for item in ingredients]

        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.'
            )

        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Нужно добавить хотя бы один тег.'
            )

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Теги не должны повторяться.'
            )

        return tags

    def create_recipe_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient_data['id'],
                    amount=ingredient_data['amount'],
                )
                for ingredient_data in ingredients
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_recipe_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        instance.recipe_ingredients.all().delete()
        self.create_recipe_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context=self.context,
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Добавление рецепта в избранное."""

    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe',
        )
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное.',
            )
        ]

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(
            instance.recipe,
            context=self.context,
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Добавление рецепта в список покупок."""

    class Meta:
        model = ShoppingCart
        fields = (
            'user',
            'recipe',
        )
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в список покупок.',
            )
        ]

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(
            instance.recipe,
            context=self.context,
        ).data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Подписка на автора."""

    class Meta:
        model = Subscription
        fields = (
            'user',
            'author',
        )
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя.',
            )
        ]

    def validate(self, attrs):
        if attrs['user'] == attrs['author']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )

        return attrs

    def to_representation(self, instance):
        request = self.context.get('request')
        recipes_limit = None

        if request:
            recipes_limit = request.query_params.get('recipes_limit')

        return UserWithRecipesSerializer(
            instance.author,
            context={
                **self.context,
                'recipes_limit': recipes_limit,
            },
        ).data


class UserWithRecipesSerializer(UserSerializer):
    """Пользователь с коротким списком рецептов."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True,
    )

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        recipes_limit = self.context.get('recipes_limit')

        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                pass

        return RecipeMinifiedSerializer(
            recipes,
            many=True,
            context=self.context,
        ).data
