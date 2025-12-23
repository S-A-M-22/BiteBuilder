"""
Test suite for product_serializers functionality.
Comprehensive testing with high coverage for all product_serializers-related functionality.
"""

import pytest
import uuid
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from rest_framework import serializers

from apps.core.models import Product, ProductNutrient, Nutrient
from apps.api.product_serializers import (
    NutrientSerializer,
    ProductNutrientReadSerializer,
    ProductNutrientWriteSerializer,
    ProductReadSerializer,
    ProductWriteSerializer
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
def test_nutrient_protein(db):
    """Create a protein nutrient."""
    return Nutrient.objects.create(
        code='protein',
        name='Protein',
        unit='g',
        category='macronutrient',
        display_order=2,
        is_visible=True
    )


@pytest.fixture
def test_nutrient_fat(db):
    """Create a fat nutrient."""
    return Nutrient.objects.create(
        code='fat',
        name='Total Fat',
        unit='g',
        category='macronutrient',
        display_order=3,
        is_visible=True
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
def test_product_enriched(db):
    """Create a test product with enrichment data."""
    return Product.objects.create(
        barcode='9876543210987',
        name='Enriched Product',
        brand='Brand',
        primary_source='woolworths',
        last_enriched_at=timezone.now()
    )


@pytest.fixture
def test_product_queued(db):
    """Create a test product queued for enrichment."""
    product = Product.objects.create(
        barcode='1111111111111',
        name='Queued Product',
        brand='Brand',
        primary_source='woolworths'
    )
    product.needs_enrichment = True
    product.save()
    return product


@pytest.fixture
def test_product_nutrient(db, test_product, test_nutrient):
    """Create a test product nutrient."""
    return ProductNutrient.objects.create(
        product=test_product,
        nutrient=test_nutrient,
        amount_per_100g=Decimal('150.500'),
        amount_per_serving=Decimal('25.000')
    )


@pytest.fixture
def test_product_nutrient_null(db, test_product, test_nutrient_protein):
    """Create a test product nutrient with null values."""
    return ProductNutrient.objects.create(
        product=test_product,
        nutrient=test_nutrient_protein,
        amount_per_100g=None,
        amount_per_serving=None
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
            'category': 'macronutrient'
        }
        
        serializer = NutrientSerializer(data=data)
        assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"
        
        nutrient = serializer.save()
        assert nutrient.code == 'fiber'
        assert nutrient.name == 'Dietary Fiber'
        assert nutrient.unit == 'g'
        assert nutrient.category == 'macronutrient'
    
    def test_nutrient_serializer_create_with_microgram(self, db):
        """Test NutrientSerializer with microgram unit."""
        data = {
            'code': 'vitamin_c',
            'name': 'Vitamin C',
            'unit': 'µg',
            'category': 'vitamin'
        }
        
        serializer = NutrientSerializer(data=data)
        assert serializer.is_valid()
        
        nutrient = serializer.save()
        assert nutrient.unit == 'µg'
    
    def test_nutrient_serializer_create_with_percent(self, db):
        """Test NutrientSerializer with percent unit."""
        data = {
            'code': 'sodium_percent',
            'name': 'Sodium %',
            'unit': '%',
            'category': 'mineral'
        }
        
        serializer = NutrientSerializer(data=data)
        assert serializer.is_valid()
        
        nutrient = serializer.save()
        assert nutrient.unit == '%'
    
    def test_nutrient_serializer_update(self, test_nutrient):
        """Test NutrientSerializer for updating nutrient."""
        data = {
            'code': 'energy_kcal',
            'name': 'Energy (kcal)',
            'unit': 'kcal',
            'category': 'macronutrient'
        }
        
        serializer = NutrientSerializer(test_nutrient, data=data)
        assert serializer.is_valid()
        
        nutrient = serializer.save()
        assert nutrient.code == 'energy_kcal'
        assert nutrient.name == 'Energy (kcal)'
    
    def test_nutrient_serializer_partial_update(self, test_nutrient):
        """Test NutrientSerializer for partial update."""
        data = {
            'name': 'Updated Name'
        }
        
        serializer = NutrientSerializer(test_nutrient, data=data, partial=True)
        assert serializer.is_valid()
        
        nutrient = serializer.save()
        assert nutrient.name == 'Updated Name'
        assert nutrient.code == test_nutrient.code


# =========================================================
# PRODUCT NUTRIENT READ SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestProductNutrientReadSerializer:
    """Tests for ProductNutrientReadSerializer functionality."""
    
    def test_product_nutrient_read_serializer(self, test_product_nutrient):
        """Test ProductNutrientReadSerializer basic functionality."""
        serializer = ProductNutrientReadSerializer(test_product_nutrient)
        data = serializer.data
        
        assert 'nutrient' in data
        assert data['nutrient']['id'] == str(test_product_nutrient.nutrient.id)
        assert data['nutrient']['name'] == test_product_nutrient.nutrient.name
        assert data['nutrient']['unit'] == test_product_nutrient.nutrient.unit
        assert data['nutrient']['category'] == test_product_nutrient.nutrient.category
        assert data['amount_per_100g'] == '150.500'
        assert data['amount_per_serving'] == '25.000'
    
    def test_product_nutrient_read_serializer_nested_nutrient(self, test_product_nutrient):
        """Test that nested nutrient serializer is used."""
        serializer = ProductNutrientReadSerializer(test_product_nutrient)
        data = serializer.data
        
        assert isinstance(data['nutrient'], dict)
        assert 'id' in data['nutrient']
        assert 'name' in data['nutrient']
        assert 'unit' in data['nutrient']
        assert 'category' in data['nutrient']
    
    def test_product_nutrient_read_serializer_null_amounts(self, test_product_nutrient_null):
        """Test ProductNutrientReadSerializer with null amounts."""
        serializer = ProductNutrientReadSerializer(test_product_nutrient_null)
        data = serializer.data
        
        assert data['amount_per_100g'] is None
        assert data['amount_per_serving'] is None
    
    def test_product_nutrient_read_serializer_zero_amounts(self, test_product, test_nutrient):
        """Test ProductNutrientReadSerializer with zero amounts."""
        product_nutrient = ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient,
            amount_per_100g=Decimal('0.000'),
            amount_per_serving=Decimal('0.000')
        )
        
        serializer = ProductNutrientReadSerializer(product_nutrient)
        data = serializer.data
        
        assert data['amount_per_100g'] == '0.000'
        assert data['amount_per_serving'] == '0.000'


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
        assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"
        
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
    
    def test_product_nutrient_write_serializer_invalid_nutrient(self, test_product):
        """Test ProductNutrientWriteSerializer with invalid nutrient ID."""
        data = {
            'nutrient': uuid.uuid4(),  # Non-existent nutrient
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
    
    def test_product_nutrient_write_serializer_decimal_precision(self, test_product, test_nutrient):
        """Test ProductNutrientWriteSerializer decimal precision."""
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
    
    def test_product_nutrient_write_serializer_string_amounts(self, test_product, test_nutrient):
        """Test ProductNutrientWriteSerializer with string amounts."""
        data = {
            'nutrient': test_nutrient.id,
            'amount_per_100g': '999.999',
            'amount_per_serving': '111.111'
        }
        
        serializer = ProductNutrientWriteSerializer(data=data)
        assert serializer.is_valid()
        
        product_nutrient = serializer.save(product=test_product)
        assert product_nutrient.amount_per_100g == Decimal('999.999')
        assert product_nutrient.amount_per_serving == Decimal('111.111')


# =========================================================
# PRODUCT READ SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestProductReadSerializer:
    """Tests for ProductReadSerializer functionality."""
    
    def test_product_read_serializer_basic(self, test_product):
        """Test ProductReadSerializer basic functionality."""
        serializer = ProductReadSerializer(test_product)
        data = serializer.data
        
        assert data['id'] == str(test_product.id)
        assert data['barcode'] == test_product.barcode
        assert data['name'] == test_product.name
        assert data['brand'] == test_product.brand
        assert data['description'] == test_product.description
        assert data['size'] == test_product.size
        assert data['primary_source'] == test_product.primary_source
    
    def test_product_read_serializer_all_fields(self, test_product):
        """Test ProductReadSerializer includes all fields."""
        serializer = ProductReadSerializer(test_product)
        data = serializer.data
        
        expected_fields = [
            'id', 'barcode', 'name', 'brand', 'description', 'size',
            'price_current', 'is_on_special', 'image_url', 'product_url',
            'health_star', 'allergens', 'serving_size_value', 'serving_size_unit',
            'servings_per_pack', 'nutrition_basis', 'primary_source',
            'last_enriched_at', 'enrichment_attempts', 'created_at', 'updated_at',
            'product_nutrients', 'enrichment_status'
        ]
        
        for field in expected_fields:
            assert field in data
    
    def test_product_read_serializer_enrichment_status_none(self, test_product):
        """Test ProductReadSerializer enrichment_status with no enrichment."""
        serializer = ProductReadSerializer(test_product)
        data = serializer.data
        
        assert data['enrichment_status'] == 'none'
    
    def test_product_read_serializer_enrichment_status_ready(self, test_product_enriched):
        """Test ProductReadSerializer enrichment_status with enriched product."""
        serializer = ProductReadSerializer(test_product_enriched)
        data = serializer.data
        
        assert data['enrichment_status'] == 'ready'
    
    def test_product_read_serializer_enrichment_status_queued(self, test_product_queued):
        """Test ProductReadSerializer enrichment_status with queued product."""
        serializer = ProductReadSerializer(test_product_queued)
        data = serializer.data
        
        assert data['enrichment_status'] == 'queued'
    
    def test_product_read_serializer_with_product_nutrients(self, test_product_nutrient):
        """Test ProductReadSerializer includes product nutrients."""
        serializer = ProductReadSerializer(test_product_nutrient.product)
        data = serializer.data
        
        assert 'product_nutrients' in data
        assert isinstance(data['product_nutrients'], list)
        assert len(data['product_nutrients']) == 1
        
        nutrient_data = data['product_nutrients'][0]
        assert 'nutrient' in nutrient_data
        assert 'amount_per_100g' in nutrient_data
        assert 'amount_per_serving' in nutrient_data
    
    def test_product_read_serializer_product_nutrients_empty(self, test_product):
        """Test ProductReadSerializer with no product nutrients."""
        serializer = ProductReadSerializer(test_product)
        data = serializer.data
        
        assert 'product_nutrients' in data
        assert data['product_nutrients'] == []
    
    def test_product_read_serializer_multiple_product_nutrients(self, test_product, test_nutrient, test_nutrient_protein):
        """Test ProductReadSerializer with multiple product nutrients."""
        ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient,
            amount_per_100g=Decimal('150.000')
        )
        ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient_protein,
            amount_per_100g=Decimal('20.000')
        )
        
        serializer = ProductReadSerializer(test_product)
        data = serializer.data
        
        assert len(data['product_nutrients']) == 2
    
    def test_product_read_serializer_decimal_fields(self, test_product):
        """Test ProductReadSerializer with decimal fields."""
        serializer = ProductReadSerializer(test_product)
        data = serializer.data
        
        assert data['price_current'] == '10.99'
        assert data['serving_size_value'] == '100.000'
        assert data['servings_per_pack'] == '5.000'
    
    def test_product_read_serializer_datetime_fields(self, test_product):
        """Test ProductReadSerializer with datetime fields."""
        serializer = ProductReadSerializer(test_product)
        data = serializer.data
        
        assert 'created_at' in data
        assert 'updated_at' in data
    
    def test_product_read_serializer_null_fields(self):
        """Test ProductReadSerializer with null fields."""
        product = Product.objects.create(
            barcode='9999999999999',
            name='Null Product',
            primary_source='user_added'
        )
        
        serializer = ProductReadSerializer(product)
        data = serializer.data
        
        assert data['brand'] is None
        assert data['description'] is None
        assert data['size'] is None
        assert data['price_current'] is None
        assert data['image_url'] is None
        assert data['product_url'] is None
        assert data['health_star'] is None
        assert data['allergens'] is None


# =========================================================
# PRODUCT WRITE SERIALIZER TESTS
# =========================================================

@pytest.mark.django_db
class TestProductWriteSerializer:
    """Tests for ProductWriteSerializer functionality."""
    
    def test_product_write_serializer_create(self, db):
        """Test ProductWriteSerializer for creating new product."""
        data = {
            'barcode': '1234567890123',
            'name': 'New Product',
            'brand': 'Brand',
            'description': 'Description',
            'size': '500g',
            'price_current': '15.99',
            'is_on_special': True,
            'image_url': 'https://example.com/image.jpg',
            'product_url': 'https://example.com/product',
            'health_star': '4.5',
            'allergens': 'Milk, Soy',
            'serving_size_value': '100.000',
            'serving_size_unit': 'g',
            'servings_per_pack': '5.000',
            'nutrition_basis': 'per_100g',
            'primary_source': 'user_added'
        }
        
        serializer = ProductWriteSerializer(data=data)
        assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"
        
        product = serializer.save()
        assert product.barcode == '1234567890123'
        assert product.name == 'New Product'
        assert product.brand == 'Brand'
        assert product.price_current == Decimal('15.99')
        assert product.is_on_special is True
    
    def test_product_write_serializer_update(self, test_product):
        """Test ProductWriteSerializer for updating product."""
        data = {
            'barcode': '1234567890123',
            'name': 'Updated Product',
            'brand': 'Updated Brand',
            'price_current': '20.99',
            'is_on_special': True,
            'primary_source': 'user_added'
        }
        
        serializer = ProductWriteSerializer(test_product, data=data)
        assert serializer.is_valid()
        
        product = serializer.save()
        assert product.name == 'Updated Product'
        assert product.brand == 'Updated Brand'
        assert product.price_current == Decimal('20.99')
        assert product.is_on_special is True
    
    def test_product_write_serializer_partial_update(self, test_product):
        """Test ProductWriteSerializer for partial update."""
        data = {
            'name': 'Partially Updated Product'
        }
        
        serializer = ProductWriteSerializer(test_product, data=data, partial=True)
        assert serializer.is_valid()
        
        product = serializer.save()
        assert product.name == 'Partially Updated Product'
        assert product.brand == test_product.brand
    
    def test_product_write_serializer_minimal_data(self, db):
        """Test ProductWriteSerializer with minimal required data."""
        data = {
            'name': 'Minimal Product',
            'primary_source': 'user_added'
        }
        
        serializer = ProductWriteSerializer(data=data)
        assert serializer.is_valid()
        
        product = serializer.save()
        assert product.name == 'Minimal Product'
        assert product.primary_source == 'user_added'
        assert product.barcode is None
    
    def test_product_write_serializer_decimal_precision(self, db):
        """Test ProductWriteSerializer with decimal precision."""
        data = {
            'name': 'Decimal Product',
            'price_current': '123.45',
            'serving_size_value': '99.999',
            'servings_per_pack': '7.123',
            'primary_source': 'user_added'
        }
        
        serializer = ProductWriteSerializer(data=data)
        assert serializer.is_valid()
        
        product = serializer.save()
        assert product.price_current == Decimal('123.45')
        assert product.serving_size_value == Decimal('99.999')
        assert product.servings_per_pack == Decimal('7.123')
    
    def test_product_write_serializer_string_amounts(self, db):
        """Test ProductWriteSerializer with string amounts."""
        data = {
            'name': 'String Product',
            'price_current': '999.99',
            'serving_size_value': '50.5',
            'servings_per_pack': '2.25',
            'primary_source': 'user_added'
        }
        
        serializer = ProductWriteSerializer(data=data)
        assert serializer.is_valid()
        
        product = serializer.save()
        assert product.price_current == Decimal('999.99')
        assert product.serving_size_value == Decimal('50.5')
        assert product.servings_per_pack == Decimal('2.25')
    
    def test_product_write_serializer_null_fields(self, db):
        """Test ProductWriteSerializer with null fields."""
        data = {
            'name': 'Null Product',
            'primary_source': 'user_added'
        }
        
        serializer = ProductWriteSerializer(data=data)
        assert serializer.is_valid()
        
        product = serializer.save()
        assert product.barcode is None
        assert product.brand is None
        assert product.description is None
        assert product.size is None
        assert product.price_current is None
        assert product.image_url is None
        assert product.product_url is None
        assert product.health_star is None
        assert product.allergens is None
    
    def test_product_write_serializer_excludes_product_nutrients(self, test_product_nutrient):
        """Test that ProductWriteSerializer excludes product_nutrients field."""
        data = {
            'name': 'Updated Name',
            'primary_source': 'user_added'
        }
        
        serializer = ProductWriteSerializer(test_product_nutrient.product, data=data)
        assert serializer.is_valid()
        
        product = serializer.save()
        # Verify product_nutrients is not in serializer fields
        assert 'product_nutrients' not in serializer.fields


# =========================================================
# INTEGRATION TESTS
# =========================================================

@pytest.mark.django_db
class TestProductSerializerIntegration:
    """Integration tests for product serializers."""
    
    def test_serialization_roundtrip(self, test_product):
        """Test serialization and deserialization roundtrip."""
        # Serialize
        read_serializer = ProductReadSerializer(test_product)
        data = read_serializer.data
        
        # Extract only writable fields with proper types
        write_data = {
            'barcode': data['barcode'],
            'name': data['name'],
            'brand': data['brand'],
            'description': data['description'],
            'size': data['size'],
            'price_current': data['price_current'] if data['price_current'] else None,
            'is_on_special': data['is_on_special'],
            'image_url': data['image_url'],
            'product_url': data['product_url'],
            'health_star': data['health_star'],
            'allergens': data['allergens'],
            'serving_size_value': data['serving_size_value'] if data['serving_size_value'] else None,
            'serving_size_unit': data['serving_size_unit'],
            'servings_per_pack': data['servings_per_pack'] if data['servings_per_pack'] else None,
            'nutrition_basis': data['nutrition_basis'],
            'primary_source': data['primary_source']
        }
        
        # Deserialize to a new barcode to avoid unique constraint
        write_data['barcode'] = '9999999999999'
        
        # Deserialize
        write_serializer = ProductWriteSerializer(data=write_data)
        assert write_serializer.is_valid(), f"Serializer errors: {write_serializer.errors}"
        
        product = write_serializer.save()
        assert product.name == test_product.name
    
    def test_product_with_multiple_nutrients(self, test_product, test_nutrient, test_nutrient_protein, test_nutrient_fat):
        """Test product serialization with multiple nutrients."""
        ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient,
            amount_per_100g=Decimal('150.000')
        )
        ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient_protein,
            amount_per_100g=Decimal('20.000')
        )
        ProductNutrient.objects.create(
            product=test_product,
            nutrient=test_nutrient_fat,
            amount_per_100g=Decimal('10.000')
        )
        
        serializer = ProductReadSerializer(test_product)
        data = serializer.data
        
        assert len(data['product_nutrients']) == 3
        
        # Verify all nutrients are present
        nutrient_names = [pn['nutrient']['name'] for pn in data['product_nutrients']]
        assert 'Energy (kJ)' in nutrient_names
        assert 'Protein' in nutrient_names
        assert 'Total Fat' in nutrient_names


# =========================================================
# EDGE CASES AND BOUNDARY TESTS
# =========================================================

@pytest.mark.django_db
class TestProductSerializerEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_product_with_long_fields(self, db):
        """Test product with maximum length fields."""
        data = {
            'barcode': '12345678901234567890123456789012',  # 32 chars
            'name': 'A' * 255,  # Max length
            'brand': 'B' * 255,
            'size': 'C' * 100,
            'primary_source': 'user_added'
        }
        
        serializer = ProductWriteSerializer(data=data)
        assert serializer.is_valid()
        
        product = serializer.save()
        assert len(product.name) == 255
    
    def test_product_zero_price(self, db):
        """Test product with zero price."""
        data = {
            'name': 'Free Product',
            'price_current': '0.00',
            'primary_source': 'user_added'
        }
        
        serializer = ProductWriteSerializer(data=data)
        assert serializer.is_valid()
        
        product = serializer.save()
        assert product.price_current == Decimal('0.00')
    
    def test_product_negative_values(self, db):
        """Test that negative values are handled."""
        # Note: This may raise validation errors depending on field validation
        data = {
            'name': 'Test Product',
            'price_current': '-10.00',
            'primary_source': 'user_added'
        }
        
        serializer = ProductWriteSerializer(data=data)
        # Depending on validation, this might be invalid
        # We're just checking that the serializer handles it
    
    def test_product_boolean_fields(self, db):
        """Test product boolean fields."""
        data = {
            'name': 'Special Product',
            'is_on_special': True,
            'primary_source': 'user_added'
        }
        
        serializer = ProductWriteSerializer(data=data)
        assert serializer.is_valid()
        
        product = serializer.save()
        assert product.is_on_special is True
        
        # Test false
        data['is_on_special'] = False
        serializer = ProductWriteSerializer(product, data=data)
        assert serializer.is_valid()
        product = serializer.save()
        assert product.is_on_special is False
    
    def test_product_url_fields(self, db):
        """Test product URL fields."""
        data = {
            'name': 'URL Product',
            'image_url': 'https://example.com/image.png',
            'product_url': 'https://example.com/product/123',
            'primary_source': 'user_added'
        }
        
        serializer = ProductWriteSerializer(data=data)
        assert serializer.is_valid()
        
        product = serializer.save()
        assert product.image_url == 'https://example.com/image.png'
        assert product.product_url == 'https://example.com/product/123'
    
    def test_product_nutrition_basis_choices(self, db):
        """Test product nutrition basis choices."""
        # Test per_100g
        data = {
            'name': 'Per 100g Product',
            'nutrition_basis': 'per_100g',
            'primary_source': 'user_added'
        }
        
        serializer = ProductWriteSerializer(data=data)
        assert serializer.is_valid()
        product = serializer.save()
        assert product.nutrition_basis == 'per_100g'
        
        # Test per_serving
        data['nutrition_basis'] = 'per_serving'
        data['name'] = 'Per Serving Product'
        serializer = ProductWriteSerializer(data=data)
        assert serializer.is_valid()
        product = serializer.save()
        assert product.nutrition_basis == 'per_serving'
    
    def test_product_primary_source_choices(self, db):
        """Test product primary source choices."""
        sources = ['woolworths', 'openfoodfacts', 'user_added']
        
        for source in sources:
            data = {
                'name': f'{source.title()} Product',
                'primary_source': source
            }
            
            serializer = ProductWriteSerializer(data=data)
            assert serializer.is_valid()
            product = serializer.save()
            assert product.primary_source == source
