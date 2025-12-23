"""
Test suite for serializers.py functionality.
Simplified comprehensive testing with high coverage.
"""

import pytest
import uuid
from decimal import Decimal
from django.utils import timezone
from rest_framework import serializers

from apps.core.models import (
    Product, ProductNutrient, Nutrient, Goal, GoalNutrient, 
    Meal, MealItem
)
from apps.core.models.eaten_meal import EatenMeal
from apps.users.models import Profile
from apps.api.serializers import (
    NutrientSerializer,
    ProfileSerializer,
    GoalSerializer,
    GoalNutrientWriteSerializer,
    GoalNutrientReadSerializer,
    MealItemSerializer,
    MealItemWriteSerializer,
    MealSerializer,
    MealWriteSerializer,
    EatenMealWriteSerializer,
    EatenMealReadSerializer
)


# =========================================================
# FIXTURES
# =========================================================

@pytest.fixture
def test_profile(db):
    """Create a test profile."""
    return Profile.objects.create(
        id=uuid.uuid4(),
        username='testuser',
        email='test@example.com',
        is_admin=False
    )


@pytest.fixture
def test_nutrient(db):
    """Create a test nutrient."""
    return Nutrient.objects.create(
        code='energy_kj',
        name='Energy (kJ)',
        unit='kJ',
        category='macronutrient',
        display_order=1,
        is_visible=True
    )


@pytest.fixture
def test_goal(db, test_profile):
    """Create a test goal."""
    return Goal.objects.create(
        user=test_profile,
        target_weight_kg=70.0,
        target_calories=2000,
        consumed_calories=1500.0,
        reset_frequency=Goal.ResetFrequency.DAILY
    )


@pytest.fixture
def test_goal_nutrient(db, test_goal, test_nutrient):
    """Create a test goal nutrient."""
    return GoalNutrient.objects.create(
        goal=test_goal,
        nutrient=test_nutrient,
        target_amount=100.0,
        consumed_amount=50.0
    )


@pytest.fixture
def test_product(db):
    """Create a test product."""
    return Product.objects.create(
        barcode='1234567890123',
        name='Test Product',
        brand='Test Brand',
        description='Test description',
        size='500g',
        price_current=Decimal('10.99'),
        is_on_special=False,
        image_url='https://example.com/image.jpg',
        product_url='https://example.com/product',
        health_star='4.5',
        allergens='Milk, Soy',
        serving_size_value=Decimal('100.000'),
        serving_size_unit='g',
        servings_per_pack=Decimal('5.000'),
        nutrition_basis='per_100g',
        primary_source='user_added'
    )


@pytest.fixture
def test_meal(db, test_profile):
    """Create a test meal."""
    return Meal.objects.create(
        user=test_profile,
        meal_type=Meal.MealType.BREAKFAST,
        name='Test Breakfast',
        date_time=timezone.now(),
        notes='Test meal notes'
    )


@pytest.fixture
def test_meal_item(db, test_meal, test_product):
    """Create a test meal item."""
    return MealItem.objects.create(
        meal=test_meal,
        product=test_product,
        quantity=150.0
    )


@pytest.fixture
def test_eaten_meal(db, test_profile, test_meal):
    """Create a test eaten meal."""
    return EatenMeal.objects.create(
        user=test_profile,
        meal=test_meal,
        eaten_at=timezone.now()
    )


# =========================================================
# NUTRIENT SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestNutrientSerializer:
    """Tests for NutrientSerializer functionality."""
    
    def test_nutrient_serializer_read(self, test_nutrient):
        """Test NutrientSerializer for reading existing nutrient."""
        serializer = NutrientSerializer(test_nutrient)
        data = serializer.data
        
        assert data['id'] == str(test_nutrient.id)
        assert data['code'] == test_nutrient.code
        assert data['name'] == test_nutrient.name
        assert data['unit'] == test_nutrient.unit
        assert data['category'] == test_nutrient.category
    
    def test_nutrient_serializer_create(self, db):
        """Test NutrientSerializer for creating new nutrient."""
        data = {
            'code': 'fiber',
            'name': 'Dietary Fiber',
            'unit': 'g',
            'category': 'macronutrient',
            'display_order': 5,
            'is_visible': True
        }
        
        serializer = NutrientSerializer(data=data)
        assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"
        
        nutrient = serializer.save()
        assert nutrient.code == 'fiber'
        assert nutrient.name == 'Dietary Fiber'
        assert nutrient.unit == 'g'
        assert nutrient.category == 'macronutrient'
    
    def test_nutrient_serializer_update(self, test_nutrient):
        """Test NutrientSerializer for updating nutrient."""
        data = {
            'code': 'energy_kcal',
            'name': 'Energy (kcal)',
            'unit': 'kcal',
            'category': 'macronutrient',
            'display_order': 1,
            'is_visible': False
        }
        
        serializer = NutrientSerializer(test_nutrient, data=data)
        assert serializer.is_valid()
        
        nutrient = serializer.save()
        assert nutrient.code == 'energy_kcal'
        assert nutrient.name == 'Energy (kcal)'
        assert nutrient.unit == 'kcal'
        assert nutrient.is_visible is False


# =========================================================
# PROFILE SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestProfileSerializer:
    """Tests for ProfileSerializer functionality."""
    
    def test_profile_serializer_read(self, test_profile):
        """Test ProfileSerializer for reading existing profile."""
        serializer = ProfileSerializer(test_profile)
        data = serializer.data
        
        assert data['id'] == str(test_profile.id)
        assert data['username'] == test_profile.username
        assert data['email'] == test_profile.email
        assert data['is_admin'] == test_profile.is_admin
    
    def test_profile_serializer_create(self, db):
        """Test ProfileSerializer for creating new profile."""
        data = {
            'id': str(uuid.uuid4()),
            'username': 'newuser',
            'email': 'newuser@example.com',
            'is_admin': False
        }
        
        serializer = ProfileSerializer(data=data)
        assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"
        
        profile = serializer.save()
        assert profile.username == 'newuser'
        assert profile.email == 'newuser@example.com'
        assert profile.is_admin is False
    
    def test_profile_serializer_partial_update(self, test_profile):
        """Test ProfileSerializer for partial update."""
        data = {
            'email': 'partial@example.com'
        }
        
        serializer = ProfileSerializer(test_profile, data=data, partial=True)
        assert serializer.is_valid()
        
        profile = serializer.save()
        assert profile.email == 'partial@example.com'
        assert profile.username == test_profile.username


# =========================================================
# GOAL SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestGoalSerializer:
    """Tests for GoalSerializer functionality."""
    
    def test_goal_serializer_read(self, test_goal):
        """Test GoalSerializer for reading existing goal."""
        serializer = GoalSerializer(test_goal)
        data = serializer.data
        
        assert data['id'] == str(test_goal.id)
        assert data['user'] == test_goal.user.id
        assert data['target_weight_kg'] == test_goal.target_weight_kg
        assert data['target_calories'] == test_goal.target_calories
        assert data['consumed_calories'] == test_goal.consumed_calories
        assert data['reset_frequency'] == test_goal.reset_frequency
    
    def test_goal_serializer_create(self, db, test_profile):
        """Test GoalSerializer for creating new goal."""
        data = {
            'user': test_profile.id,
            'target_weight_kg': 75.0,
            'target_calories': 2500,
            'consumed_calories': 0.0,
            'reset_frequency': Goal.ResetFrequency.WEEKLY
        }
        
        serializer = GoalSerializer(data=data)
        assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"
        
        goal = serializer.save()
        assert goal.user == test_profile
        assert goal.target_weight_kg == 75.0
        assert goal.target_calories == 2500
        assert goal.consumed_calories == 0.0
        assert goal.reset_frequency == Goal.ResetFrequency.WEEKLY
    
    def test_goal_serializer_partial_update(self, test_goal):
        """Test GoalSerializer for partial update."""
        data = {
            'target_calories': 3500
        }
        
        serializer = GoalSerializer(test_goal, data=data, partial=True)
        assert serializer.is_valid()
        
        goal = serializer.save()
        assert goal.target_calories == 3500
        assert goal.target_weight_kg == test_goal.target_weight_kg


# =========================================================
# GOAL NUTRIENT WRITE SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestGoalNutrientWriteSerializer:
    """Tests for GoalNutrientWriteSerializer functionality."""
    
    def test_goal_nutrient_write_serializer_create(self, test_goal, test_nutrient):
        """Test GoalNutrientWriteSerializer for creation."""
        data = {
            'goal': test_goal.id,
            'nutrient': test_nutrient.id,
            'target_amount': 100.0,
            'consumed_amount': 0.0
        }
        
        serializer = GoalNutrientWriteSerializer(data=data)
        assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"
        
        goal_nutrient = serializer.save()
        assert goal_nutrient.goal == test_goal
        assert goal_nutrient.nutrient == test_nutrient
        assert goal_nutrient.target_amount == 100.0
        assert goal_nutrient.consumed_amount == 0.0
    
    def test_goal_nutrient_write_serializer_invalid_goal(self, test_nutrient):
        """Test GoalNutrientWriteSerializer with invalid goal ID."""
        data = {
            'goal': uuid.uuid4(),  # Non-existent goal
            'nutrient': test_nutrient.id,
            'target_amount': 100.0
        }
        
        serializer = GoalNutrientWriteSerializer(data=data)
        assert not serializer.is_valid()
        assert 'goal' in serializer.errors


# =========================================================
# GOAL NUTRIENT READ SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestGoalNutrientReadSerializer:
    """Tests for GoalNutrientReadSerializer functionality."""
    
    def test_goal_nutrient_read_serializer(self, test_goal_nutrient):
        """Test GoalNutrientReadSerializer basic functionality."""
        serializer = GoalNutrientReadSerializer(test_goal_nutrient)
        data = serializer.data
        
        assert data['id'] == str(test_goal_nutrient.id)
        assert data['goal'] == test_goal_nutrient.goal.id
        assert data['nutrient']['id'] == str(test_goal_nutrient.nutrient.id)
        assert data['nutrient']['name'] == test_goal_nutrient.nutrient.name
        assert data['nutrient']['unit'] == test_goal_nutrient.nutrient.unit
        assert data['target_amount'] == test_goal_nutrient.target_amount
        assert data['consumed_amount'] == test_goal_nutrient.consumed_amount
    
    def test_goal_nutrient_read_serializer_nested_nutrient(self, test_goal_nutrient):
        """Test that nested nutrient serializer is used."""
        serializer = GoalNutrientReadSerializer(test_goal_nutrient)
        data = serializer.data
        
        assert isinstance(data['nutrient'], dict)
        assert 'id' in data['nutrient']
        assert 'name' in data['nutrient']
        assert 'unit' in data['nutrient']
        assert 'category' in data['nutrient']


# =========================================================
# MEAL ITEM SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestMealItemSerializer:
    """Tests for MealItemSerializer functionality."""
    
    def test_meal_item_serializer_read(self, test_meal_item):
        """Test MealItemSerializer for reading existing meal item."""
        serializer = MealItemSerializer(test_meal_item)
        data = serializer.data
        
        assert data['id'] == str(test_meal_item.id)
        assert data['quantity'] == test_meal_item.quantity
        assert data['meal'] == test_meal_item.meal.id
        assert 'product' in data
        assert data['product']['barcode'] == test_meal_item.product.barcode
        assert data['product']['name'] == test_meal_item.product.name
    
    def test_meal_item_serializer_nested_product(self, test_meal_item):
        """Test that nested product serializer is used."""
        serializer = MealItemSerializer(test_meal_item)
        data = serializer.data
        
        assert isinstance(data['product'], dict)
        assert 'barcode' in data['product']
        assert 'name' in data['product']
        assert 'brand' in data['product']


# =========================================================
# MEAL ITEM WRITE SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestMealItemWriteSerializer:
    """Tests for MealItemWriteSerializer functionality."""
    
    def test_meal_item_write_serializer_create(self, test_meal, test_product):
        """Test MealItemWriteSerializer for creation."""
        data = {
            'meal': test_meal.id,
            'product': test_product.barcode,
            'quantity': 200.0
        }
        
        serializer = MealItemWriteSerializer(data=data)
        assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"
        
        meal_item = serializer.save()
        assert meal_item.meal == test_meal
        assert meal_item.product == test_product
        assert meal_item.quantity == 200.0
    
    def test_meal_item_write_serializer_invalid_meal(self, test_product):
        """Test MealItemWriteSerializer with invalid meal ID."""
        data = {
            'meal': uuid.uuid4(),  # Non-existent meal
            'product': test_product.barcode,
            'quantity': 100.0
        }
        
        serializer = MealItemWriteSerializer(data=data)
        assert not serializer.is_valid()
        assert 'meal' in serializer.errors


# =========================================================
# MEAL SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestMealSerializer:
    """Tests for MealSerializer functionality."""
    
    def test_meal_serializer_read(self, test_meal):
        """Test MealSerializer for reading existing meal."""
        serializer = MealSerializer(test_meal)
        data = serializer.data
        
        assert data['id'] == str(test_meal.id)
        assert data['user'] == test_meal.user.id
        assert data['meal_type'] == test_meal.meal_type
        assert data['name'] == test_meal.name
        assert data['date_time'] == test_meal.date_time.isoformat().replace('+00:00', 'Z')
        assert data['notes'] == test_meal.notes
        assert 'items' in data
        assert data['items'] == []
    
    def test_meal_serializer_with_items(self, test_meal_item):
        """Test MealSerializer with meal items."""
        serializer = MealSerializer(test_meal_item.meal)
        data = serializer.data
        
        assert len(data['items']) == 1
        assert data['items'][0]['id'] == str(test_meal_item.id)
        assert data['items'][0]['quantity'] == test_meal_item.quantity


# =========================================================
# MEAL WRITE SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestMealWriteSerializer:
    """Tests for MealWriteSerializer functionality."""
    
    def test_meal_write_serializer_create(self, test_profile):
        """Test MealWriteSerializer for creating new meal."""
        data = {
            'user': test_profile.id,
            'meal_type': Meal.MealType.LUNCH,
            'name': 'Test Lunch',
            'date_time': timezone.now().isoformat(),
            'notes': 'Test lunch notes',
            'items': []
        }
        
        serializer = MealWriteSerializer(data=data)
        assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"
        
        meal = serializer.save()
        assert meal.user == test_profile
        assert meal.meal_type == Meal.MealType.LUNCH
        assert meal.name == 'Test Lunch'
        assert meal.notes == 'Test lunch notes'
    
    def test_meal_write_serializer_create_method(self, test_profile, test_product):
        """Test the custom create method of MealWriteSerializer."""
        data = {
            'user': test_profile.id,
            'meal_type': Meal.MealType.BREAKFAST,
            'name': 'Custom Create Test',
            'date_time': timezone.now().isoformat(),
            'notes': 'Custom create notes',
            'items': []
        }
        
        serializer = MealWriteSerializer(data=data)
        assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"
        
        meal = serializer.save()
        assert meal.name == 'Custom Create Test'
        assert meal.items.count() == 0
    
    def test_meal_write_serializer_partial_update(self, test_meal):
        """Test MealWriteSerializer for partial update."""
        data = {
            'name': 'Partially Updated Meal'
        }
        
        serializer = MealWriteSerializer(test_meal, data=data, partial=True)
        assert serializer.is_valid()
        
        updated_meal = serializer.save()
        assert updated_meal.name == 'Partially Updated Meal'
        assert updated_meal.meal_type == test_meal.meal_type


# =========================================================
# EATEN MEAL WRITE SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestEatenMealWriteSerializer:
    """Tests for EatenMealWriteSerializer functionality."""
    
    def test_eaten_meal_write_serializer_create(self, test_profile, test_meal):
        """Test EatenMealWriteSerializer for creating new eaten meal."""
        data = {
            'user': test_profile.id,
            'meal': test_meal.id
        }
        
        serializer = EatenMealWriteSerializer(data=data)
        assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"
        
        eaten_meal = serializer.save()
        assert eaten_meal.user == test_profile
        assert eaten_meal.meal == test_meal
        assert eaten_meal.eaten_at is not None
    
    def test_eaten_meal_write_serializer_invalid_user(self, test_meal):
        """Test EatenMealWriteSerializer with invalid user ID."""
        data = {
            'user': uuid.uuid4(),  # Non-existent user
            'meal': test_meal.id
        }
        
        serializer = EatenMealWriteSerializer(data=data)
        assert not serializer.is_valid()
        assert 'user' in serializer.errors


# =========================================================
# EATEN MEAL READ SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestEatenMealReadSerializer:
    """Tests for EatenMealReadSerializer functionality."""
    
    def test_eaten_meal_read_serializer(self, test_eaten_meal):
        """Test EatenMealReadSerializer basic functionality."""
        serializer = EatenMealReadSerializer(test_eaten_meal)
        data = serializer.data
        
        assert data['id'] == str(test_eaten_meal.id)
        assert data['user'] == test_eaten_meal.user.id
        assert 'meal' in data
        assert data['meal']['id'] == str(test_eaten_meal.meal.id)
        assert data['meal']['name'] == test_eaten_meal.meal.name
        assert data['meal']['meal_type'] == test_eaten_meal.meal.meal_type
        assert data['eaten_at'] == test_eaten_meal.eaten_at.isoformat().replace('+00:00', 'Z')
    
    def test_eaten_meal_read_serializer_nested_meal(self, test_eaten_meal):
        """Test that nested meal serializer is used."""
        serializer = EatenMealReadSerializer(test_eaten_meal)
        data = serializer.data
        
        assert isinstance(data['meal'], dict)
        assert 'id' in data['meal']
        assert 'user' in data['meal']
        assert 'meal_type' in data['meal']
        assert 'name' in data['meal']
        assert 'date_time' in data['meal']
        assert 'notes' in data['meal']
        assert 'items' in data['meal']


# =========================================================
# EDGE CASES TESTS
# =========================================================

@pytest.mark.django_db
class TestSerializerEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_meal_with_null_fields(self, test_profile):
        """Test meal with null optional fields."""
        meal = Meal.objects.create(
            user=test_profile,
            meal_type=Meal.MealType.BREAKFAST,
            name=None,
            notes=None
        )
        
        serializer = MealSerializer(meal)
        data = serializer.data
        
        assert data['name'] is None
        assert data['notes'] is None
    
    def test_goal_with_null_fields(self, test_profile):
        """Test goal with null optional fields."""
        goal = Goal.objects.create(
            user=test_profile,
            target_weight_kg=None,
            target_calories=None,
            consumed_calories=0.0,
            reset_frequency=Goal.ResetFrequency.NONE
        )
        
        serializer = GoalSerializer(goal)
        data = serializer.data
        
        assert data['target_weight_kg'] is None
        assert data['target_calories'] is None
    
    def test_meal_item_zero_quantity(self, test_meal, test_product):
        """Test meal item with zero quantity."""
        meal_item = MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=0.0
        )
        
        serializer = MealItemSerializer(meal_item)
        data = serializer.data
        
        assert data['quantity'] == 0.0
    
    def test_goal_nutrient_zero_amounts(self, test_goal, test_nutrient):
        """Test goal nutrient with zero amounts."""
        goal_nutrient = GoalNutrient.objects.create(
            goal=test_goal,
            nutrient=test_nutrient,
            target_amount=0.0,
            consumed_amount=0.0
        )
        
        serializer = GoalNutrientReadSerializer(goal_nutrient)
        data = serializer.data
        
        assert data['target_amount'] == 0.0
        assert data['consumed_amount'] == 0.0
    
    def test_meal_with_empty_items(self, test_meal):
        """Test meal with no items."""
        serializer = MealSerializer(test_meal)
        data = serializer.data
        
        assert data['items'] == []
    
    def test_serializer_field_validation(self, test_profile):
        """Test serializer field validation."""
        # Test invalid meal type
        data = {
            'user': test_profile.id,
            'meal_type': 'invalid_type',
            'name': 'Test Meal',
            'items': []
        }
        
        serializer = MealWriteSerializer(data=data)
        assert not serializer.is_valid()
        assert 'meal_type' in serializer.errors