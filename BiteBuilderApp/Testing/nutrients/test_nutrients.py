"""
Test suite for Nutrients functionality including Nutrient model and API endpoints.
Comprehensive testing with high coverage for all nutrient-related functionality.
"""

import pytest
import uuid
from django.utils import timezone
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework import status
from django.contrib.sessions.middleware import SessionMiddleware

from apps.core.models import Nutrient, Meal, MealItem, Goal, GoalNutrient
from apps.core.models.eaten_meal import EatenMeal
from apps.users.models import Profile
from apps.api.views import NutrientViewSet, MealViewSet, MealItemViewSet, ProfileViewSet, GoalViewSet, GoalNutrientViewSet, EatenMealViewSet
from apps.api.serializers import NutrientSerializer, MealSerializer, MealWriteSerializer, MealItemSerializer, MealItemWriteSerializer, ProfileSerializer, GoalSerializer, GoalNutrientWriteSerializer, GoalNutrientReadSerializer, EatenMealWriteSerializer, EatenMealReadSerializer


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
def test_nutrient(db):
    """Create a test nutrient for testing."""
    return Nutrient.objects.create(
        code='energy_kj',
        name='Energy (kJ)',
        unit='kJ',
        category='macronutrient',
        display_order=1,
        is_visible=True
    )


@pytest.fixture
def test_nutrient_vitamin(db):
    """Create a test vitamin nutrient."""
    return Nutrient.objects.create(
        code='vitamin_c',
        name='Vitamin C',
        unit='mg',
        category='vitamin',
        display_order=2,
        is_visible=True
    )


@pytest.fixture
def test_nutrient_mineral(db):
    """Create a test mineral nutrient."""
    return Nutrient.objects.create(
        code='calcium',
        name='Calcium',
        unit='mg',
        category='mineral',
        display_order=3,
        is_visible=True
    )


# =========================================================
# NUTRIENT MODEL TESTS
# =========================================================

@pytest.mark.django_db
class TestNutrientModel:
    """Tests for Nutrient model functionality."""
    
    def test_nutrient_creation(self, db):
        """Test basic nutrient creation."""
        nutrient = Nutrient.objects.create(
            code='protein',
            name='Protein',
            unit='g',
            category='macronutrient',
            display_order=1,
            is_visible=True
        )
        
        assert nutrient.code == 'protein'
        assert nutrient.name == 'Protein'
        assert nutrient.unit == 'g'
        assert nutrient.category == 'macronutrient'
        assert nutrient.display_order == 1
        assert nutrient.is_visible is True
        assert nutrient.id is not None
    
    def test_nutrient_str_representation(self, test_nutrient):
        """Test nutrient string representation."""
        str_repr = str(test_nutrient)
        assert test_nutrient.name in str_repr
        assert test_nutrient.unit in str_repr
    
    def test_nutrient_choices(self):
        """Test nutrient unit and category choices."""
        unit_choices = Nutrient.UNIT_CHOICES
        assert ('g', 'g') in unit_choices
        assert ('mg', 'mg') in unit_choices
        assert ('kJ', 'kJ') in unit_choices
        assert ('kcal', 'kcal') in unit_choices
        
        category_choices = Nutrient._meta.get_field('category').choices
        assert ('macronutrient', 'Macronutrient') in category_choices
        assert ('vitamin', 'Vitamin') in category_choices
        assert ('mineral', 'Mineral') in category_choices
    
    def test_nutrient_save_lowercase_code(self, db):
        """Test that nutrient code is converted to lowercase on save."""
        nutrient = Nutrient.objects.create(
            code='PROTEIN',
            name='Protein',
            unit='g'
        )
        
        assert nutrient.code == 'protein'
    
    def test_nutrient_meta_options(self):
        """Test nutrient model meta options."""
        assert Nutrient._meta.db_table == "bitebuilder.nutrients"
        assert len(Nutrient._meta.indexes) == 2
        
        # Test ordering
        ordering = Nutrient._meta.ordering
        assert 'display_order' in ordering
        assert 'name' in ordering
    
    def test_nutrient_unique_constraints(self, db):
        """Test nutrient unique constraints."""
        # Create first nutrient
        Nutrient.objects.create(
            code='energy_kj',
            name='Energy (kJ)',
            unit='kJ'
        )
        
        # Try to create duplicate code
        with pytest.raises(Exception):  # Should raise IntegrityError
            Nutrient.objects.create(
                code='energy_kj',
                name='Energy (kcal)',
                unit='kcal'
            )
        
        # Try to create duplicate name
        with pytest.raises(Exception):  # Should raise IntegrityError
            Nutrient.objects.create(
                code='energy_kcal',
                name='Energy (kJ)',
                unit='kcal'
            )


# =========================================================
# NUTRIENT SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestNutrientSerializer:
    """Tests for Nutrient serializers."""
    
    def test_nutrient_serializer_read(self, test_nutrient):
        """Test NutrientSerializer for reading."""
        serializer = NutrientSerializer(test_nutrient)
        data = serializer.data
        
        assert data['id'] == str(test_nutrient.id)
        assert data['code'] == test_nutrient.code
        assert data['name'] == test_nutrient.name
        assert data['unit'] == test_nutrient.unit
        assert data['category'] == test_nutrient.category
        assert data['display_order'] == test_nutrient.display_order
        assert data['is_visible'] == test_nutrient.is_visible
    
    def test_nutrient_serializer_create(self, db):
        """Test NutrientSerializer for creation."""
        data = {
            'code': 'fiber',
            'name': 'Dietary Fiber',
            'unit': 'g',
            'category': 'macronutrient',
            'display_order': 5,
            'is_visible': True
        }
        
        serializer = NutrientSerializer(data=data)
        assert serializer.is_valid()
        
        nutrient = serializer.save()
        assert nutrient.code == 'fiber'
        assert nutrient.name == 'Dietary Fiber'
        assert nutrient.unit == 'g'
        assert nutrient.category == 'macronutrient'
    
    def test_nutrient_serializer_validation(self, db):
        """Test NutrientSerializer validation."""
        # Test invalid unit choice
        data = {
            'code': 'test',
            'name': 'Test Nutrient',
            'unit': 'invalid_unit',
            'category': 'macronutrient'
        }
        
        serializer = NutrientSerializer(data=data)
        assert not serializer.is_valid()
        assert 'unit' in serializer.errors
        
        # Test invalid category choice
        data = {
            'code': 'test',
            'name': 'Test Nutrient',
            'unit': 'g',
            'category': 'invalid_category'
        }
        
        serializer = NutrientSerializer(data=data)
        assert not serializer.is_valid()
        assert 'category' in serializer.errors


# =========================================================
# NUTRIENT VIEWSET TESTS
# =========================================================

@pytest.mark.django_db
class TestNutrientViewSet:
    """Tests for NutrientViewSet API endpoints."""
    
    def test_get_queryset(self, test_nutrient, test_nutrient_vitamin, api_factory, add_session_to_request):
        """Test get_queryset returns all nutrients."""
        viewset = NutrientViewSet()
        request = api_factory.get('/api/nutrients/')
        request = add_session_to_request(request)
        
        viewset.request = request
        queryset = viewset.get_queryset()
        
        assert queryset.count() == 2
        assert test_nutrient in queryset
        assert test_nutrient_vitamin in queryset
    
    def test_get_serializer_class(self, api_factory, add_session_to_request):
        """Test serializer class selection."""
        viewset = NutrientViewSet()
        request = api_factory.get('/api/nutrients/')
        request = add_session_to_request(request)
        
        viewset.request = request
        serializer_class = viewset.get_serializer_class()
        assert serializer_class == NutrientSerializer


# =========================================================
# API ENDPOINT TESTS
# =========================================================

@pytest.mark.django_db
class TestNutrientAPIEndpoints:
    """Tests for nutrient-related API endpoints."""
    
    def test_nutrients_list_endpoint(self, api_client, test_nutrient, test_nutrient_vitamin):
        """Test GET /api/nutrients/ endpoint."""
        response = api_client.get('/api/nutrients/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        
        # Check that both nutrients are in response
        nutrient_ids = [item['id'] for item in response.data]
        assert str(test_nutrient.id) in nutrient_ids
        assert str(test_nutrient_vitamin.id) in nutrient_ids
    
    def test_nutrients_create_endpoint(self, api_client):
        """Test POST /api/nutrients/ endpoint."""
        data = {
            'code': 'sodium',
            'name': 'Sodium',
            'unit': 'mg',
            'category': 'mineral',
            'display_order': 10,
            'is_visible': True
        }
        
        response = api_client.post('/api/nutrients/', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['code'] == 'sodium'
        assert response.data['name'] == 'Sodium'
        assert response.data['unit'] == 'mg'
        assert response.data['category'] == 'mineral'
    
    def test_nutrients_detail_endpoint(self, api_client, test_nutrient):
        """Test GET /api/nutrients/{id}/ endpoint."""
        response = api_client.get(f'/api/nutrients/{test_nutrient.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(test_nutrient.id)
        assert response.data['code'] == test_nutrient.code
        assert response.data['name'] == test_nutrient.name
    
    def test_nutrients_update_endpoint(self, api_client, test_nutrient):
        """Test PUT /api/nutrients/{id}/ endpoint."""
        data = {
            'code': 'energy_kj',
            'name': 'Energy (kJ) - Updated',
            'unit': 'kJ',
            'category': 'macronutrient',
            'display_order': 1,
            'is_visible': False
        }
        
        response = api_client.put(f'/api/nutrients/{test_nutrient.id}/', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Energy (kJ) - Updated'
        assert response.data['is_visible'] is False
    
    def test_nutrients_delete_endpoint(self, api_client, test_nutrient):
        """Test DELETE /api/nutrients/{id}/ endpoint."""
        response = api_client.delete(f'/api/nutrients/{test_nutrient.id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Nutrient.objects.filter(id=test_nutrient.id).exists()


# =========================================================
# ERROR HANDLING TESTS
# =========================================================

@pytest.mark.django_db
class TestNutrientErrorHandling:
    """Tests for error handling in nutrient functionality."""
    
    def test_nutrient_creation_invalid_data(self, api_client):
        """Test nutrient creation with invalid data."""
        data = {
            'code': 'test',
            'name': 'Test Nutrient',
            'unit': 'invalid_unit',  # Invalid choice
            'category': 'macronutrient'
        }
        
        response = api_client.post('/api/nutrients/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'unit' in response.data
    
    def test_nutrient_creation_duplicate_code(self, api_client, test_nutrient):
        """Test nutrient creation with duplicate code."""
        data = {
            'code': test_nutrient.code,  # Duplicate code
            'name': 'Different Name',
            'unit': 'g',
            'category': 'macronutrient'
        }
        
        response = api_client.post('/api/nutrients/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'code' in response.data
    
    def test_nutrient_access_nonexistent(self, api_client):
        """Test accessing non-existent nutrient."""
        fake_id = str(uuid.uuid4())
        response = api_client.get(f'/api/nutrients/{fake_id}/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


# =========================================================
# INTEGRATION TESTS
# =========================================================

@pytest.mark.django_db
class TestNutrientIntegration:
    """Integration tests for nutrient functionality."""
    
    def test_nutrient_ordering(self, api_client):
        """Test that nutrients are ordered by display_order and name."""
        # Create nutrients with different display orders
        nutrient1 = Nutrient.objects.create(
            code='z_nutrient',
            name='Z Nutrient',
            unit='g',
            display_order=3
        )
        nutrient2 = Nutrient.objects.create(
            code='a_nutrient',
            name='A Nutrient',
            unit='g',
            display_order=1
        )
        nutrient3 = Nutrient.objects.create(
            code='m_nutrient',
            name='M Nutrient',
            unit='g',
            display_order=2
        )
        
        response = api_client.get('/api/nutrients/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        
        # Should be ordered by display_order, then by name
        names = [item['name'] for item in response.data]
        assert names[0] == 'A Nutrient'  # display_order=1
        assert names[1] == 'M Nutrient'  # display_order=2
        assert names[2] == 'Z Nutrient'  # display_order=3
    
    def test_nutrient_filtering_by_category(self, api_client, test_nutrient, test_nutrient_vitamin, test_nutrient_mineral):
        """Test filtering nutrients by category."""
        # Test macronutrient filtering
        response = api_client.get('/api/nutrients/?category=macronutrient')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['category'] == 'macronutrient'
        
        # Test vitamin filtering
        response = api_client.get('/api/nutrients/?category=vitamin')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['category'] == 'vitamin'
        
        # Test mineral filtering
        response = api_client.get('/api/nutrients/?category=mineral')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['category'] == 'mineral'
    
    def test_nutrient_visibility_filtering(self, api_client):
        """Test filtering nutrients by visibility."""
        # Create visible and invisible nutrients
        visible_nutrient = Nutrient.objects.create(
            code='visible',
            name='Visible Nutrient',
            unit='g',
            is_visible=True
        )
        invisible_nutrient = Nutrient.objects.create(
            code='invisible',
            name='Invisible Nutrient',
            unit='g',
            is_visible=False
        )
        
        # Test getting all nutrients
        response = api_client.get('/api/nutrients/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        
        # Test filtering visible nutrients
        response = api_client.get('/api/nutrients/?is_visible=true')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['is_visible'] is True
        
        # Test filtering invisible nutrients
        response = api_client.get('/api/nutrients/?is_visible=false')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['is_visible'] is False


# =========================================================
# EDGE CASES AND BOUNDARY TESTS
# =========================================================

@pytest.mark.django_db
class TestNutrientEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_nutrient_with_max_length_fields(self, api_client):
        """Test nutrient with maximum length fields."""
        data = {
            'code': 'a' * 50,  # Max length for code
            'name': 'A' * 100,  # Max length for name
            'unit': 'g',
            'category': 'macronutrient'
        }
        
        response = api_client.post('/api/nutrients/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['code'] == 'a' * 50
        assert response.data['name'] == 'A' * 100
    
    def test_nutrient_with_special_characters(self, api_client):
        """Test nutrient with special characters in name."""
        data = {
            'code': 'special_chars',
            'name': 'Nutrient with émojis 🥗 and spëcial chars',
            'unit': 'g',
            'category': 'macronutrient'
        }
        
        response = api_client.post('/api/nutrients/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'émojis' in response.data['name']
    
    def test_nutrient_with_zero_display_order(self, api_client):
        """Test nutrient with zero display order."""
        data = {
            'code': 'zero_order',
            'name': 'Zero Order Nutrient',
            'unit': 'g',
            'display_order': 0
        }
        
        response = api_client.post('/api/nutrients/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['display_order'] == 0
    
    def test_nutrient_with_null_category(self, api_client):
        """Test nutrient with null category."""
        data = {
            'code': 'no_category',
            'name': 'No Category Nutrient',
            'unit': 'g',
            'category': None
        }
        
        response = api_client.post('/api/nutrients/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['category'] is None
    
    def test_nutrient_code_trimming(self, api_client):
        """Test that nutrient code is trimmed of whitespace."""
        data = {
            'code': '  trimmed_code  ',
            'name': 'Trimmed Code Nutrient',
            'unit': 'g'
        }
        
        response = api_client.post('/api/nutrients/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['code'] == 'trimmed_code'  # Should be trimmed and lowercase


# =========================================================
# ADDITIONAL VIEWSET TESTS FOR COVERAGE
# =========================================================

@pytest.mark.django_db
class TestAdditionalViewSets:
    """Tests for other ViewSets to improve coverage."""
    
    def test_meal_viewset_get_serializer_class(self, api_factory, add_session_to_request):
        """Test MealViewSet serializer class selection."""
        viewset = MealViewSet()
        request = api_factory.get('/api/meals/')
        request = add_session_to_request(request)
        
        viewset.request = request
        viewset.action = 'list'
        serializer_class = viewset.get_serializer_class()
        assert serializer_class == MealSerializer
        
        viewset.action = 'create'
        serializer_class = viewset.get_serializer_class()
        assert serializer_class == MealWriteSerializer
    
    def test_meal_item_viewset_get_serializer_class(self, api_factory, add_session_to_request):
        """Test MealItemViewSet serializer class selection."""
        viewset = MealItemViewSet()
        request = api_factory.get('/api/meal-items/')
        request = add_session_to_request(request)
        
        viewset.request = request
        viewset.action = 'list'
        serializer_class = viewset.get_serializer_class()
        assert serializer_class == MealItemSerializer
        
        viewset.action = 'create'
        serializer_class = viewset.get_serializer_class()
        assert serializer_class == MealItemWriteSerializer
    
    def test_profile_viewset_basic(self, api_factory, add_session_to_request):
        """Test ProfileViewSet basic functionality."""
        viewset = ProfileViewSet()
        request = api_factory.get('/api/profile/')
        request = add_session_to_request(request)
        
        viewset.request = request
        queryset = viewset.get_queryset()
        assert queryset.count() == 0  # No profiles created yet
    
    def test_goal_viewset_get_queryset(self, api_factory, add_session_to_request):
        """Test GoalViewSet queryset filtering."""
        viewset = GoalViewSet()
        request = api_factory.get('/api/goals/?user=test-user-id')
        request = add_session_to_request(request)
        
        viewset.request = request
        queryset = viewset.get_queryset()
        assert queryset.count() == 0  # No goals created yet
    
    def test_goal_nutrient_viewset_get_serializer_class(self, api_factory, add_session_to_request):
        """Test GoalNutrientViewSet serializer class selection."""
        viewset = GoalNutrientViewSet()
        request = api_factory.get('/api/goal-nutrients/')
        request = add_session_to_request(request)
        
        viewset.request = request
        viewset.action = 'list'
        serializer_class = viewset.get_serializer_class()
        assert serializer_class == GoalNutrientReadSerializer
        
        viewset.action = 'create'
        serializer_class = viewset.get_serializer_class()
        assert serializer_class == GoalNutrientWriteSerializer
    
    def test_eaten_meal_viewset_get_serializer_class(self, api_factory, add_session_to_request):
        """Test EatenMealViewSet serializer class selection."""
        viewset = EatenMealViewSet()
        request = api_factory.get('/api/eaten-meals/')
        request = add_session_to_request(request)
        
        viewset.request = request
        viewset.action = 'list'
        serializer_class = viewset.get_serializer_class()
        assert serializer_class == EatenMealReadSerializer
        
        viewset.action = 'create'
        serializer_class = viewset.get_serializer_class()
        assert serializer_class == EatenMealWriteSerializer


# =========================================================
# ADDITIONAL SERIALIZER TESTS FOR COVERAGE
# =========================================================

@pytest.mark.django_db
class TestAdditionalSerializers:
    """Tests for other serializers to improve coverage."""
    
    def test_profile_serializer(self, db):
        """Test ProfileSerializer."""
        profile = Profile.objects.create(
            id=str(uuid.uuid4()),
            username='testuser',
            email='test@example.com'
        )
        
        serializer = ProfileSerializer(profile)
        data = serializer.data
        
        assert data['id'] == str(profile.id)
        assert data['username'] == profile.username
        assert data['email'] == profile.email
    
    def test_goal_serializer(self, db):
        """Test GoalSerializer."""
        profile = Profile.objects.create(
            id=str(uuid.uuid4()),
            username='testuser',
            email='test@example.com'
        )
        
        goal = Goal.objects.create(
            user=profile,
            target_weight_kg=70.0,
            target_calories=2000,
            consumed_calories=1500.0
        )
        
        serializer = GoalSerializer(goal)
        data = serializer.data
        
        assert data['id'] == str(goal.id)
        assert data['target_weight_kg'] == goal.target_weight_kg
        assert data['target_calories'] == goal.target_calories
        assert data['consumed_calories'] == goal.consumed_calories
    
    def test_goal_nutrient_write_serializer(self, db):
        """Test GoalNutrientWriteSerializer."""
        profile = Profile.objects.create(
            id=str(uuid.uuid4()),
            username='testuser',
            email='test@example.com'
        )
        
        goal = Goal.objects.create(user=profile)
        nutrient = Nutrient.objects.create(
            code='protein',
            name='Protein',
            unit='g'
        )
        
        data = {
            'goal': goal.id,
            'nutrient': nutrient.id
        }
        
        serializer = GoalNutrientWriteSerializer(data=data)
        assert serializer.is_valid()
        
        goal_nutrient = serializer.save()
        assert goal_nutrient.goal == goal
        assert goal_nutrient.nutrient == nutrient
    
    def test_goal_nutrient_read_serializer(self, db):
        """Test GoalNutrientReadSerializer."""
        profile = Profile.objects.create(
            id=str(uuid.uuid4()),
            username='testuser',
            email='test@example.com'
        )
        
        goal = Goal.objects.create(user=profile)
        nutrient = Nutrient.objects.create(
            code='protein',
            name='Protein',
            unit='g'
        )
        
        goal_nutrient = GoalNutrient.objects.create(
            goal=goal,
            nutrient=nutrient
        )
        
        serializer = GoalNutrientReadSerializer(goal_nutrient)
        data = serializer.data
        
        assert data['id'] == str(goal_nutrient.id)
        assert data['goal'] == goal.id
        assert 'nutrient' in data
        assert data['nutrient']['name'] == nutrient.name
    
    def test_eaten_meal_write_serializer(self, db):
        """Test EatenMealWriteSerializer."""
        profile = Profile.objects.create(
            id=str(uuid.uuid4()),
            username='testuser',
            email='test@example.com'
        )
        
        meal = Meal.objects.create(
            user=profile,
            meal_type='breakfast',
            name='Test Breakfast'
        )
        
        data = {
            'user': profile.id,
            'meal': meal.id
        }
        
        serializer = EatenMealWriteSerializer(data=data)
        assert serializer.is_valid()
        
        eaten_meal = serializer.save()
        assert eaten_meal.user == profile
        assert eaten_meal.meal == meal
    
    def test_eaten_meal_read_serializer(self, db):
        """Test EatenMealReadSerializer."""
        profile = Profile.objects.create(
            id=str(uuid.uuid4()),
            username='testuser',
            email='test@example.com'
        )
        
        meal = Meal.objects.create(
            user=profile,
            meal_type='breakfast',
            name='Test Breakfast'
        )
        
        eaten_meal = EatenMeal.objects.create(
            user=profile,
            meal=meal
        )
        
        serializer = EatenMealReadSerializer(eaten_meal)
        data = serializer.data
        
        assert data['id'] == str(eaten_meal.id)
        assert data['user'] == profile.id
        assert 'meal' in data
        assert data['meal']['id'] == str(meal.id)
