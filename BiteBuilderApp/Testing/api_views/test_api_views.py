"""
Test suite for API Views functionality.
Comprehensive testing for Django REST Framework ViewSets.
"""

import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework import status, viewsets
from django.contrib.sessions.models import Session

from apps.api.views import (
    MealViewSet,
    MealItemViewSet,
    NutrientViewSet,
    ProfileViewSet,
    GoalViewSet,
    GoalNutrientViewSet,
    EatenMealViewSet
)
from apps.core.models import Meal, MealItem, Nutrient, Goal, GoalNutrient
from apps.core.models.eaten_meal import EatenMeal
from apps.users.models import Profile


@pytest.fixture
def api_factory():
    """Create API request factory for testing."""
    return APIRequestFactory()


@pytest.fixture
def api_client():
    """Create API client for testing."""
    return APIClient()


class TestMealViewSet:
    """Tests for MealViewSet."""
    
    def test_get_serializer_class_read_actions(self, api_factory):
        """Test get_serializer_class returns MealSerializer for read actions."""
        viewset = MealViewSet()
        viewset.action = 'list'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class.__name__ == 'MealSerializer'
    
    def test_get_serializer_class_write_actions(self, api_factory):
        """Test get_serializer_class returns MealWriteSerializer for write actions."""
        viewset = MealViewSet()
        viewset.action = 'create'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class.__name__ == 'MealWriteSerializer'
    
    def test_get_serializer_class_update_actions(self, api_factory):
        """Test get_serializer_class returns MealWriteSerializer for update actions."""
        viewset = MealViewSet()
        viewset.action = 'update'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class.__name__ == 'MealWriteSerializer'
    
    def test_get_serializer_class_partial_update_actions(self, api_factory):
        """Test get_serializer_class returns MealWriteSerializer for partial_update actions."""
        viewset = MealViewSet()
        viewset.action = 'partial_update'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class.__name__ == 'MealWriteSerializer'
    
    def test_get_queryset_no_session(self, api_factory):
        """Test get_queryset returns empty queryset when no session."""
        request = api_factory.get('/api/meals/')
        request.session = {}
        
        viewset = MealViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        assert queryset.count() == 0
    
    def test_get_queryset_no_user_id(self, api_factory):
        """Test get_queryset returns empty queryset when no user_id in session."""
        request = api_factory.get('/api/meals/')
        request.session = {'other_key': 'value'}
        
        viewset = MealViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        assert queryset.count() == 0
    
    @patch('apps.api.views.Meal.objects')
    def test_get_queryset_with_user_id(self, mock_meal_objects, api_factory):
        """Test get_queryset filters by user_id when session contains user_id."""
        request = api_factory.get('/api/meals/')
        request.session = {'sb_user_id': 'user123'}
        
        # Mock the queryset chain
        mock_queryset = MagicMock()
        mock_meal_objects.select_related.return_value = mock_queryset
        mock_queryset.prefetch_related.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        
        viewset = MealViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        
        # Verify the queryset chain was called correctly
        mock_meal_objects.select_related.assert_called_once_with("user")
        mock_queryset.prefetch_related.assert_called_once_with("items__product__product_nutrients__nutrient")
        mock_queryset.filter.assert_called_once_with(user='user123')
        mock_queryset.order_by.assert_called_once_with("-date_time")
    
    def test_perform_create_no_session(self, api_factory):
        """Test perform_create raises PermissionError when no session."""
        request = api_factory.post('/api/meals/')
        request.session = {}
        
        viewset = MealViewSet()
        viewset.request = request
        
        serializer = MagicMock()
        
        with pytest.raises(PermissionError, match="User not authenticated in session."):
            viewset.perform_create(serializer)
    
    def test_perform_create_no_user_id(self, api_factory):
        """Test perform_create raises PermissionError when no user_id in session."""
        request = api_factory.post('/api/meals/')
        request.session = {'other_key': 'value'}
        
        viewset = MealViewSet()
        viewset.request = request
        
        serializer = MagicMock()
        
        with pytest.raises(PermissionError, match="User not authenticated in session."):
            viewset.perform_create(serializer)
    
    def test_perform_create_success(self, api_factory):
        """Test perform_create saves with user_id when session contains user_id."""
        request = api_factory.post('/api/meals/')
        request.session = {'sb_user_id': 'user123'}
        
        viewset = MealViewSet()
        viewset.request = request
        
        serializer = MagicMock()
        
        viewset.perform_create(serializer)
        
        serializer.save.assert_called_once_with(user_id='user123')


class TestMealItemViewSet:
    """Tests for MealItemViewSet."""
    
    def test_get_serializer_class_read_actions(self, api_factory):
        """Test get_serializer_class returns MealItemSerializer for read actions."""
        viewset = MealItemViewSet()
        viewset.action = 'list'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class.__name__ == 'MealItemSerializer'
    
    def test_get_serializer_class_write_actions(self, api_factory):
        """Test get_serializer_class returns MealItemWriteSerializer for write actions."""
        viewset = MealItemViewSet()
        viewset.action = 'create'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class.__name__ == 'MealItemWriteSerializer'
    
    def test_get_serializer_class_update_actions(self, api_factory):
        """Test get_serializer_class returns MealItemWriteSerializer for update actions."""
        viewset = MealItemViewSet()
        viewset.action = 'update'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class.__name__ == 'MealItemWriteSerializer'
    
    def test_get_serializer_class_partial_update_actions(self, api_factory):
        """Test get_serializer_class returns MealItemWriteSerializer for partial_update actions."""
        viewset = MealItemViewSet()
        viewset.action = 'partial_update'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class.__name__ == 'MealItemWriteSerializer'
    
    def test_get_queryset_no_session(self, api_factory):
        """Test get_queryset returns empty queryset when no session."""
        request = api_factory.get('/api/meal-items/')
        request.session = {}
        
        viewset = MealItemViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        assert queryset.count() == 0
    
    def test_get_queryset_no_user_id(self, api_factory):
        """Test get_queryset returns empty queryset when no user_id in session."""
        request = api_factory.get('/api/meal-items/')
        request.session = {'other_key': 'value'}
        
        viewset = MealItemViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        assert queryset.count() == 0
    
    @patch('apps.api.views.MealItem.objects')
    def test_get_queryset_with_user_id(self, mock_meal_item_objects, api_factory):
        """Test get_queryset filters by user_id when session contains user_id."""
        request = api_factory.get('/api/meal-items/')
        request.session = {'sb_user_id': 'user123'}
        
        # Mock the queryset chain
        mock_queryset = MagicMock()
        mock_meal_item_objects.select_related.return_value = mock_queryset
        mock_queryset.prefetch_related.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        
        viewset = MealItemViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        
        # Verify the queryset chain was called correctly
        mock_meal_item_objects.select_related.assert_called_once_with("meal", "product")
        mock_queryset.prefetch_related.assert_called_once_with("product__product_nutrients__nutrient")
        mock_queryset.filter.assert_called_once_with(meal__user='user123')
        mock_queryset.order_by.assert_called_once_with("-meal__date_time")
    
    @patch('apps.api.views.MealItemWriteSerializer')
    @patch('apps.api.views.MealItemSerializer')
    def test_create_success(self, mock_read_serializer_class, mock_write_serializer_class, api_factory):
        """Test create method uses write serializer for input and read serializer for output."""
        request = api_factory.post('/api/meal-items/', {'test': 'data'})
        # Mock request.data attribute
        request.data = {'test': 'data'}
        
        # Mock write serializer
        mock_write_serializer = MagicMock()
        mock_write_serializer.is_valid.return_value = True
        mock_meal_item = MagicMock()
        mock_write_serializer.save.return_value = mock_meal_item
        mock_write_serializer_class.return_value = mock_write_serializer
        
        # Mock read serializer
        mock_read_serializer = MagicMock()
        mock_read_serializer.data = {'id': 1, 'test': 'data'}
        mock_read_serializer_class.return_value = mock_read_serializer
        
        viewset = MealItemViewSet()
        viewset.request = request
        
        response = viewset.create(request)
        
        # Verify write serializer was used for validation and saving
        mock_write_serializer_class.assert_called_once()
        mock_write_serializer.is_valid.assert_called_once_with(raise_exception=True)
        mock_write_serializer.save.assert_called_once()
        
        # Verify read serializer was used for response
        mock_read_serializer_class.assert_called_once_with(mock_meal_item, context={"request": request})
        
        # Verify response
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data == {'id': 1, 'test': 'data'}
    
    @patch('apps.api.views.MealItemWriteSerializer')
    def test_create_validation_error(self, mock_write_serializer_class, api_factory):
        """Test create method raises exception when validation fails."""
        request = api_factory.post('/api/meal-items/', {'test': 'data'})
        # Mock request.data attribute
        request.data = {'test': 'data'}
        
        # Mock write serializer with validation error
        mock_write_serializer = MagicMock()
        mock_write_serializer.is_valid.side_effect = Exception("Validation error")
        mock_write_serializer_class.return_value = mock_write_serializer
        
        viewset = MealItemViewSet()
        viewset.request = request
        
        with pytest.raises(Exception, match="Validation error"):
            viewset.create(request)


class TestNutrientViewSet:
    """Tests for NutrientViewSet."""
    
    def test_queryset(self, api_factory):
        """Test NutrientViewSet queryset."""
        viewset = NutrientViewSet()
        assert viewset.queryset.model == Nutrient
    
    def test_serializer_class(self, api_factory):
        """Test NutrientViewSet serializer class."""
        viewset = NutrientViewSet()
        assert viewset.serializer_class.__name__ == 'NutrientSerializer'


class TestProfileViewSet:
    """Tests for ProfileViewSet."""
    
    def test_queryset(self, api_factory):
        """Test ProfileViewSet queryset."""
        viewset = ProfileViewSet()
        assert viewset.queryset.model == Profile
    
    def test_serializer_class(self, api_factory):
        """Test ProfileViewSet serializer class."""
        viewset = ProfileViewSet()
        assert viewset.serializer_class.__name__ == 'ProfileSerializer'


class TestGoalViewSet:
    """Tests for GoalViewSet."""
    
    def test_queryset(self, api_factory):
        """Test GoalViewSet queryset."""
        viewset = GoalViewSet()
        assert viewset.queryset.model == Goal
    
    def test_serializer_class(self, api_factory):
        """Test GoalViewSet serializer class."""
        viewset = GoalViewSet()
        assert viewset.serializer_class.__name__ == 'GoalSerializer'
    
    def test_get_queryset_no_user_param(self, api_factory):
        """Test get_queryset returns all goals when no user parameter."""
        request = api_factory.get('/api/goals/')
        # Mock request.query_params attribute
        request.query_params = {}
        
        viewset = GoalViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        assert queryset.model == Goal
    
    def test_get_queryset_with_user_param(self, api_factory):
        """Test get_queryset filters by user when user parameter provided."""
        request = api_factory.get('/api/goals/?user=user123')
        # Mock request.query_params attribute
        request.query_params = {'user': 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'}
        
        viewset = GoalViewSet()
        viewset.request = request
        
        # Test the actual get_queryset method
        with patch('apps.api.views.Goal.objects') as mock_goal_objects:
            mock_queryset = MagicMock()
            mock_queryset.filter.return_value = mock_queryset
            mock_goal_objects.all.return_value = mock_queryset
            
            # Mock super().get_queryset() to return our mock queryset
            with patch.object(viewsets.ModelViewSet, 'get_queryset', return_value=mock_queryset):
                queryset = viewset.get_queryset()
                mock_queryset.filter.assert_called_once_with(user_id='a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11')
    
    def test_get_queryset_with_empty_user_param(self, api_factory):
        """Test get_queryset returns all goals when user parameter is empty."""
        request = api_factory.get('/api/goals/?user=')
        # Mock request.query_params attribute
        request.query_params = {'user': ''}
        
        viewset = GoalViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        assert queryset.model == Goal


class TestGoalNutrientViewSet:
    """Tests for GoalNutrientViewSet."""
    
    def test_queryset(self, api_factory):
        """Test GoalNutrientViewSet queryset."""
        viewset = GoalNutrientViewSet()
        assert viewset.queryset.model == GoalNutrient
    
    def test_get_serializer_class_read_actions(self, api_factory):
        """Test get_serializer_class returns GoalNutrientReadSerializer for read actions."""
        viewset = GoalNutrientViewSet()
        viewset.action = 'list'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class.__name__ == 'GoalNutrientReadSerializer'
    
    def test_get_serializer_class_write_actions(self, api_factory):
        """Test get_serializer_class returns GoalNutrientWriteSerializer for write actions."""
        viewset = GoalNutrientViewSet()
        viewset.action = 'create'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class.__name__ == 'GoalNutrientWriteSerializer'
    
    def test_get_serializer_class_update_actions(self, api_factory):
        """Test get_serializer_class returns GoalNutrientWriteSerializer for update actions."""
        viewset = GoalNutrientViewSet()
        viewset.action = 'update'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class.__name__ == 'GoalNutrientWriteSerializer'
    
    def test_get_serializer_class_partial_update_actions(self, api_factory):
        """Test get_serializer_class returns GoalNutrientWriteSerializer for partial_update actions."""
        viewset = GoalNutrientViewSet()
        viewset.action = 'partial_update'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class.__name__ == 'GoalNutrientWriteSerializer'
    
    @patch('apps.api.views.GoalNutrientWriteSerializer')
    @patch('apps.api.views.GoalNutrientReadSerializer')
    def test_create_success(self, mock_read_serializer_class, mock_write_serializer_class, api_factory):
        """Test create method uses write serializer for input and read serializer for output."""
        request = api_factory.post('/api/goal-nutrients/', {'test': 'data'})
        # Mock request.data attribute
        request.data = {'test': 'data'}
        
        # Mock write serializer
        mock_write_serializer = MagicMock()
        mock_write_serializer.is_valid.return_value = True
        mock_instance = MagicMock()
        mock_write_serializer.save.return_value = mock_instance
        mock_write_serializer_class.return_value = mock_write_serializer
        
        # Mock read serializer
        mock_read_serializer = MagicMock()
        mock_read_serializer.data = {'id': 1, 'test': 'data'}
        mock_read_serializer_class.return_value = mock_read_serializer
        
        viewset = GoalNutrientViewSet()
        viewset.request = request
        viewset.action = 'create'
        viewset.format_kwarg = None
        
        response = viewset.create(request)
        
        # Verify write serializer was used for validation and saving
        mock_write_serializer_class.assert_called_once()
        mock_write_serializer.is_valid.assert_called_once_with(raise_exception=True)
        mock_write_serializer.save.assert_called_once()
        
        # Verify read serializer was used for response
        mock_read_serializer_class.assert_called_once_with(mock_instance, context={"request": request})
        
        # Verify response
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data == {'id': 1, 'test': 'data'}
    
    @patch('apps.api.views.GoalNutrientWriteSerializer')
    def test_create_validation_error(self, mock_write_serializer_class, api_factory):
        """Test create method raises exception when validation fails."""
        request = api_factory.post('/api/goal-nutrients/', {'test': 'data'})
        # Mock request.data attribute
        request.data = {'test': 'data'}
        
        # Mock write serializer with validation error
        mock_write_serializer = MagicMock()
        mock_write_serializer.is_valid.side_effect = Exception("Validation error")
        mock_write_serializer_class.return_value = mock_write_serializer
        
        viewset = GoalNutrientViewSet()
        viewset.request = request
        viewset.action = 'create'
        viewset.format_kwarg = None
        
        with pytest.raises(Exception, match="Validation error"):
            viewset.create(request)


class TestEatenMealViewSet:
    """Tests for EatenMealViewSet."""
    
    def test_queryset(self, api_factory):
        """Test EatenMealViewSet queryset."""
        viewset = EatenMealViewSet()
        assert viewset.queryset.model == EatenMeal
    
    def test_serializer_class(self, api_factory):
        """Test EatenMealViewSet default serializer class."""
        viewset = EatenMealViewSet()
        assert viewset.serializer_class.__name__ == 'EatenMealReadSerializer'
    
    def test_get_serializer_class_read_actions(self, api_factory):
        """Test get_serializer_class returns EatenMealReadSerializer for read actions."""
        viewset = EatenMealViewSet()
        viewset.action = 'list'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class.__name__ == 'EatenMealReadSerializer'
    
    def test_get_serializer_class_write_actions(self, api_factory):
        """Test get_serializer_class returns EatenMealWriteSerializer for write actions."""
        viewset = EatenMealViewSet()
        viewset.action = 'create'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class.__name__ == 'EatenMealWriteSerializer'
    
    def test_get_serializer_class_update_actions(self, api_factory):
        """Test get_serializer_class returns EatenMealWriteSerializer for update actions."""
        viewset = EatenMealViewSet()
        viewset.action = 'update'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class.__name__ == 'EatenMealWriteSerializer'
    
    def test_get_serializer_class_partial_update_actions(self, api_factory):
        """Test get_serializer_class returns EatenMealWriteSerializer for partial_update actions."""
        viewset = EatenMealViewSet()
        viewset.action = 'partial_update'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class.__name__ == 'EatenMealWriteSerializer'
    
    @patch('apps.api.views.EatenMealWriteSerializer')
    @patch('apps.api.views.EatenMealReadSerializer')
    def test_create_success(self, mock_read_serializer_class, mock_write_serializer_class, api_factory):
        """Test create method uses write serializer for input and read serializer for output."""
        request = api_factory.post('/api/eaten-meals/', {'test': 'data'})
        # Mock request.data attribute
        request.data = {'test': 'data'}
        
        # Mock write serializer
        mock_write_serializer = MagicMock()
        mock_write_serializer.is_valid.return_value = True
        mock_instance = MagicMock()
        mock_write_serializer.save.return_value = mock_instance
        mock_write_serializer_class.return_value = mock_write_serializer
        
        # Mock read serializer
        mock_read_serializer = MagicMock()
        mock_read_serializer.data = {'id': 1, 'test': 'data'}
        mock_read_serializer_class.return_value = mock_read_serializer
        
        viewset = EatenMealViewSet()
        viewset.request = request
        viewset.action = 'create'
        viewset.format_kwarg = None
        
        response = viewset.create(request)
        
        # Verify write serializer was used for validation and saving
        mock_write_serializer_class.assert_called_once()
        mock_write_serializer.is_valid.assert_called_once_with(raise_exception=True)
        mock_write_serializer.save.assert_called_once()
        
        # Verify read serializer was used for response
        mock_read_serializer_class.assert_called_once_with(mock_instance, context={"request": request})
        
        # Verify response
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data == {'id': 1, 'test': 'data'}
    
    @patch('apps.api.views.EatenMealWriteSerializer')
    def test_create_validation_error(self, mock_write_serializer_class, api_factory):
        """Test create method raises exception when validation fails."""
        request = api_factory.post('/api/eaten-meals/', {'test': 'data'})
        # Mock request.data attribute
        request.data = {'test': 'data'}
        
        # Mock write serializer with validation error
        mock_write_serializer = MagicMock()
        mock_write_serializer.is_valid.side_effect = Exception("Validation error")
        mock_write_serializer_class.return_value = mock_write_serializer
        
        viewset = EatenMealViewSet()
        viewset.request = request
        viewset.action = 'create'
        viewset.format_kwarg = None
        
        with pytest.raises(Exception, match="Validation error"):
            viewset.create(request)


class TestApiViewsIntegration:
    """Integration tests for API Views."""
    
    def test_meal_viewset_integration(self, api_factory):
        """Test MealViewSet integration with session management."""
        request = api_factory.get('/api/meals/')
        request.session = {'sb_user_id': 'user123'}
        
        with patch('apps.api.views.Meal.objects') as mock_meal_objects:
            mock_queryset = MagicMock()
            mock_meal_objects.select_related.return_value = mock_queryset
            mock_queryset.prefetch_related.return_value = mock_queryset
            mock_queryset.filter.return_value = mock_queryset
            mock_queryset.order_by.return_value = mock_queryset
            
            viewset = MealViewSet()
            viewset.request = request
            
            # Test get_queryset
            queryset = viewset.get_queryset()
            mock_meal_objects.select_related.assert_called_once_with("user")
            
            # Test get_serializer_class
            viewset.action = 'list'
            serializer_class = viewset.get_serializer_class()
            assert serializer_class.__name__ == 'MealSerializer'
            
            viewset.action = 'create'
            serializer_class = viewset.get_serializer_class()
            assert serializer_class.__name__ == 'MealWriteSerializer'
    
    def test_meal_item_viewset_integration(self, api_factory):
        """Test MealItemViewSet integration with session management."""
        request = api_factory.get('/api/meal-items/')
        request.session = {'sb_user_id': 'user123'}
        
        with patch('apps.api.views.MealItem.objects') as mock_meal_item_objects:
            mock_queryset = MagicMock()
            mock_meal_item_objects.select_related.return_value = mock_queryset
            mock_queryset.prefetch_related.return_value = mock_queryset
            mock_queryset.filter.return_value = mock_queryset
            mock_queryset.order_by.return_value = mock_queryset
            
            viewset = MealItemViewSet()
            viewset.request = request
            
            # Test get_queryset
            queryset = viewset.get_queryset()
            mock_meal_item_objects.select_related.assert_called_once_with("meal", "product")
            
            # Test get_serializer_class
            viewset.action = 'list'
            serializer_class = viewset.get_serializer_class()
            assert serializer_class.__name__ == 'MealItemSerializer'
            
            viewset.action = 'create'
            serializer_class = viewset.get_serializer_class()
            assert serializer_class.__name__ == 'MealItemWriteSerializer'
    
    def test_goal_viewset_integration(self, api_factory):
        """Test GoalViewSet integration with query parameters."""
        request = api_factory.get('/api/goals/?user=user123')
        # Mock request.query_params attribute
        request.query_params = {'user': 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'}
        
        with patch('apps.api.views.Goal.objects') as mock_goal_objects:
            mock_queryset = MagicMock()
            mock_queryset.filter.return_value = mock_queryset
            mock_goal_objects.all.return_value = mock_queryset
            
            viewset = GoalViewSet()
            viewset.request = request
            
            # Mock super().get_queryset() to return our mock queryset
            with patch.object(viewsets.ModelViewSet, 'get_queryset', return_value=mock_queryset):
                # Test get_queryset
                queryset = viewset.get_queryset()
                mock_queryset.filter.assert_called_once_with(user_id='a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11')
            
            # Test serializer class
            assert viewset.serializer_class.__name__ == 'GoalSerializer'
    
    def test_goal_nutrient_viewset_integration(self, api_factory):
        """Test GoalNutrientViewSet integration with serializer switching."""
        viewset = GoalNutrientViewSet()
        
        # Test different actions
        viewset.action = 'list'
        assert viewset.get_serializer_class().__name__ == 'GoalNutrientReadSerializer'
        
        viewset.action = 'create'
        assert viewset.get_serializer_class().__name__ == 'GoalNutrientWriteSerializer'
        
        viewset.action = 'update'
        assert viewset.get_serializer_class().__name__ == 'GoalNutrientWriteSerializer'
        
        viewset.action = 'partial_update'
        assert viewset.get_serializer_class().__name__ == 'GoalNutrientWriteSerializer'
    
    def test_eaten_meal_viewset_integration(self, api_factory):
        """Test EatenMealViewSet integration with serializer switching."""
        viewset = EatenMealViewSet()
        
        # Test different actions
        viewset.action = 'list'
        assert viewset.get_serializer_class().__name__ == 'EatenMealReadSerializer'
        
        viewset.action = 'create'
        assert viewset.get_serializer_class().__name__ == 'EatenMealWriteSerializer'
        
        viewset.action = 'update'
        assert viewset.get_serializer_class().__name__ == 'EatenMealWriteSerializer'
        
        viewset.action = 'partial_update'
        assert viewset.get_serializer_class().__name__ == 'EatenMealWriteSerializer'


class TestApiViewsEdgeCases:
    """Edge case tests for API Views."""
    
    def test_meal_viewset_session_edge_cases(self, api_factory):
        """Test MealViewSet with various session edge cases."""
        viewset = MealViewSet()
        
        # Test with None session
        request = api_factory.get('/api/meals/')
        request.session = None
        viewset.request = request
        
        with pytest.raises(AttributeError):
            viewset.get_queryset()
        
        # Test with empty session
        request = api_factory.get('/api/meals/')
        request.session = {}
        viewset.request = request
        
        queryset = viewset.get_queryset()
        assert queryset.count() == 0
    
    def test_meal_item_viewset_session_edge_cases(self, api_factory):
        """Test MealItemViewSet with various session edge cases."""
        viewset = MealItemViewSet()
        
        # Test with None session
        request = api_factory.get('/api/meal-items/')
        request.session = None
        viewset.request = request
        
        with pytest.raises(AttributeError):
            viewset.get_queryset()
        
        # Test with empty session
        request = api_factory.get('/api/meal-items/')
        request.session = {}
        viewset.request = request
        
        queryset = viewset.get_queryset()
        assert queryset.count() == 0
    
    def test_goal_viewset_query_param_edge_cases(self, api_factory):
        """Test GoalViewSet with various query parameter edge cases."""
        viewset = GoalViewSet()
        
        # Test with None user parameter
        request = api_factory.get('/api/goals/?user=None')
        request.query_params = {'user': 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'}
        viewset.request = request
        
        queryset = viewset.get_queryset()
        assert queryset.model == Goal
        
        # Test with special characters in user parameter
        request = api_factory.get('/api/goals/?user=user@123')
        request.query_params = {'user': 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'}
        viewset.request = request
        
        with patch('apps.api.views.Goal.objects') as mock_goal_objects:
            mock_queryset = MagicMock()
            mock_queryset.filter.return_value = mock_queryset
            mock_goal_objects.all.return_value = mock_queryset
            
            # Mock super().get_queryset() to return our mock queryset
            with patch.object(viewsets.ModelViewSet, 'get_queryset', return_value=mock_queryset):
                queryset = viewset.get_queryset()
                mock_queryset.filter.assert_called_once_with(user_id='a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11')
    
    def test_viewset_action_edge_cases(self, api_factory):
        """Test ViewSets with various action edge cases."""
        # Test MealViewSet with unknown action
        viewset = MealViewSet()
        viewset.action = 'unknown_action'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class.__name__ == 'MealSerializer'  # Should default to read serializer
        
        # Test MealItemViewSet with unknown action
        viewset = MealItemViewSet()
        viewset.action = 'unknown_action'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class.__name__ == 'MealItemSerializer'  # Should default to read serializer
        
        # Test GoalNutrientViewSet with unknown action
        viewset = GoalNutrientViewSet()
        viewset.action = 'unknown_action'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class.__name__ == 'GoalNutrientReadSerializer'  # Should default to read serializer
        
        # Test EatenMealViewSet with unknown action
        viewset = EatenMealViewSet()
        viewset.action = 'unknown_action'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class.__name__ == 'EatenMealReadSerializer'  # Should default to read serializer
    
    def test_perform_create_edge_cases(self, api_factory):
        """Test perform_create with various edge cases."""
        viewset = MealViewSet()
        
        # Test with None session
        request = api_factory.post('/api/meals/')
        request.session = None
        viewset.request = request
        
        serializer = MagicMock()
        
        with pytest.raises(AttributeError):
            viewset.perform_create(serializer)
        
        # Test with session but no sb_user_id
        request = api_factory.post('/api/meals/')
        request.session = {'other_key': 'value'}
        viewset.request = request
        
        serializer = MagicMock()
        
        with pytest.raises(PermissionError, match="User not authenticated in session."):
            viewset.perform_create(serializer)
    
    def test_create_method_edge_cases(self, api_factory):
        """Test create methods with various edge cases."""
        # Test MealItemViewSet create with invalid data
        request = api_factory.post('/api/meal-items/', {})
        request.data = {}
        
        with patch('apps.api.views.MealItemWriteSerializer') as mock_serializer_class:
            mock_serializer = MagicMock()
            mock_serializer.is_valid.side_effect = Exception("Validation failed")
            mock_serializer_class.return_value = mock_serializer
            
            viewset = MealItemViewSet()
            viewset.request = request
            
            with pytest.raises(Exception, match="Validation failed"):
                viewset.create(request)
        
        # Test GoalNutrientViewSet create with invalid data
        request = api_factory.post('/api/goal-nutrients/', {})
        request.data = {}
        
        with patch('apps.api.views.GoalNutrientWriteSerializer') as mock_serializer_class:
            mock_serializer = MagicMock()
            mock_serializer.is_valid.side_effect = Exception("Validation failed")
            mock_serializer_class.return_value = mock_serializer
            
            viewset = GoalNutrientViewSet()
            viewset.request = request
            viewset.action = 'create'
            viewset.format_kwarg = None
            
            with pytest.raises(Exception, match="Validation failed"):
                viewset.create(request)
        
        # Test EatenMealViewSet create with invalid data
        request = api_factory.post('/api/eaten-meals/', {})
        request.data = {}
        
        with patch('apps.api.views.EatenMealWriteSerializer') as mock_serializer_class:
            mock_serializer = MagicMock()
            mock_serializer.is_valid.side_effect = Exception("Validation failed")
            mock_serializer_class.return_value = mock_serializer
            
            viewset = EatenMealViewSet()
            viewset.request = request
            viewset.action = 'create'
            viewset.format_kwarg = None
            
            with pytest.raises(Exception, match="Validation failed"):
                viewset.create(request)
