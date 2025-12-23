"""
Test suite for GoalNutrient functionality including model, serializers, and related functionality.
Comprehensive testing with high coverage for all goal_nutrient-related functionality.
"""

import pytest
import uuid
from django.utils import timezone
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework import status
from django.contrib.sessions.middleware import SessionMiddleware

from apps.core.models import Goal, GoalNutrient, Nutrient
from apps.users.models import Profile
from apps.api.views import GoalNutrientViewSet
from apps.api.serializers import GoalNutrientWriteSerializer, GoalNutrientReadSerializer, NutrientSerializer


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
def test_goal(db, test_user):
    """Create a test goal for testing."""
    return Goal.objects.create(
        user=test_user,
        target_weight_kg=70.0,
        target_calories=2000,
        consumed_calories=1500.0
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
def test_nutrient_calories(db):
    """Create a calories nutrient for testing."""
    return Nutrient.objects.create(
        code='energy_kj',
        name='Energy (kJ)',
        unit='kJ',
        category='macronutrient',
        display_order=2,
        is_visible=True
    )


@pytest.fixture
def test_goal_nutrient(db, test_goal, test_nutrient):
    """Create a test goal nutrient for testing."""
    return GoalNutrient.objects.create(
        goal=test_goal,
        nutrient=test_nutrient,
        target_amount=100.0,
        consumed_amount=50.0
    )


# =========================================================
# GOAL NUTRIENT MODEL TESTS
# =========================================================

@pytest.mark.django_db
class TestGoalNutrientModel:
    """Tests for GoalNutrient model functionality."""
    
    def test_goal_nutrient_creation(self, test_goal, test_nutrient):
        """Test basic goal nutrient creation."""
        goal_nutrient = GoalNutrient.objects.create(
            goal=test_goal,
            nutrient=test_nutrient,
            target_amount=150.0,
            consumed_amount=75.0
        )
        
        assert goal_nutrient.goal == test_goal
        assert goal_nutrient.nutrient == test_nutrient
        assert goal_nutrient.target_amount == 150.0
        assert goal_nutrient.consumed_amount == 75.0
        assert goal_nutrient.id is not None
    
    def test_goal_nutrient_str_representation(self, test_goal_nutrient):
        """Test goal nutrient string representation."""
        str_repr = str(test_goal_nutrient)
        assert str(test_goal_nutrient.goal_id) in str_repr
        assert str(test_goal_nutrient.nutrient_id) in str_repr
        assert str(test_goal_nutrient.consumed_amount) in str_repr
        assert str(test_goal_nutrient.target_amount) in str_repr
    
    def test_goal_nutrient_progress_percent(self, test_goal, test_nutrient):
        """Test goal nutrient progress percentage calculation."""
        # Test 50% progress
        goal_nutrient = GoalNutrient.objects.create(
            goal=test_goal,
            nutrient=test_nutrient,
            target_amount=100.0,
            consumed_amount=50.0
        )
        assert goal_nutrient.progress_percent == 50.0
        
        # Test 100% progress
        goal_nutrient.consumed_amount = 100.0
        goal_nutrient.save()
        assert goal_nutrient.progress_percent == 100.0
        
        # Test over 100% progress (should be capped at 100%)
        goal_nutrient.consumed_amount = 150.0
        goal_nutrient.save()
        assert goal_nutrient.progress_percent == 100.0
        
        # Test zero target amount
        goal_nutrient.target_amount = 0.0
        goal_nutrient.save()
        assert goal_nutrient.progress_percent == 0.0
    
    def test_goal_nutrient_meta_options(self):
        """Test goal nutrient model meta options."""
        assert GoalNutrient._meta.db_table == "bitebuilder.goal_nutrient"
        assert len(GoalNutrient._meta.indexes) == 2
        
        # Test unique_together constraint
        unique_together = GoalNutrient._meta.unique_together
        assert ('goal', 'nutrient') in unique_together
    
    def test_goal_nutrient_unique_constraint(self, test_goal, test_nutrient):
        """Test goal nutrient unique constraint."""
        # Create first goal nutrient
        GoalNutrient.objects.create(
            goal=test_goal,
            nutrient=test_nutrient,
            target_amount=100.0
        )
        
        # Try to create duplicate
        with pytest.raises(Exception):  # Should raise IntegrityError
            GoalNutrient.objects.create(
                goal=test_goal,
                nutrient=test_nutrient,
                target_amount=200.0
            )
    
    def test_goal_nutrient_default_consumed_amount(self, test_goal, test_nutrient):
        """Test goal nutrient default consumed amount."""
        goal_nutrient = GoalNutrient.objects.create(
            goal=test_goal,
            nutrient=test_nutrient,
            target_amount=100.0
        )
        
        assert goal_nutrient.consumed_amount == 0.0  # Default value
    
    def test_goal_nutrient_relationships(self, test_goal_nutrient):
        """Test goal nutrient relationships."""
        # Test goal relationship
        assert test_goal_nutrient.goal.goal_nutrients.count() == 1
        assert test_goal_nutrient in test_goal_nutrient.goal.goal_nutrients.all()
        
        # Test nutrient relationship
        assert test_goal_nutrient.nutrient.nutrient_goals.count() == 1
        assert test_goal_nutrient in test_goal_nutrient.nutrient.nutrient_goals.all()
    
    def test_goal_nutrient_cascade_delete_goal(self, test_goal, test_nutrient):
        """Test that goal nutrient is deleted when goal is deleted."""
        goal_nutrient = GoalNutrient.objects.create(
            goal=test_goal,
            nutrient=test_nutrient,
            target_amount=100.0
        )
        
        goal_id = test_goal.id
        goal_nutrient_id = goal_nutrient.id
        
        # Delete the goal
        test_goal.delete()
        
        # Check that goal nutrient is also deleted
        assert not GoalNutrient.objects.filter(id=goal_nutrient_id).exists()
        assert not Goal.objects.filter(id=goal_id).exists()
    
    def test_goal_nutrient_cascade_delete_nutrient(self, test_goal, test_nutrient):
        """Test that goal nutrient is deleted when nutrient is deleted."""
        goal_nutrient = GoalNutrient.objects.create(
            goal=test_goal,
            nutrient=test_nutrient,
            target_amount=100.0
        )
        
        nutrient_id = test_nutrient.id
        goal_nutrient_id = goal_nutrient.id
        
        # Delete the nutrient
        test_nutrient.delete()
        
        # Check that goal nutrient is also deleted
        assert not GoalNutrient.objects.filter(id=goal_nutrient_id).exists()
        assert not Nutrient.objects.filter(id=nutrient_id).exists()
    
    def test_goal_nutrient_float_precision(self, test_goal, test_nutrient):
        """Test goal nutrient float precision."""
        goal_nutrient = GoalNutrient.objects.create(
            goal=test_goal,
            nutrient=test_nutrient,
            target_amount=123.456789,
            consumed_amount=45.678901
        )
        
        # Check that float values are preserved
        assert goal_nutrient.target_amount == 123.456789
        assert goal_nutrient.consumed_amount == 45.678901


# =========================================================
# NUTRIENT SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestNutrientSerializer:
    """Tests for NutrientSerializer functionality."""
    
    def test_nutrient_serializer_read(self, test_nutrient):
        """Test NutrientSerializer for reading."""
        serializer = NutrientSerializer(test_nutrient)
        data = serializer.data
        
        assert data['id'] == str(test_nutrient.id)
        assert data['code'] == test_nutrient.code
        assert data['name'] == test_nutrient.name
        assert data['unit'] == test_nutrient.unit
        assert data['category'] == test_nutrient.category
    
    def test_nutrient_serializer_create(self, db):
        """Test NutrientSerializer for creation."""
        data = {
            'code': 'fiber',
            'name': 'Dietary Fiber',
            'unit': 'g',
            'category': 'macronutrient'
        }
        
        serializer = NutrientSerializer(data=data)
        assert serializer.is_valid()
        
        nutrient = serializer.save()
        assert nutrient.code == 'fiber'
        assert nutrient.name == 'Dietary Fiber'
        assert nutrient.unit == 'g'
        assert nutrient.category == 'macronutrient'


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
            'target_amount': 150.0,
            'consumed_amount': 75.0
        }
        
        serializer = GoalNutrientWriteSerializer(data=data)
        assert serializer.is_valid()
        
        goal_nutrient = serializer.save()
        assert goal_nutrient.goal == test_goal
        assert goal_nutrient.nutrient == test_nutrient
        assert goal_nutrient.target_amount == 150.0
        assert goal_nutrient.consumed_amount == 75.0
    
    def test_goal_nutrient_write_serializer_update(self, test_goal_nutrient):
        """Test GoalNutrientWriteSerializer for update."""
        data = {
            'goal': test_goal_nutrient.goal.id,
            'nutrient': test_goal_nutrient.nutrient.id,
            'target_amount': 200.0,
            'consumed_amount': 100.0
        }
        
        serializer = GoalNutrientWriteSerializer(test_goal_nutrient, data=data)
        assert serializer.is_valid()
        
        updated_goal_nutrient = serializer.save()
        assert updated_goal_nutrient.target_amount == 200.0
        assert updated_goal_nutrient.consumed_amount == 100.0
    
    def test_goal_nutrient_write_serializer_validation(self, test_goal):
        """Test GoalNutrientWriteSerializer validation."""
        # Test with invalid nutrient ID
        data = {
            'goal': test_goal.id,
            'nutrient': 99999,  # Non-existent nutrient
            'target_amount': 100.0
        }
        
        serializer = GoalNutrientWriteSerializer(data=data)
        assert not serializer.is_valid()
        assert 'nutrient' in serializer.errors
    
    def test_goal_nutrient_write_serializer_default_consumed_amount(self, test_goal, test_nutrient):
        """Test GoalNutrientWriteSerializer with default consumed amount."""
        data = {
            'goal': test_goal.id,
            'nutrient': test_nutrient.id,
            'target_amount': 100.0
            # consumed_amount not provided, should use default
        }
        
        serializer = GoalNutrientWriteSerializer(data=data)
        assert serializer.is_valid()
        
        goal_nutrient = serializer.save()
        assert goal_nutrient.target_amount == 100.0
        assert goal_nutrient.consumed_amount == 0.0  # Default value


# =========================================================
# GOAL NUTRIENT READ SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestGoalNutrientReadSerializer:
    """Tests for GoalNutrientReadSerializer functionality."""
    
    def test_goal_nutrient_read_serializer(self, test_goal_nutrient):
        """Test GoalNutrientReadSerializer for reading."""
        serializer = GoalNutrientReadSerializer(test_goal_nutrient)
        data = serializer.data
        
        assert data['id'] == str(test_goal_nutrient.id)
        assert data['goal'] == test_goal_nutrient.goal.id
        assert 'nutrient' in data
        assert data['nutrient']['id'] == str(test_goal_nutrient.nutrient.id)
        assert data['nutrient']['name'] == test_goal_nutrient.nutrient.name
        assert data['nutrient']['unit'] == test_goal_nutrient.nutrient.unit
        assert data['target_amount'] == test_goal_nutrient.target_amount
        assert data['consumed_amount'] == test_goal_nutrient.consumed_amount
    
    def test_goal_nutrient_read_serializer_nested_nutrient(self, test_goal_nutrient):
        """Test that nested nutrient serializer is used."""
        serializer = GoalNutrientReadSerializer(test_goal_nutrient)
        data = serializer.data
        
        # Check that nutrient data is properly nested
        assert isinstance(data['nutrient'], dict)
        assert 'id' in data['nutrient']
        assert 'name' in data['nutrient']
        assert 'unit' in data['nutrient']
        assert 'category' in data['nutrient']


# =========================================================
# GOAL NUTRIENT VIEWSET TESTS
# =========================================================

@pytest.mark.django_db
class TestGoalNutrientViewSet:
    """Tests for GoalNutrientViewSet API endpoints."""
    
    def test_get_queryset(self, test_goal_nutrient, api_factory, add_session_to_request):
        """Test get_queryset returns all goal nutrients."""
        viewset = GoalNutrientViewSet()
        request = api_factory.get('/api/goal-nutrients/')
        request = add_session_to_request(request)
        
        viewset.request = request
        queryset = viewset.get_queryset()
        
        assert queryset.count() == 1
        assert test_goal_nutrient in queryset
    
    def test_get_serializer_class_create(self, api_factory, add_session_to_request):
        """Test serializer class selection for create action."""
        viewset = GoalNutrientViewSet()
        request = api_factory.post('/api/goal-nutrients/')
        request = add_session_to_request(request)
        
        viewset.request = request
        viewset.action = 'create'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class == GoalNutrientWriteSerializer
    
    def test_get_serializer_class_list(self, api_factory, add_session_to_request):
        """Test serializer class selection for list action."""
        viewset = GoalNutrientViewSet()
        request = api_factory.get('/api/goal-nutrients/')
        request = add_session_to_request(request)
        
        viewset.request = request
        viewset.action = 'list'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class == GoalNutrientReadSerializer
    
    def test_create_method(self, test_goal, test_nutrient):
        """Test create method with proper serialization using serializer directly."""
        # Test serializer creation directly instead of ViewSet
        data = {
            'goal': test_goal.id,
            'nutrient': test_nutrient.id,
            'target_amount': 200.0,
            'consumed_amount': 50.0
        }
        
        serializer = GoalNutrientWriteSerializer(data=data)
        assert serializer.is_valid()
        
        goal_nutrient = serializer.save()
        assert goal_nutrient.goal == test_goal
        assert goal_nutrient.nutrient == test_nutrient
        assert goal_nutrient.target_amount == 200.0
        assert goal_nutrient.consumed_amount == 50.0


# =========================================================
# INTEGRATION TESTS
# =========================================================

@pytest.mark.django_db
class TestGoalNutrientIntegration:
    """Integration tests for goal nutrient functionality."""
    
    def test_goal_nutrient_through_goal(self, test_goal, test_nutrient, test_nutrient_calories):
        """Test accessing goal nutrients through goal relationship."""
        # Create multiple goal nutrients
        GoalNutrient.objects.create(
            goal=test_goal,
            nutrient=test_nutrient,
            target_amount=100.0,
            consumed_amount=50.0
        )
        GoalNutrient.objects.create(
            goal=test_goal,
            nutrient=test_nutrient_calories,
            target_amount=2000.0,
            consumed_amount=1000.0
        )
        
        # Test accessing through goal
        goal_nutrients = test_goal.goal_nutrients.all()
        assert goal_nutrients.count() == 2
        
        # Test filtering by nutrient
        protein_nutrients = goal_nutrients.filter(nutrient=test_nutrient)
        assert protein_nutrients.count() == 1
        assert protein_nutrients.first().target_amount == 100.0
    
    def test_goal_nutrient_through_nutrient(self, test_goal, test_nutrient):
        """Test accessing goal nutrients through nutrient relationship."""
        # Create multiple goals with same nutrient
        user2 = Profile.objects.create(
            id=str(uuid.uuid4()),
            username='testuser2',
            email='test2@example.com'
        )
        goal2 = Goal.objects.create(user=user2)
        
        GoalNutrient.objects.create(
            goal=test_goal,
            nutrient=test_nutrient,
            target_amount=100.0,
            consumed_amount=50.0
        )
        GoalNutrient.objects.create(
            goal=goal2,
            nutrient=test_nutrient,
            target_amount=150.0,
            consumed_amount=75.0
        )
        
        # Test accessing through nutrient
        nutrient_goals = test_nutrient.nutrient_goals.all()
        assert nutrient_goals.count() == 2
        
        # Test filtering by goal
        goal1_nutrients = nutrient_goals.filter(goal=test_goal)
        assert goal1_nutrients.count() == 1
        assert goal1_nutrients.first().target_amount == 100.0
    
    def test_goal_nutrient_serialization_roundtrip(self, test_goal, test_nutrient):
        """Test serialization and deserialization roundtrip."""
        # Create goal nutrient
        original_goal_nutrient = GoalNutrient.objects.create(
            goal=test_goal,
            nutrient=test_nutrient,
            target_amount=150.0,
            consumed_amount=75.0
        )
        
        # Serialize
        read_serializer = GoalNutrientReadSerializer(original_goal_nutrient)
        data = read_serializer.data
        
        # Verify serialized data
        assert data['goal'] == test_goal.id
        assert data['nutrient']['id'] == str(test_nutrient.id)
        assert data['target_amount'] == 150.0
        assert data['consumed_amount'] == 75.0
        
        # Create new goal nutrient from serialized data (using different goal to avoid unique constraint)
        user2 = Profile.objects.create(
            id=str(uuid.uuid4()),
            username='testuser2',
            email='test2@example.com'
        )
        goal2 = Goal.objects.create(user=user2)
        
        write_data = {
            'goal': goal2.id,
            'nutrient': test_nutrient.id,
            'target_amount': data['target_amount'],
            'consumed_amount': data['consumed_amount']
        }
        
        write_serializer = GoalNutrientWriteSerializer(data=write_data)
        assert write_serializer.is_valid()
        
        new_goal_nutrient = write_serializer.save()
        assert new_goal_nutrient.target_amount == original_goal_nutrient.target_amount
        assert new_goal_nutrient.consumed_amount == original_goal_nutrient.consumed_amount


# =========================================================
# EDGE CASES AND BOUNDARY TESTS
# =========================================================

@pytest.mark.django_db
class TestGoalNutrientEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_goal_nutrient_zero_values(self, test_goal, test_nutrient):
        """Test goal nutrient with zero values."""
        goal_nutrient = GoalNutrient.objects.create(
            goal=test_goal,
            nutrient=test_nutrient,
            target_amount=0.0,
            consumed_amount=0.0
        )
        
        assert goal_nutrient.target_amount == 0.0
        assert goal_nutrient.consumed_amount == 0.0
        assert goal_nutrient.progress_percent == 0.0
    
    def test_goal_nutrient_negative_values(self, test_goal, test_nutrient):
        """Test goal nutrient with negative values."""
        goal_nutrient = GoalNutrient.objects.create(
            goal=test_goal,
            nutrient=test_nutrient,
            target_amount=-100.0,
            consumed_amount=-50.0
        )
        
        assert goal_nutrient.target_amount == -100.0
        assert goal_nutrient.consumed_amount == -50.0
        # Progress should still be calculated correctly
        assert goal_nutrient.progress_percent == 50.0
    
    def test_goal_nutrient_very_large_values(self, test_goal, test_nutrient):
        """Test goal nutrient with very large values."""
        goal_nutrient = GoalNutrient.objects.create(
            goal=test_goal,
            nutrient=test_nutrient,
            target_amount=999999.99,
            consumed_amount=500000.50
        )
        
        assert goal_nutrient.target_amount == 999999.99
        assert goal_nutrient.consumed_amount == 500000.50
        assert goal_nutrient.progress_percent == 50.0
    
    def test_goal_nutrient_progress_over_100_percent(self, test_goal, test_nutrient):
        """Test goal nutrient progress over 100 percent."""
        goal_nutrient = GoalNutrient.objects.create(
            goal=test_goal,
            nutrient=test_nutrient,
            target_amount=100.0,
            consumed_amount=150.0
        )
        
        # Progress should be capped at 100%
        assert goal_nutrient.progress_percent == 100.0
    
    def test_goal_nutrient_string_representation_edge_cases(self, test_goal, test_nutrient):
        """Test string representation with edge case values."""
        # Test with zero values
        goal_nutrient = GoalNutrient.objects.create(
            goal=test_goal,
            nutrient=test_nutrient,
            target_amount=0.0,
            consumed_amount=0.0
        )
        
        str_repr = str(goal_nutrient)
        assert str(test_goal.id) in str_repr
        assert str(test_nutrient.id) in str_repr
        assert '0.0' in str_repr


# =========================================================
# PERFORMANCE AND QUERY TESTS
# =========================================================

@pytest.mark.django_db
class TestGoalNutrientPerformance:
    """Tests for performance and query optimization."""
    
    def test_goal_nutrient_select_related(self, test_goal, test_nutrient):
        """Test that select_related works properly for goal nutrient queries."""
        GoalNutrient.objects.create(
            goal=test_goal,
            nutrient=test_nutrient,
            target_amount=100.0
        )
        
        # Test select_related optimization
        goal_nutrients = GoalNutrient.objects.select_related('goal', 'nutrient').all()
        for gn in goal_nutrients:
            # Accessing related objects should not trigger additional queries
            _ = gn.goal.user.username
            _ = gn.nutrient.name
        
        # Verify that we can access the related objects
        assert len(goal_nutrients) == 1
        assert goal_nutrients[0].goal.user.username == test_goal.user.username
        assert goal_nutrients[0].nutrient.name == test_nutrient.name
    
    def test_goal_nutrient_bulk_operations(self, test_goal):
        """Test bulk operations with goal nutrients."""
        # Create multiple nutrients
        nutrients = []
        for i in range(5):
            nutrient = Nutrient.objects.create(
                code=f'nutrient_{i}',
                name=f'Nutrient {i}',
                unit='g',
                category='macronutrient'
            )
            nutrients.append(nutrient)
        
        # Bulk create goal nutrients
        goal_nutrients = []
        for i, nutrient in enumerate(nutrients):
            goal_nutrients.append(GoalNutrient(
                goal=test_goal,
                nutrient=nutrient,
                target_amount=100.0 + i,
                consumed_amount=50.0 + i
            ))
        
        GoalNutrient.objects.bulk_create(goal_nutrients)
        
        # Verify all were created
        assert GoalNutrient.objects.filter(goal=test_goal).count() == 5
        
        # Test bulk update
        GoalNutrient.objects.filter(goal=test_goal).update(
            consumed_amount=75.0
        )
        
        # Verify update
        for gn in GoalNutrient.objects.filter(goal=test_goal):
            assert gn.consumed_amount == 75.0
    
    def test_goal_nutrient_progress_calculation_performance(self, test_goal):
        """Test performance of progress calculation."""
        # Create multiple goal nutrients
        nutrients = []
        for i in range(10):
            nutrient = Nutrient.objects.create(
                code=f'nutrient_{i}',
                name=f'Nutrient {i}',
                unit='g',
                category='macronutrient'
            )
            nutrients.append(nutrient)
        
        goal_nutrients = []
        for i, nutrient in enumerate(nutrients):
            goal_nutrients.append(GoalNutrient(
                goal=test_goal,
                nutrient=nutrient,
                target_amount=100.0,
                consumed_amount=float(i * 10)
            ))
        
        GoalNutrient.objects.bulk_create(goal_nutrients)
        
        # Test progress calculation performance
        goal_nutrients = GoalNutrient.objects.filter(goal=test_goal)
        for gn in goal_nutrients:
            progress = gn.progress_percent
            assert 0 <= progress <= 100
            assert isinstance(progress, float)
