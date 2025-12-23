"""
Test suite for MealItem functionality including model, serializers, and related functionality.
Comprehensive testing with high coverage for all meal_item-related functionality.
"""

import pytest
import uuid
from decimal import Decimal
from django.utils import timezone
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework import status
from django.contrib.sessions.middleware import SessionMiddleware
from datetime import datetime, timedelta

from apps.core.models import Meal, MealItem, Product, Nutrient
from apps.users.models import Profile
from apps.api.views import MealItemViewSet
from apps.api.serializers import MealItemSerializer, MealItemWriteSerializer, ProductReadSerializer


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
    product = Product.objects.create(
        name='Test Product',
        brand='Test Brand',
        description='Test Description',
        barcode='123456789'
    )
    return product


@pytest.fixture
def test_product2(db):
    """Create a second test product for testing."""
    return Product.objects.create(
        name='Test Product 2',
        brand='Test Brand 2',
        description='Test Description 2',
        barcode='987654321'
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
def test_meal_item2(db, test_meal2, test_product2):
    """Create a second test meal item for testing."""
    return MealItem.objects.create(
        meal=test_meal2,
        product=test_product2,
        quantity=200.0
    )


# =========================================================
# MEAL ITEM MODEL TESTS
# =========================================================

@pytest.mark.django_db
class TestMealItemModel:
    """Tests for MealItem model functionality."""
    
    def test_meal_item_creation(self, test_meal, test_product):
        """Test basic meal item creation."""
        meal_item = MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=150.0
        )
        
        assert meal_item.meal == test_meal
        assert meal_item.product == test_product
        assert meal_item.quantity == 150.0
        assert meal_item.id is not None
    
    def test_meal_item_str_representation(self, test_meal_item):
        """Test meal item string representation."""
        str_repr = str(test_meal_item)
        assert str(test_meal_item.meal_id) in str_repr
        assert str(test_meal_item.product_id) in str_repr
        assert str(test_meal_item.quantity) in str_repr
    
    def test_meal_item_meta_options(self):
        """Test meal item model meta options."""
        assert MealItem._meta.db_table == "bitebuilder.meal_item"
        assert len(MealItem._meta.indexes) == 2
        
        # Test index fields
        indexes = MealItem._meta.indexes
        index_fields = [index.fields for index in indexes]
        assert ["meal"] in index_fields
        assert ["product"] in index_fields
    
    def test_meal_item_relationships(self, test_meal_item):
        """Test meal item relationships."""
        # Test meal relationship
        assert test_meal_item.meal.items.count() == 1
        assert test_meal_item in test_meal_item.meal.items.all()
        
        # Test product relationship
        assert test_meal_item.product.meal_items.count() == 1
        assert test_meal_item in test_meal_item.product.meal_items.all()
    
    def test_meal_item_cascade_delete_meal(self, test_meal, test_product):
        """Test that meal item is deleted when meal is deleted."""
        meal_item = MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=100.0
        )
        
        meal_id = test_meal.id
        meal_item_id = meal_item.id
        
        # Delete the meal
        test_meal.delete()
        
        # Check that meal item is also deleted
        assert not MealItem.objects.filter(id=meal_item_id).exists()
        assert not Meal.objects.filter(id=meal_id).exists()
    
    def test_meal_item_cascade_delete_product(self, test_meal, test_product):
        """Test that meal item is deleted when product is deleted."""
        meal_item = MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=100.0
        )
        
        product_id = test_product.id
        meal_item_id = meal_item.id
        
        # Delete the product
        test_product.delete()
        
        # Check that meal item is also deleted
        assert not MealItem.objects.filter(id=meal_item_id).exists()
        assert not Product.objects.filter(id=product_id).exists()
    
    def test_meal_item_quantity_precision(self, test_meal, test_product):
        """Test meal item quantity precision with decimal values."""
        meal_item = MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=123.456789
        )
        
        # Django FloatField should preserve precision
        assert meal_item.quantity == 123.456789
    
    def test_meal_item_zero_quantity(self, test_meal, test_product):
        """Test meal item with zero quantity."""
        meal_item = MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=0.0
        )
        
        assert meal_item.quantity == 0.0
    
    def test_meal_item_negative_quantity(self, test_meal, test_product):
        """Test meal item with negative quantity."""
        meal_item = MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=-50.0
        )
        
        assert meal_item.quantity == -50.0
    
    def test_meal_item_large_quantity(self, test_meal, test_product):
        """Test meal item with large quantity."""
        large_quantity = 999999.99
        meal_item = MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=large_quantity
        )
        
        assert meal_item.quantity == large_quantity
    
    def test_meal_item_multiple_items_same_meal(self, test_meal, test_product, test_product2):
        """Test multiple meal items for same meal."""
        meal_item1 = MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=100.0
        )
        meal_item2 = MealItem.objects.create(
            meal=test_meal,
            product=test_product2,
            quantity=200.0
        )
        
        # Both should exist
        assert MealItem.objects.filter(meal=test_meal).count() == 2
        assert meal_item1 in test_meal.items.all()
        assert meal_item2 in test_meal.items.all()
    
    def test_meal_item_same_product_different_meals(self, test_meal, test_meal2, test_product):
        """Test same product in different meals."""
        meal_item1 = MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=100.0
        )
        meal_item2 = MealItem.objects.create(
            meal=test_meal2,
            product=test_product,
            quantity=150.0
        )
        
        # Both should exist
        assert MealItem.objects.filter(product=test_product).count() == 2
        assert meal_item1 in test_product.meal_items.all()
        assert meal_item2 in test_product.meal_items.all()


# =========================================================
# PRODUCT READ SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestProductReadSerializer:
    """Tests for ProductReadSerializer functionality."""
    
    def test_product_read_serializer(self, test_product):
        """Test ProductReadSerializer for reading."""
        serializer = ProductReadSerializer(test_product)
        data = serializer.data
        
        assert data['id'] == str(test_product.id)
        assert data['name'] == test_product.name
        assert data['brand'] == test_product.brand
        assert data['barcode'] == test_product.barcode


# =========================================================
# MEAL ITEM SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestMealItemSerializer:
    """Tests for MealItemSerializer functionality."""
    
    def test_meal_item_serializer_read(self, test_meal_item):
        """Test MealItemSerializer for reading."""
        serializer = MealItemSerializer(test_meal_item)
        data = serializer.data
        
        assert data['id'] == str(test_meal_item.id)
        assert data['quantity'] == test_meal_item.quantity
        assert data['meal'] == test_meal_item.meal.id
        assert 'product' in data
        assert data['product']['id'] == str(test_meal_item.product.id)
        assert data['product']['name'] == test_meal_item.product.name
    
    def test_meal_item_serializer_nested_product(self, test_meal_item):
        """Test that nested product serializer is used."""
        serializer = MealItemSerializer(test_meal_item)
        data = serializer.data
        
        # Check that product data is properly nested
        assert isinstance(data['product'], dict)
        assert 'id' in data['product']
        assert 'name' in data['product']
        assert 'brand' in data['product']
        assert 'barcode' in data['product']


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
            'quantity': 150.0
        }
        
        serializer = MealItemWriteSerializer(data=data)
        assert serializer.is_valid()
        
        meal_item = serializer.save()
        assert meal_item.meal == test_meal
        assert meal_item.product == test_product
        assert meal_item.quantity == 150.0
    
    def test_meal_item_write_serializer_update(self, test_meal_item, test_product2):
        """Test MealItemWriteSerializer for update."""
        data = {
            'meal': test_meal_item.meal.id,
            'product': test_product2.barcode,
            'quantity': 250.0
        }
        
        serializer = MealItemWriteSerializer(test_meal_item, data=data)
        assert serializer.is_valid()
        
        updated_meal_item = serializer.save()
        assert updated_meal_item.product == test_product2
        assert updated_meal_item.quantity == 250.0
        assert updated_meal_item.meal == test_meal_item.meal
    
    def test_meal_item_write_serializer_validation_invalid_meal(self, test_product):
        """Test MealItemWriteSerializer validation with invalid meal."""
        data = {
            'meal': 99999,  # Non-existent meal
            'product': test_product.barcode,
            'quantity': 100.0
        }
        
        serializer = MealItemWriteSerializer(data=data)
        assert not serializer.is_valid()
        assert 'meal' in serializer.errors
    
    def test_meal_item_write_serializer_validation_invalid_product(self, test_meal):
        """Test MealItemWriteSerializer validation with invalid product."""
        data = {
            'meal': test_meal.id,
            'product': 'invalid_barcode',
            'quantity': 100.0
        }
        
        serializer = MealItemWriteSerializer(data=data)
        assert not serializer.is_valid()
        assert 'product' in serializer.errors
    
    def test_meal_item_write_serializer_validation_invalid_quantity(self, test_meal, test_product):
        """Test MealItemWriteSerializer validation with invalid quantity."""
        data = {
            'meal': test_meal.id,
            'product': test_product.barcode,
            'quantity': 'invalid_quantity'
        }
        
        serializer = MealItemWriteSerializer(data=data)
        assert not serializer.is_valid()
        assert 'quantity' in serializer.errors
    
    def test_meal_item_write_serializer_validation_missing_fields(self):
        """Test MealItemWriteSerializer validation with missing fields."""
        data = {}
        
        serializer = MealItemWriteSerializer(data=data)
        assert not serializer.is_valid()
        assert 'meal' in serializer.errors
        assert 'product' in serializer.errors
        assert 'quantity' in serializer.errors


# =========================================================
# MEAL ITEM VIEWSET TESTS
# =========================================================

@pytest.mark.django_db
class TestMealItemViewSet:
    """Tests for MealItemViewSet API endpoints."""
    
    def test_get_queryset(self, test_meal_item, api_factory, add_session_to_request):
        """Test get_queryset returns all meal items."""
        viewset = MealItemViewSet()
        request = api_factory.get('/api/meal-items/')
        request = add_session_to_request(request)
        
        # Set session data for user filtering
        request.session['sb_user_id'] = str(test_meal_item.meal.user.id)
        
        viewset.request = request
        queryset = viewset.get_queryset()
        
        assert queryset.count() == 1
        assert test_meal_item in queryset
    
    def test_get_serializer_class_create(self, api_factory, add_session_to_request):
        """Test serializer class selection for create action."""
        viewset = MealItemViewSet()
        request = api_factory.post('/api/meal-items/')
        request = add_session_to_request(request)
        
        viewset.request = request
        viewset.action = 'create'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class == MealItemWriteSerializer
    
    def test_get_serializer_class_list(self, api_factory, add_session_to_request):
        """Test serializer class selection for list action."""
        viewset = MealItemViewSet()
        request = api_factory.get('/api/meal-items/')
        request = add_session_to_request(request)
        
        viewset.request = request
        viewset.action = 'list'
        
        serializer_class = viewset.get_serializer_class()
        assert serializer_class == MealItemSerializer
    
    def test_create_method(self, test_meal, test_product):
        """Test create method with proper serialization using serializer directly."""
        # Test serializer creation directly instead of ViewSet
        data = {
            'meal': test_meal.id,
            'product': test_product.barcode,
            'quantity': 150.0
        }
        
        serializer = MealItemWriteSerializer(data=data)
        assert serializer.is_valid()
        
        meal_item = serializer.save()
        assert meal_item.meal == test_meal
        assert meal_item.product == test_product
        assert meal_item.quantity == 150.0
    
    def test_retrieve_method(self, test_meal_item):
        """Test retrieve method with proper serialization using serializer directly."""
        # Test serializer reading directly instead of ViewSet
        serializer = MealItemSerializer(test_meal_item)
        data = serializer.data
        
        assert data['id'] == str(test_meal_item.id)
        assert data['meal'] == test_meal_item.meal.id
        assert data['product']['id'] == str(test_meal_item.product.id)
        assert data['quantity'] == test_meal_item.quantity


# =========================================================
# INTEGRATION TESTS
# =========================================================

@pytest.mark.django_db
class TestMealItemIntegration:
    """Integration tests for meal item functionality."""
    
    def test_meal_item_through_meal(self, test_meal, test_product, test_product2):
        """Test accessing meal items through meal relationship."""
        # Create multiple meal items
        MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=100.0
        )
        MealItem.objects.create(
            meal=test_meal,
            product=test_product2,
            quantity=200.0
        )
        
        # Test accessing through meal
        meal_items = test_meal.items.all()
        assert meal_items.count() == 2
        
        # Test filtering by product
        product1_items = meal_items.filter(product=test_product)
        assert product1_items.count() == 1
        assert product1_items.first().product == test_product
    
    def test_meal_item_through_product(self, test_meal, test_meal2, test_product):
        """Test accessing meal items through product relationship."""
        # Create multiple meals with same product
        MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=100.0
        )
        MealItem.objects.create(
            meal=test_meal2,
            product=test_product,
            quantity=150.0
        )
        
        # Test accessing through product
        meal_items = test_product.meal_items.all()
        assert meal_items.count() == 2
        
        # Test filtering by meal
        meal1_items = meal_items.filter(meal=test_meal)
        assert meal1_items.count() == 1
        assert meal1_items.first().meal == test_meal
    
    def test_meal_item_serialization_roundtrip(self, test_meal, test_product):
        """Test serialization and deserialization roundtrip."""
        # Create meal item
        original_meal_item = MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=125.5
        )
        
        # Serialize
        read_serializer = MealItemSerializer(original_meal_item)
        data = read_serializer.data
        
        # Verify serialized data
        assert data['meal'] == test_meal.id
        assert data['product']['barcode'] == test_product.barcode
        assert data['quantity'] == 125.5
        
        # Create new meal item from serialized data (using different meal to avoid conflicts)
        meal2 = Meal.objects.create(
            user=test_meal.user,
            meal_type='dinner',
            name='Test Dinner'
        )
        
        write_data = {
            'meal': meal2.id,
            'product': test_product.barcode,
            'quantity': 175.0
        }
        
        write_serializer = MealItemWriteSerializer(data=write_data)
        assert write_serializer.is_valid()
        
        new_meal_item = write_serializer.save()
        assert new_meal_item.meal == meal2
        assert new_meal_item.product == original_meal_item.product
        assert new_meal_item.quantity == 175.0
    
    def test_meal_item_with_nutrition_data(self, test_meal, test_product):
        """Test meal item with nutrition data."""
        # Create meal item
        meal_item = MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=100.0
        )
        
        # Test that we can access product nutrition through meal item
        assert meal_item.product.name == test_product.name
        assert meal_item.product.barcode == test_product.barcode
        
        # Test quantity calculation
        assert meal_item.quantity == 100.0


# =========================================================
# EDGE CASES AND BOUNDARY TESTS
# =========================================================

@pytest.mark.django_db
class TestMealItemEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_meal_item_very_small_quantity(self, test_meal, test_product):
        """Test meal item with very small quantity."""
        small_quantity = 0.001
        meal_item = MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=small_quantity
        )
        
        assert meal_item.quantity == small_quantity
    
    def test_meal_item_very_large_quantity(self, test_meal, test_product):
        """Test meal item with very large quantity."""
        large_quantity = 999999999.99
        meal_item = MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=large_quantity
        )
        
        assert meal_item.quantity == large_quantity
    
    def test_meal_item_string_representation_edge_cases(self, test_meal, test_product):
        """Test string representation with edge case values."""
        # Test with very small quantity
        meal_item = MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=0.001
        )
        
        str_repr = str(meal_item)
        assert str(test_meal.id) in str_repr
        assert str(test_product.barcode) in str_repr  # Use barcode instead of ID
        assert '0.001' in str_repr
    
    def test_meal_item_duplicate_product_same_meal(self, test_meal, test_product):
        """Test multiple meal items with same product in same meal."""
        # This should be allowed based on the model (no unique_together constraint)
        meal_item1 = MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=100.0
        )
        meal_item2 = MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=200.0
        )
        
        # Both should exist
        assert MealItem.objects.filter(meal=test_meal, product=test_product).count() == 2
        assert meal_item1 in test_meal.items.all()
        assert meal_item2 in test_meal.items.all()
    
    def test_meal_item_unicode_product_name(self, test_meal, test_product):
        """Test meal item with unicode product name."""
        # Update product with unicode name
        test_product.name = "Test Product with Üñíçødé"
        test_product.save()
        
        meal_item = MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=100.0
        )
        
        # Test serialization with unicode
        serializer = MealItemSerializer(meal_item)
        data = serializer.data
        assert "Üñíçødé" in data['product']['name']


# =========================================================
# PERFORMANCE AND QUERY TESTS
# =========================================================

@pytest.mark.django_db
class TestMealItemPerformance:
    """Tests for performance and query optimization."""
    
    def test_meal_item_select_related(self, test_meal, test_product):
        """Test that select_related works properly for meal item queries."""
        MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=100.0
        )
        
        # Test select_related optimization
        meal_items = MealItem.objects.select_related('meal', 'product').all()
        for mi in meal_items:
            # Accessing related objects should not trigger additional queries
            _ = mi.meal.meal_type
            _ = mi.product.name
        
        # Verify that we can access the related objects
        assert len(meal_items) == 1
        assert meal_items[0].meal.meal_type == test_meal.meal_type
        assert meal_items[0].product.name == test_product.name
    
    def test_meal_item_bulk_operations(self, test_meal):
        """Test bulk operations with meal items."""
        # Create multiple products
        products = []
        for i in range(5):
            product = Product.objects.create(
                name=f'Product {i}',
                brand=f'Brand {i}',
                description=f'Description {i}',
                barcode=f'12345678{i}'
            )
            products.append(product)
        
        # Bulk create meal items
        meal_items = []
        for i, product in enumerate(products):
            meal_items.append(MealItem(
                meal=test_meal,
                product=product,
                quantity=100.0 + i * 10
            ))
        
        MealItem.objects.bulk_create(meal_items)
        
        # Verify all were created
        assert MealItem.objects.filter(meal=test_meal).count() == 5
        
        # Test bulk update
        MealItem.objects.filter(meal=test_meal).update(
            quantity=500.0
        )
        
        # Verify update
        for mi in MealItem.objects.filter(meal=test_meal):
            assert mi.quantity == 500.0
    
    def test_meal_item_ordering(self, test_meal, test_product):
        """Test meal item ordering by quantity."""
        # Create meal items with different quantities
        quantities = [300.0, 100.0, 200.0]
        
        for qty in quantities:
            MealItem.objects.create(
                meal=test_meal,
                product=test_product,
                quantity=qty
            )
        
        # Test ordering by quantity
        meal_items = MealItem.objects.filter(meal=test_meal).order_by('quantity')
        ordered_quantities = [mi.quantity for mi in meal_items]
        
        # Should be in ascending order
        assert ordered_quantities == sorted(quantities)
    
    def test_meal_item_filtering(self, test_meal, test_product, test_product2):
        """Test meal item filtering capabilities."""
        # Create meal items with different quantities
        MealItem.objects.create(
            meal=test_meal,
            product=test_product,
            quantity=100.0
        )
        MealItem.objects.create(
            meal=test_meal,
            product=test_product2,
            quantity=200.0
        )
        
        # Test filtering by quantity range
        small_items = MealItem.objects.filter(
            meal=test_meal,
            quantity__lt=150.0
        )
        assert small_items.count() == 1
        assert small_items.first().product == test_product
        
        # Test filtering by product
        product1_items = MealItem.objects.filter(
            meal=test_meal,
            product=test_product
        )
        assert product1_items.count() == 1
        assert product1_items.first().product == test_product
    
    def test_meal_item_aggregation(self, test_meal, test_product):
        """Test meal item aggregation functions."""
        # Create multiple meal items
        quantities = [100.0, 200.0, 300.0]
        for qty in quantities:
            MealItem.objects.create(
                meal=test_meal,
                product=test_product,
                quantity=qty
            )
        
        # Test aggregation
        from django.db.models import Sum, Avg, Count
        
        total_quantity = MealItem.objects.filter(meal=test_meal).aggregate(
            total=Sum('quantity')
        )['total']
        assert total_quantity == 600.0
        
        avg_quantity = MealItem.objects.filter(meal=test_meal).aggregate(
            average=Avg('quantity')
        )['average']
        assert avg_quantity == 200.0
        
        item_count = MealItem.objects.filter(meal=test_meal).aggregate(
            count=Count('id')
        )['count']
        assert item_count == 3
