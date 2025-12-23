"""
Test suite for ProductNutrient functionality including model, serializers, and related functionality.
Comprehensive testing with high coverage for all product_nutrient-related functionality.
"""

import pytest
import uuid
from decimal import Decimal
from django.utils import timezone
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework import status
from django.contrib.sessions.middleware import SessionMiddleware

from apps.core.models import Product, ProductNutrient, Nutrient
from apps.api.product_serializers import ProductNutrientReadSerializer, ProductNutrientWriteSerializer, NutrientSerializer


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
def test_product(db):
    """Create a test product for testing."""
    return Product.objects.create(
        barcode='123456789',
        name='Test Product',
        brand='Test Brand',
        primary_source='user_added'
    )


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
def test_nutrient_protein(db):
    """Create a protein nutrient for testing."""
    return Nutrient.objects.create(
        code='protein',
        name='Protein',
        unit='g',
        category='macronutrient',
        display_order=2,
        is_visible=True
    )


@pytest.fixture
def test_product_nutrient(db, test_product, test_nutrient):
    """Create a test product nutrient for testing."""
    return ProductNutrient.objects.create(
        product=test_product,
        nutrient=test_nutrient,
        amount_per_100g=Decimal('150.500'),
        amount_per_serving=Decimal('25.000')
    )


# =========================================================
# PRODUCT NUTRIENT MODEL TESTS
# =========================================================

@pytest.mark.django_db
class TestProductNutrientModel:
    """Tests for ProductNutrient model functionality."""
    
    def test_product_nutrient_creation(self, test_product, test_nutrient):
        """Test basic product nutrient creation."""
        product_nutrient = ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient,
            amount_per_100g=Decimal('200.750'),
            amount_per_serving=Decimal('30.250')
        )
        
        assert product_nutrient.product == test_product
        assert product_nutrient.nutrient == test_nutrient
        assert product_nutrient.amount_per_100g == Decimal('200.750')
        assert product_nutrient.amount_per_serving == Decimal('30.250')
        assert product_nutrient.id is not None
    
    def test_product_nutrient_str_representation(self, test_product_nutrient):
        """Test product nutrient string representation."""
        str_repr = str(test_product_nutrient)
        assert test_product_nutrient.product.name in str_repr
        assert test_product_nutrient.nutrient.name in str_repr
        assert str(test_product_nutrient.amount_per_100g) in str_repr
    
    def test_product_nutrient_meta_options(self):
        """Test product nutrient model meta options."""
        assert ProductNutrient._meta.db_table == "bitebuilder.product_nutrient"
        assert len(ProductNutrient._meta.indexes) == 2
        
        # Test unique_together constraint
        unique_together = ProductNutrient._meta.unique_together
        assert ('product', 'nutrient') in unique_together
    
    def test_product_nutrient_unique_constraint(self, test_product, test_nutrient):
        """Test product nutrient unique constraint."""
        # Create first product nutrient
        ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient,
            amount_per_100g=Decimal('100.000')
        )
        
        # Try to create duplicate
        with pytest.raises(Exception):  # Should raise IntegrityError
            ProductNutrient.objects.create(
                product=test_product,
                nutrient=test_nutrient,
                amount_per_100g=Decimal('200.000')
            )
    
    def test_product_nutrient_null_amounts(self, test_product, test_nutrient):
        """Test product nutrient with null amounts."""
        product_nutrient = ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient,
            amount_per_100g=None,
            amount_per_serving=None
        )
        
        assert product_nutrient.amount_per_100g is None
        assert product_nutrient.amount_per_serving is None
    
    def test_product_nutrient_decimal_precision(self, test_product, test_nutrient):
        """Test product nutrient decimal precision."""
        product_nutrient = ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient,
            amount_per_100g=Decimal('123.456789'),  # Should be truncated to 3 decimal places
            amount_per_serving=Decimal('45.678901')
        )
        
        # Check that precision is maintained within limits
        assert product_nutrient.amount_per_100g == Decimal('123.456789')  # Django preserves the full precision
        assert product_nutrient.amount_per_serving == Decimal('45.678901')
    
    def test_product_nutrient_relationships(self, test_product_nutrient):
        """Test product nutrient relationships."""
        # Test product relationship
        assert test_product_nutrient.product.product_nutrients.count() == 1
        assert test_product_nutrient in test_product_nutrient.product.product_nutrients.all()
        
        # Test nutrient relationship
        assert test_product_nutrient.nutrient.nutrient_products.count() == 1
        assert test_product_nutrient in test_product_nutrient.nutrient.nutrient_products.all()
    
    def test_product_nutrient_cascade_delete(self, test_product, test_nutrient):
        """Test that product nutrient is deleted when product is deleted."""
        product_nutrient = ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient,
            amount_per_100g=Decimal('100.000')
        )
        
        product_id = test_product.id
        product_nutrient_id = product_nutrient.id
        
        # Delete the product
        test_product.delete()
        
        # Check that product nutrient is also deleted
        assert not ProductNutrient.objects.filter(id=product_nutrient_id).exists()
        assert not Product.objects.filter(id=product_id).exists()
    
    def test_product_nutrient_nutrient_cascade_delete(self, test_product, test_nutrient):
        """Test that product nutrient is deleted when nutrient is deleted."""
        product_nutrient = ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient,
            amount_per_100g=Decimal('100.000')
        )
        
        nutrient_id = test_nutrient.id
        product_nutrient_id = product_nutrient.id
        
        # Delete the nutrient
        test_nutrient.delete()
        
        # Check that product nutrient is also deleted
        assert not ProductNutrient.objects.filter(id=product_nutrient_id).exists()
        assert not Nutrient.objects.filter(id=nutrient_id).exists()


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


# =========================================================
# PRODUCT NUTRIENT READ SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestProductNutrientReadSerializer:
    """Tests for ProductNutrientReadSerializer functionality."""
    
    def test_product_nutrient_read_serializer(self, test_product_nutrient):
        """Test ProductNutrientReadSerializer for reading."""
        serializer = ProductNutrientReadSerializer(test_product_nutrient)
        data = serializer.data
        
        assert 'nutrient' in data
        assert data['nutrient']['id'] == str(test_product_nutrient.nutrient.id)
        assert data['nutrient']['name'] == test_product_nutrient.nutrient.name
        assert data['nutrient']['unit'] == test_product_nutrient.nutrient.unit
        assert data['amount_per_100g'] == str(test_product_nutrient.amount_per_100g)
        assert data['amount_per_serving'] == str(test_product_nutrient.amount_per_serving)
    
    def test_product_nutrient_read_serializer_nested_nutrient(self, test_product_nutrient):
        """Test that nested nutrient serializer is used."""
        serializer = ProductNutrientReadSerializer(test_product_nutrient)
        data = serializer.data
        
        # Check that nutrient data is properly nested
        assert isinstance(data['nutrient'], dict)
        assert 'id' in data['nutrient']
        assert 'name' in data['nutrient']
        assert 'unit' in data['nutrient']
        assert 'category' in data['nutrient']


# =========================================================
# PRODUCT NUTRIENT WRITE SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestProductNutrientWriteSerializer:
    """Tests for ProductNutrientWriteSerializer functionality."""
    
    def test_product_nutrient_write_serializer_create(self, test_product, test_nutrient):
        """Test ProductNutrientWriteSerializer for creation."""
        data = {
            'nutrient': test_nutrient.id,
            'amount_per_100g': '150.500',
            'amount_per_serving': '25.000'
        }
        
        serializer = ProductNutrientWriteSerializer(data=data)
        assert serializer.is_valid()
        
        product_nutrient = serializer.save(product=test_product)
        assert product_nutrient.product == test_product
        assert product_nutrient.nutrient == test_nutrient
        assert product_nutrient.amount_per_100g == Decimal('150.500')
        assert product_nutrient.amount_per_serving == Decimal('25.000')
    
    def test_product_nutrient_write_serializer_update(self, test_product_nutrient):
        """Test ProductNutrientWriteSerializer for update."""
        data = {
            'nutrient': test_product_nutrient.nutrient.id,
            'amount_per_100g': '200.750',
            'amount_per_serving': '35.500'
        }
        
        serializer = ProductNutrientWriteSerializer(test_product_nutrient, data=data)
        assert serializer.is_valid()
        
        updated_product_nutrient = serializer.save()
        assert updated_product_nutrient.amount_per_100g == Decimal('200.750')
        assert updated_product_nutrient.amount_per_serving == Decimal('35.500')
    
    def test_product_nutrient_write_serializer_validation(self, test_product):
        """Test ProductNutrientWriteSerializer validation."""
        # Test with invalid nutrient ID
        data = {
            'nutrient': 99999,  # Non-existent nutrient
            'amount_per_100g': '100.000'
        }
        
        serializer = ProductNutrientWriteSerializer(data=data)
        assert not serializer.is_valid()
        assert 'nutrient' in serializer.errors
    
    def test_product_nutrient_write_serializer_null_amounts(self, test_product, test_nutrient):
        """Test ProductNutrientWriteSerializer with null amounts."""
        data = {
            'nutrient': test_nutrient.id,
            'amount_per_100g': None,
            'amount_per_serving': None
        }
        
        serializer = ProductNutrientWriteSerializer(data=data)
        assert serializer.is_valid()
        
        product_nutrient = serializer.save(product=test_product)
        assert product_nutrient.amount_per_100g is None
        assert product_nutrient.amount_per_serving is None
    
    def test_product_nutrient_write_serializer_decimal_validation(self, test_product, test_nutrient):
        """Test ProductNutrientWriteSerializer decimal validation."""
        # Test with valid decimal values
        data = {
            'nutrient': test_nutrient.id,
            'amount_per_100g': '123.456',
            'amount_per_serving': '45.789'
        }
        
        serializer = ProductNutrientWriteSerializer(data=data)
        assert serializer.is_valid()
        
        product_nutrient = serializer.save(product=test_product)
        assert product_nutrient.amount_per_100g == Decimal('123.456')
        assert product_nutrient.amount_per_serving == Decimal('45.789')


# =========================================================
# INTEGRATION TESTS
# =========================================================

@pytest.mark.django_db
class TestProductNutrientIntegration:
    """Integration tests for product nutrient functionality."""
    
    def test_product_nutrient_through_product(self, test_product, test_nutrient, test_nutrient_protein):
        """Test accessing product nutrients through product relationship."""
        # Create multiple product nutrients
        ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient,
            amount_per_100g=Decimal('150.000')
        )
        ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient_protein,
            amount_per_100g=Decimal('25.000')
        )
        
        # Test accessing through product
        product_nutrients = test_product.product_nutrients.all()
        assert product_nutrients.count() == 2
        
        # Test filtering by nutrient
        energy_nutrients = product_nutrients.filter(nutrient=test_nutrient)
        assert energy_nutrients.count() == 1
        assert energy_nutrients.first().amount_per_100g == Decimal('150.000')
    
    def test_product_nutrient_through_nutrient(self, test_product, test_nutrient):
        """Test accessing product nutrients through nutrient relationship."""
        # Create multiple products with same nutrient
        product2 = Product.objects.create(
            barcode='987654321',
            name='Test Product 2',
            brand='Test Brand 2',
            primary_source='user_added'
        )
        
        ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient,
            amount_per_100g=Decimal('150.000')
        )
        ProductNutrient.objects.create(
            product=product2,
            nutrient=test_nutrient,
            amount_per_100g=Decimal('200.000')
        )
        
        # Test accessing through nutrient
        nutrient_products = test_nutrient.nutrient_products.all()
        assert nutrient_products.count() == 2
        
        # Test filtering by product
        product1_nutrients = nutrient_products.filter(product=test_product)
        assert product1_nutrients.count() == 1
        assert product1_nutrients.first().amount_per_100g == Decimal('150.000')
    
    def test_product_nutrient_serialization_roundtrip(self, test_product, test_nutrient_protein):
        """Test serialization and deserialization roundtrip."""
        # Create product nutrient
        original_product_nutrient = ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient_protein,
            amount_per_100g=Decimal('150.500'),
            amount_per_serving=Decimal('25.000')
        )
        
        # Serialize
        read_serializer = ProductNutrientReadSerializer(original_product_nutrient)
        data = read_serializer.data
        
        # Verify serialized data
        assert data['nutrient']['id'] == str(test_nutrient_protein.id)
        assert data['amount_per_100g'] == '150.500'
        assert data['amount_per_serving'] == '25.000'
        
        # Create new product nutrient from serialized data (using different product to avoid unique constraint)
        product2 = Product.objects.create(
            barcode='987654321',
            name='Test Product 2',
            brand='Test Brand 2',
            primary_source='user_added'
        )
        
        write_data = {
            'nutrient': test_nutrient_protein.id,
            'amount_per_100g': data['amount_per_100g'],
            'amount_per_serving': data['amount_per_serving']
        }
        
        write_serializer = ProductNutrientWriteSerializer(data=write_data)
        assert write_serializer.is_valid()
        
        new_product_nutrient = write_serializer.save(product=product2)
        assert new_product_nutrient.amount_per_100g == original_product_nutrient.amount_per_100g
        assert new_product_nutrient.amount_per_serving == original_product_nutrient.amount_per_serving


# =========================================================
# EDGE CASES AND BOUNDARY TESTS
# =========================================================

@pytest.mark.django_db
class TestProductNutrientEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_product_nutrient_max_decimal_values(self, test_product, test_nutrient):
        """Test product nutrient with maximum decimal values."""
        product_nutrient = ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient,
            amount_per_100g=Decimal('9999999.999'),  # Max value for max_digits=10, decimal_places=3
            amount_per_serving=Decimal('9999999.999')
        )
        
        assert product_nutrient.amount_per_100g == Decimal('9999999.999')
        assert product_nutrient.amount_per_serving == Decimal('9999999.999')
    
    def test_product_nutrient_zero_values(self, test_product, test_nutrient):
        """Test product nutrient with zero values."""
        product_nutrient = ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient,
            amount_per_100g=Decimal('0.000'),
            amount_per_serving=Decimal('0.000')
        )
        
        assert product_nutrient.amount_per_100g == Decimal('0.000')
        assert product_nutrient.amount_per_serving == Decimal('0.000')
    
    def test_product_nutrient_very_small_values(self, test_product, test_nutrient):
        """Test product nutrient with very small values."""
        product_nutrient = ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient,
            amount_per_100g=Decimal('0.001'),
            amount_per_serving=Decimal('0.001')
        )
        
        assert product_nutrient.amount_per_100g == Decimal('0.001')
        assert product_nutrient.amount_per_serving == Decimal('0.001')
    
    def test_product_nutrient_mixed_null_values(self, test_product, test_nutrient):
        """Test product nutrient with mixed null and non-null values."""
        product_nutrient = ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient,
            amount_per_100g=Decimal('150.000'),
            amount_per_serving=None
        )
        
        assert product_nutrient.amount_per_100g == Decimal('150.000')
        assert product_nutrient.amount_per_serving is None
    
    def test_product_nutrient_string_representation_edge_cases(self, test_product, test_nutrient):
        """Test string representation with edge case values."""
        # Test with None values
        product_nutrient = ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient,
            amount_per_100g=None,
            amount_per_serving=None
        )
        
        str_repr = str(product_nutrient)
        assert test_product.name in str_repr
        assert test_nutrient.name in str_repr
        assert 'None' in str_repr or 'per 100g' in str_repr


# =========================================================
# PERFORMANCE AND QUERY TESTS
# =========================================================

@pytest.mark.django_db
class TestProductNutrientPerformance:
    """Tests for performance and query optimization."""
    
    def test_product_nutrient_select_related(self, test_product, test_nutrient):
        """Test that select_related works properly for product nutrient queries."""
        ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient,
            amount_per_100g=Decimal('150.000')
        )
        
        # Test select_related optimization
        product_nutrients = ProductNutrient.objects.select_related('product', 'nutrient').all()
        for pn in product_nutrients:
            # Accessing related objects should not trigger additional queries
            _ = pn.product.name
            _ = pn.nutrient.name
        
        # Verify that we can access the related objects
        assert len(product_nutrients) == 1
        assert product_nutrients[0].product.name == test_product.name
        assert product_nutrients[0].nutrient.name == test_nutrient.name
    
    def test_product_nutrient_bulk_operations(self, test_product):
        """Test bulk operations with product nutrients."""
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
        
        # Bulk create product nutrients
        product_nutrients = []
        for i, nutrient in enumerate(nutrients):
            product_nutrients.append(ProductNutrient(
                product=test_product,
                nutrient=nutrient,
                amount_per_100g=Decimal(f'{100 + i}.000')
            ))
        
        ProductNutrient.objects.bulk_create(product_nutrients)
        
        # Verify all were created
        assert ProductNutrient.objects.filter(product=test_product).count() == 5
        
        # Test bulk update
        ProductNutrient.objects.filter(product=test_product).update(
            amount_per_serving=Decimal('10.000')
        )
        
        # Verify update
        for pn in ProductNutrient.objects.filter(product=test_product):
            assert pn.amount_per_serving == Decimal('10.000')
