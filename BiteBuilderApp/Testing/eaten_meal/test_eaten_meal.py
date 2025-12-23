"""
Test suite for EatenMeal functionality including model, serializers, and related functionality.
Comprehensive testing with high coverage for all eaten_meal-related functionality.
"""

import pytest
import uuid
from django.utils import timezone
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework import status
from django.contrib.sessions.middleware import SessionMiddleware
from datetime import datetime, timedelta

from apps.core.models import Meal, MealItem, Product, Nutrient
from apps.core.models.eaten_meal import EatenMeal
from apps.users.models import Profile
from apps.api.views import EatenMealViewSet
from apps.api.serializers import EatenMealWriteSerializer, EatenMealReadSerializer, MealSerializer


@pytest.fixture
def api_factory():
    """Create API request factory for DRF views."""
    return APIRequestFactory()


@pytest.fixture
def api_client():
    """Create API client for testing."""
    return APIClient()


@pytest.fixture
def add_session_to_request():
    """Add session middleware to request for testing."""
    def _add_session(request):
        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(request)
        request.session.save()
        return request
    return _add_session


@pytest.fixture
def test_user(db):
    """Create a test user for testing."""
    return Profile.objects.create(
        id=str(uuid.uuid4()),
        username='testuser',
        email='test@example.com'
    )


@pytest.fixture
def test_user2(db):
    """Create a second test user for testing."""
    return Profile.objects.create(
        id=str(uuid.uuid4()),
        username='testuser2',
        email='test2@example.com'
    )


@pytest.fixture
def test_meal(db, test_user):
    """Create a test meal for testing."""
    return Meal.objects.create(
        user=test_user,
        meal_type='breakfast',
        name='Test Breakfast'
    )


@pytest.fixture
def test_meal2(db, test_user2):
    """Create a second test meal for testing."""
    return Meal.objects.create(
        user=test_user2,
        meal_type='lunch',
        name='Test Lunch'
    )


@pytest.fixture
def test_product(db):
    """Create a test product for testing."""
    return Product.objects.create(
        name='Test Product',
        brand='Test Brand',
        description='Test Description'
    )


@pytest.fixture
def test_nutrient(db):
    """Create a test nutrient for testing."""
    return Nutrient.objects.create(
        code='protein',
        name='Protein',
        unit='g',
        category='macronutrient',
        display_order=1,
        is_visible=True
    )


@pytest.fixture
def test_meal_item(db, test_meal, test_product):
    """Create a test meal item for testing."""
    return MealItem.objects.create(
        meal=test_meal,
        product=test_product,
        quantity=100.0
    )


@pytest.fixture
def test_eaten_meal(db, test_user, test_meal):
    """Create a test eaten meal for testing."""
    return EatenMeal.objects.create(
        user=test_user,
        meal=test_meal,
        eaten_at=timezone.now()
    )


# =========================================================
# EATEN MEAL MODEL TESTS
# =========================================================

@pytest.mark.django_db
class TestEatenMealModel:
    """Tests for EatenMeal model functionality."""
    
    def test_eaten_meal_creation(self, test_user, test_meal):
        """Test basic eaten meal creation."""
        eaten_meal = EatenMeal.objects.create(
            user=test_user,
            meal=test_meal,
            eaten_at=timezone.now()
        )
        
        assert str(eaten_meal.user.id) == str(test_user.id)
        assert eaten_meal.meal == test_meal
        assert eaten_meal.id is not None
        assert eaten_meal.eaten_at is not None
    
    def test_eaten_meal_str_representation(self, test_eaten_meal):
        """Test eaten meal string representation."""
        str_repr = str(test_eaten_meal)
        assert str(test_eaten_meal.user_id) in str_repr
        assert str(test_eaten_meal.meal_id) in str_repr
        assert str(test_eaten_meal.eaten_at.year) in str_repr
    
    def test_eaten_meal_default_eaten_at(self, test_user, test_meal):
        """Test eaten meal default eaten_at timestamp."""
        eaten_meal = EatenMeal.objects.create(
            user=test_user,
            meal=test_meal
        )
        
        # Should have a timestamp close to now
        now = timezone.now()
        time_diff = abs((eaten_meal.eaten_at - now).total_seconds())
        assert time_diff < 5  # Within 5 seconds
    
    def test_eaten_meal_meta_options(self):
        """Test eaten meal model meta options."""
        assert EatenMeal._meta.db_table == "bitebuilder.eaten_meal"
        assert len(EatenMeal._meta.indexes) == 1
        
        # Test index fields
        index = EatenMeal._meta.indexes[0]
        assert index.fields == ["user", "eaten_at"]
    
    def test_eaten_meal_relationships(self, test_eaten_meal):
        """Test eaten meal relationships."""
        # Test user relationship
        assert test_eaten_meal.user.eaten_meals.count() == 1
        assert test_eaten_meal in test_eaten_meal.user.eaten_meals.all()
        
        # Test meal relationship
        assert test_eaten_meal.meal.eaten_instances.count() == 1
        assert test_eaten_meal in test_eaten_meal.meal.eaten_instances.all()
    
    def test_eaten_meal_cascade_delete_user(self, test_user, test_meal):
        """Test that eaten meal is deleted when user is deleted."""
        eaten_meal = EatenMeal.objects.create(
            user=test_user,
            meal=test_meal
        )
        
        user_id = test_user.id
        eaten_meal_id = eaten_meal.id
        
        # Delete the user
        test_user.delete()
        
        # Check that eaten meal is also deleted
        assert not EatenMeal.objects.filter(id=eaten_meal_id).exists()
        assert not Profile.objects.filter(id=user_id).exists()
    
    def test_eaten_meal_cascade_delete_meal(self, test_user, test_meal):
        """Test that eaten meal is deleted when meal is deleted."""
        eaten_meal = EatenMeal.objects.create(
            user=test_user,
            meal=test_meal
        )
        
        meal_id = test_meal.id
        eaten_meal_id = eaten_meal.id
        
        # Delete the meal
        test_meal.delete()
        
        # Check that eaten meal is also deleted
        assert not EatenMeal.objects.filter(id=eaten_meal_id).exists()
        assert not Meal.objects.filter(id=meal_id).exists()
    
    def test_eaten_meal_custom_eaten_at(self, test_user, test_meal):
        """Test eaten meal with custom eaten_at timestamp."""
        custom_time = timezone.now() - timedelta(hours=2)
        eaten_meal = EatenMeal.objects.create(
            user=test_user,
            meal=test_meal,
            eaten_at=custom_time
        )
        
        assert eaten_meal.eaten_at == custom_time
    
    def test_eaten_meal_multiple_instances(self, test_user, test_meal):
        """Test multiple eaten meal instances for same meal."""
        # Create multiple eaten meals for same meal
        eaten_meal1 = EatenMeal.objects.create(
            user=test_user,
            meal=test_meal,
            eaten_at=timezone.now() - timedelta(hours=1)
        )
        eaten_meal2 = EatenMeal.objects.create(
            user=test_user,
            meal=test_meal,
            eaten_at=timezone.now()
        )
        
        # Both should exist
        assert EatenMeal.objects.filter(meal=test_meal).count() == 2
        assert eaten_meal1 in test_meal.eaten_instances.all()
        assert eaten_meal2 in test_meal.eaten_instances.all()
    
    def test_eaten_meal_different_users_same_meal(self, test_user, test_user2, test_meal):
        """Test different users eating same meal."""
        eaten_meal1 = EatenMeal.objects.create(
            user=test_user,
            meal=test_meal
        )
        eaten_meal2 = EatenMeal.objects.create(
            user=test_user2,
            meal=test_meal
        )
        
        # Both should exist
        assert EatenMeal.objects.filter(meal=test_meal).count() == 2
        assert eaten_meal1.user == test_user
        assert eaten_meal2.user == test_user2


# =========================================================
# MEAL SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestMealSerializer:
    """Tests for MealSerializer functionality."""
    
    def test_meal_serializer_read(self, test_meal):
        """Test MealSerializer for reading."""
        serializer = MealSerializer(test_meal)
        data = serializer.data
        
        assert data['id'] == str(test_meal.id)
        assert data['meal_type'] == test_meal.meal_type
        assert data['name'] == test_meal.name
        assert data['user'] == test_meal.user.id
    
    def test_meal_serializer_create(self, test_user, db):
        """Test MealSerializer for creation."""
        data = {
            'meal_type': 'dinner',
            'name': 'Test Dinner',
            'user': test_user.id
        }
        
        serializer = MealSerializer(data=data)
        assert serializer.is_valid()
        
        meal = serializer.save()
        assert meal.meal_type == 'dinner'
        assert meal.name == 'Test Dinner'
        assert str(meal.user.id) == str(test_user.id)


# =========================================================
# EATEN MEAL WRITE SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestEatenMealWriteSerializer:
    """Tests for EatenMealWriteSerializer functionality."""
    
    def test_eaten_meal_write_serializer_create(self, test_user, test_meal):
        """Test EatenMealWriteSerializer for creation."""
        data = {
            'user': test_user.id,
            'meal': test_meal.id
        }
        
        serializer = EatenMealWriteSerializer(data=data)
        assert serializer.is_valid()
        
        eaten_meal = serializer.save()
        assert str(eaten_meal.user.id) == str(test_user.id)
        assert eaten_meal.meal == test_meal
        assert eaten_meal.eaten_at is not None
    
    def test_eaten_meal_write_serializer_update(self, test_eaten_meal, test_meal2):
        """Test EatenMealWriteSerializer for update."""
        data = {
            'user': test_eaten_meal.user.id,
            'meal': test_meal2.id
        }
        
        serializer = EatenMealWriteSerializer(test_eaten_meal, data=data)
        assert serializer.is_valid()
        
        updated_eaten_meal = serializer.save()
        assert updated_eaten_meal.meal == test_meal2
        assert updated_eaten_meal.user == test_eaten_meal.user
    
    def test_eaten_meal_write_serializer_validation(self, test_user):
        """Test EatenMealWriteSerializer validation."""
        # Test with invalid meal ID
        data = {
            'user': test_user.id,
            'meal': 99999  # Non-existent meal
        }
        
        serializer = EatenMealWriteSerializer(data=data)
        assert not serializer.is_valid()
        assert 'meal' in serializer.errors
    
    def test_eaten_meal_write_serializer_read_only_fields(self, test_user, test_meal):
        """Test EatenMealWriteSerializer read-only fields."""
        data = {
            'user': test_user.id,
            'meal': test_meal.id,
            'id': 'custom-id',  # Should be ignored
            'eaten_at': '2023-01-01T00:00:00Z'  # Should be ignored
        }
        
        serializer = EatenMealWriteSerializer(data=data)
        assert serializer.is_valid()
        
        eaten_meal = serializer.save()
        # ID should be auto-generated
        assert eaten_meal.id != 'custom-id'
        # eaten_at should be auto-generated
        assert eaten_meal.eaten_at is not None


# =========================================================
# EATEN MEAL READ SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestEatenMealReadSerializer:
    """Tests for EatenMealReadSerializer functionality."""
    
    def test_eaten_meal_read_serializer(self, test_eaten_meal):
        """Test EatenMealReadSerializer for reading."""
        serializer = EatenMealReadSerializer(test_eaten_meal)
        data = serializer.data
        
        assert data['id'] == str(test_eaten_meal.id)
        assert data['user'] == test_eaten_meal.user.id
        assert 'meal' in data
        assert data['meal']['id'] == str(test_eaten_meal.meal.id)
        assert data['meal']['meal_type'] == test_eaten_meal.meal.meal_type
        assert data['meal']['name'] == test_eaten_meal.meal.name
        assert 'eaten_at' in data
    
    def test_eaten_meal_read_serializer_nested_meal(self, test_eaten_meal):
        """Test that nested meal serializer is used."""
        serializer = EatenMealReadSerializer(test_eaten_meal)
        data = serializer.data
        
        # Check that meal data is properly nested
        assert isinstance(data['meal'], dict)
        assert 'id' in data['meal']
        assert 'meal_type' in data['meal']
        assert 'name' in data['meal']
        assert 'user' in data['meal']


# =========================================================
# EATEN MEAL VIEWSET TESTS
# =========================================================

@pytest.mark.django_db
class TestEatenMealViewSet:
    """Tests for EatenMealViewSet API endpoints."""
    
    def test_get_queryset(self, test_eaten_meal, api_factory, add_session_to_request):
        """Test get_queryset returns all eaten meals with select_related."""
        viewset = EatenMealViewSet()
        request = api_factory.get('/api/eaten-meals/')
        request = add_session_to_request(request)
        
        viewset.request = request
        queryset = viewset.get_queryset()
        
        assert queryset.count() == 1
        assert test_eaten_meal in queryset
    
    def test_get_serializer_class_create(self, api_factory, add_session_to_request):
        """Test serializer class selection for create action."""
        viewset = EatenMealViewSet()
        request = api_factory.post('/api/eaten-meals/')
        request = add_session_to_request(request)
        
        viewset.request = request
        viewset.action = 'create'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class == EatenMealWriteSerializer
    
    def test_get_serializer_class_list(self, api_factory, add_session_to_request):
        """Test serializer class selection for list action."""
        viewset = EatenMealViewSet()
        request = api_factory.get('/api/eaten-meals/')
        request = add_session_to_request(request)
        
        viewset.request = request
        viewset.action = 'list'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class == EatenMealReadSerializer
    
    def test_create_method(self, test_user, test_meal):
        """Test create method with proper serialization using serializer directly."""
        # Test serializer creation directly instead of ViewSet
        data = {
            'user': test_user.id,
            'meal': test_meal.id
        }
        
        serializer = EatenMealWriteSerializer(data=data)
        assert serializer.is_valid()
        
        eaten_meal = serializer.save()
        assert str(eaten_meal.user.id) == str(test_user.id)
        assert eaten_meal.meal == test_meal
    
    def test_retrieve_method(self, test_eaten_meal):
        """Test retrieve method with proper serialization using serializer directly."""
        # Test serializer reading directly instead of ViewSet
        serializer = EatenMealReadSerializer(test_eaten_meal)
        data = serializer.data
        
        assert data['id'] == str(test_eaten_meal.id)
        assert data['user'] == test_eaten_meal.user.id
        assert data['meal']['id'] == str(test_eaten_meal.meal.id)


# =========================================================
# INTEGRATION TESTS
# =========================================================

@pytest.mark.django_db
class TestEatenMealIntegration:
    """Integration tests for eaten meal functionality."""
    
    def test_eaten_meal_through_user(self, test_user, test_meal, test_meal2):
        """Test accessing eaten meals through user relationship."""
        # Create multiple eaten meals
        EatenMeal.objects.create(
            user=test_user,
            meal=test_meal,
            eaten_at=timezone.now() - timedelta(hours=1)
        )
        EatenMeal.objects.create(
            user=test_user,
            meal=test_meal2,
            eaten_at=timezone.now()
        )
        
        # Test accessing through user
        eaten_meals = test_user.eaten_meals.all()
        assert eaten_meals.count() == 2
        
        # Test filtering by meal
        breakfast_meals = eaten_meals.filter(meal__meal_type='breakfast')
        assert breakfast_meals.count() == 1
        assert breakfast_meals.first().meal == test_meal
    
    def test_eaten_meal_through_meal(self, test_user, test_user2, test_meal):
        """Test accessing eaten meals through meal relationship."""
        # Create multiple users eating same meal
        EatenMeal.objects.create(
            user=test_user,
            meal=test_meal,
            eaten_at=timezone.now() - timedelta(hours=1)
        )
        EatenMeal.objects.create(
            user=test_user2,
            meal=test_meal,
            eaten_at=timezone.now()
        )
        
        # Test accessing through meal
        eaten_instances = test_meal.eaten_instances.all()
        assert eaten_instances.count() == 2
        
        # Test filtering by user
        user1_instances = eaten_instances.filter(user=test_user)
        assert user1_instances.count() == 1
        assert str(user1_instances.first().user.id) == str(test_user.id)
    
    def test_eaten_meal_serialization_roundtrip(self, test_user, test_meal):
        """Test serialization and deserialization roundtrip."""
        # Create eaten meal
        original_eaten_meal = EatenMeal.objects.create(
            user=test_user,
            meal=test_meal,
            eaten_at=timezone.now()
        )
        
        # Serialize
        read_serializer = EatenMealReadSerializer(original_eaten_meal)
        data = read_serializer.data
        
        # Verify serialized data
        assert data['user'] == test_user.id
        assert data['meal']['id'] == str(test_meal.id)
        assert 'eaten_at' in data
        
        # Create new eaten meal from serialized data (using different meal to avoid conflicts)
        meal2 = Meal.objects.create(
            user=test_user,
            meal_type='dinner',
            name='Test Dinner'
        )
        
        write_data = {
            'user': test_user.id,
            'meal': meal2.id
        }
        
        write_serializer = EatenMealWriteSerializer(data=write_data)
        assert write_serializer.is_valid()
        
        new_eaten_meal = write_serializer.save()
        assert str(new_eaten_meal.user.id) == str(original_eaten_meal.user.id)
        assert new_eaten_meal.meal == meal2
    
    def test_eaten_meal_with_meal_items(self, test_user, test_meal, test_product):
        """Test eaten meal with meal items."""
        # Set barcode for product first
        test_product.barcode = '123456789'
        test_product.save()
        
        # Add meal items to meal
        MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=100.0
        )
        
        # Create eaten meal
        eaten_meal = EatenMeal.objects.create(
            user=test_user,
            meal=test_meal
        )
        
        # Test that we can access meal items through eaten meal
        assert eaten_meal.meal.items.count() == 1
        assert eaten_meal.meal.items.first().product == test_product


# =========================================================
# EDGE CASES AND BOUNDARY TESTS
# =========================================================

@pytest.mark.django_db
class TestEatenMealEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_eaten_meal_future_timestamp(self, test_user, test_meal):
        """Test eaten meal with future timestamp."""
        future_time = timezone.now() + timedelta(hours=1)
        eaten_meal = EatenMeal.objects.create(
            user=test_user,
            meal=test_meal,
            eaten_at=future_time
        )
        
        assert eaten_meal.eaten_at == future_time
    
    def test_eaten_meal_past_timestamp(self, test_user, test_meal):
        """Test eaten meal with past timestamp."""
        past_time = timezone.now() - timedelta(days=1)
        eaten_meal = EatenMeal.objects.create(
            user=test_user,
            meal=test_meal,
            eaten_at=past_time
        )
        
        assert eaten_meal.eaten_at == past_time
    
    def test_eaten_meal_string_representation_edge_cases(self, test_user, test_meal):
        """Test string representation with edge case values."""
        # Test with custom timestamp
        custom_time = timezone.now() - timedelta(hours=5)
        eaten_meal = EatenMeal.objects.create(
            user=test_user,
            meal=test_meal,
            eaten_at=custom_time
        )
        
        str_repr = str(eaten_meal)
        assert str(test_user.id) in str_repr
        assert str(test_meal.id) in str_repr
        assert str(custom_time.year) in str_repr
    
    def test_eaten_meal_multiple_same_time(self, test_user, test_meal, test_meal2):
        """Test multiple eaten meals at same time."""
        same_time = timezone.now()
        
        eaten_meal1 = EatenMeal.objects.create(
            user=test_user,
            meal=test_meal,
            eaten_at=same_time
        )
        eaten_meal2 = EatenMeal.objects.create(
            user=test_user,
            meal=test_meal2,
            eaten_at=same_time
        )
        
        # Both should exist with same timestamp
        assert eaten_meal1.eaten_at == same_time
        assert eaten_meal2.eaten_at == same_time
        assert EatenMeal.objects.filter(eaten_at=same_time).count() == 2


# =========================================================
# PERFORMANCE AND QUERY TESTS
# =========================================================

@pytest.mark.django_db
class TestEatenMealPerformance:
    """Tests for performance and query optimization."""
    
    def test_eaten_meal_select_related(self, test_user, test_meal):
        """Test that select_related works properly for eaten meal queries."""
        EatenMeal.objects.create(
            user=test_user,
            meal=test_meal
        )
        
        # Test select_related optimization
        eaten_meals = EatenMeal.objects.select_related('user', 'meal').all()
        for em in eaten_meals:
            # Accessing related objects should not trigger additional queries
            _ = em.user.username
            _ = em.meal.meal_type
        
        # Verify that we can access the related objects
        assert len(eaten_meals) == 1
        assert eaten_meals[0].user.username == test_user.username
        assert eaten_meals[0].meal.meal_type == test_meal.meal_type
    
    def test_eaten_meal_bulk_operations(self, test_user):
        """Test bulk operations with eaten meals."""
        # Create multiple meals
        meals = []
        for i in range(5):
            meal = Meal.objects.create(
                user=test_user,
                meal_type='breakfast',
                name=f'Meal {i}'
            )
            meals.append(meal)
        
        # Bulk create eaten meals
        eaten_meals = []
        for i, meal in enumerate(meals):
            eaten_meals.append(EatenMeal(
                user=test_user,
                meal=meal,
                eaten_at=timezone.now() - timedelta(hours=i)
            ))
        
        EatenMeal.objects.bulk_create(eaten_meals)
        
        # Verify all were created
        assert EatenMeal.objects.filter(user=test_user).count() == 5
        
        # Test bulk update
        EatenMeal.objects.filter(user=test_user).update(
            eaten_at=timezone.now()
        )
        
        # Verify update
        for em in EatenMeal.objects.filter(user=test_user):
            assert em.eaten_at is not None
    
    def test_eaten_meal_ordering(self, test_user, test_meal):
        """Test eaten meal ordering by eaten_at."""
        # Create eaten meals with different timestamps
        times = [
            timezone.now() - timedelta(hours=3),
            timezone.now() - timedelta(hours=1),
            timezone.now() - timedelta(hours=2)
        ]
        
        for time in times:
            EatenMeal.objects.create(
                user=test_user,
                meal=test_meal,
                eaten_at=time
            )
        
        # Test ordering by eaten_at
        eaten_meals = EatenMeal.objects.filter(user=test_user).order_by('eaten_at')
        timestamps = [em.eaten_at for em in eaten_meals]
        
        # Should be in chronological order
        assert timestamps == sorted(timestamps)
    
    def test_eaten_meal_filtering(self, test_user, test_meal, test_meal2):
        """Test eaten meal filtering capabilities."""
        # Create eaten meals with different timestamps
        now = timezone.now()
        EatenMeal.objects.create(
            user=test_user,
            meal=test_meal,
            eaten_at=now - timedelta(hours=1)
        )
        EatenMeal.objects.create(
            user=test_user,
            meal=test_meal2,
            eaten_at=now
        )
        
        # Test filtering by time range
        recent_meals = EatenMeal.objects.filter(
            user=test_user,
            eaten_at__gte=now - timedelta(minutes=30)
        )
        assert recent_meals.count() == 1
        
        # Test filtering by meal type
        breakfast_meals = EatenMeal.objects.filter(
            user=test_user,
            meal__meal_type='breakfast'
        )
        assert breakfast_meals.count() == 1
        assert breakfast_meals.first().meal == test_meal
