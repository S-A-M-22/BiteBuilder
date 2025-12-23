"""
Test suite for Products API functionality.

This module tests the ProductViewSet and related functionality including:
- Product listing and retrieval
- Product search
- Product saving and enrichment
- Preview enrichment
- Product details retrieval
"""

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from unittest.mock import patch, MagicMock
import json

from apps.core.models import Product, ProductNutrient, Nutrient
from django.test import override_settings, modify_settings

# Enable database access for all tests
pytestmark = pytest.mark.django_db

# Disable OTP middleware for tests
@pytest.fixture(autouse=True)
def disable_middleware():
    """Disable OTP middleware for all tests."""
    with override_settings(
        MIDDLEWARE=[
            m for m in [
                'django.middleware.security.SecurityMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.common.CommonMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
                'django.middleware.clickjacking.XFrameOptionsMiddleware',
                'corsheaders.middleware.CorsMiddleware',
            ]
        ]
    ):
        yield


@pytest.fixture
def api_client():
    """Create an API client for testing."""
    return APIClient()


@pytest.fixture
def test_product():
    """Create a test product."""
    return Product.objects.create(
        barcode="1234567890123",
        name="Test Product",
        brand="Test Brand",
        description="Test description",
        size="500g",
        price_current=10.99,
        is_on_special=False,
        primary_source="user_added"
    )


@pytest.fixture
def test_nutrient():
    """Create a test nutrient."""
    return Nutrient.objects.create(
        name="Energy",
        code="energy_kcal",
        unit="kcal",
        category="macronutrient"
    )


@pytest.fixture
def test_product_nutrient(test_product, test_nutrient):
    """Create a test product nutrient."""
    return ProductNutrient.objects.create(
        product=test_product,
        nutrient=test_nutrient,
        amount_per_100g=250.0,
        amount_per_serving=50.0
    )


class TestProductList:
    """Test product listing functionality."""

    def test_list_products_empty(self, api_client):
        """Test listing products when database is empty."""
        response = api_client.get('/api/products/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_list_products_with_items(self, api_client, test_product):
        """Test listing products with existing items."""
        response = api_client.get('/api/products/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == "Test Product"
        assert response.data[0]['barcode'] == "1234567890123"

    def test_list_products_limit_50(self, api_client):
        """Test that product list is limited to 50 items."""
        for i in range(60):
            Product.objects.create(
                barcode=f"123456789012{i}",
                name=f"Product {i}",
                primary_source="user_added"
            )
        response = api_client.get('/api/products/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 50

    def test_list_products_ordered_by_updated_at(self, api_client):
        """Test that products are ordered by updated_at descending."""
        Product.objects.create(barcode="111", name="First Product", primary_source="user_added")
        Product.objects.create(barcode="222", name="Second Product", primary_source="user_added")
        response = api_client.get('/api/products/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert response.data[0]['name'] == "Second Product"


class TestProductDetail:
    """Test product detail retrieval."""

    def test_get_product_detail_success(self, api_client, test_product):
        """Test retrieving product detail by barcode."""
        response = api_client.get(f'/api/products/{test_product.barcode}/detail/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == "Test Product"
        assert response.data['barcode'] == "1234567890123"

    def test_get_product_detail_not_found(self, api_client):
        """Test retrieving non-existent product."""
        response = api_client.get('/api/products/nonexistent/detail/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.data['error'].lower()

    def test_get_product_detail_with_nutrients(self, api_client, test_product, test_product_nutrient):
        """Test retrieving product with associated nutrients."""
        response = api_client.get(f'/api/products/{test_product.barcode}/detail/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['product_nutrients']) == 1
        assert float(response.data['product_nutrients'][0]['amount_per_100g']) == 250.0


class TestProductSearch:
    """Test product search functionality."""

    @patch('apps.core.views.products.fetch_woolies')
    def test_search_products_success(self, mock_fetch_woolies, api_client):
        """Test successful product search."""
        mock_fetch_woolies.return_value = [
            {"name": "Apple", "barcode": "123", "price": 2.50},
            {"name": "Banana", "barcode": "456", "price": 1.50}
        ]
        response = api_client.get('/api/products/search/?q=apple')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'ok'
        assert len(response.data['items']) == 2
        mock_fetch_woolies.assert_called_once_with('apple')

    def test_search_products_missing_query(self, api_client):
        """Test search with missing query parameter."""
        response = api_client.get('/api/products/search/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    @patch('apps.core.views.products.fetch_woolies')
    def test_search_products_api_error(self, mock_fetch_woolies, api_client):
        """Test search when API fails."""
        mock_fetch_woolies.side_effect = Exception("API Error")
        response = api_client.get('/api/products/search/?q=apple')
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data


class TestProductSave:
    """Test product save functionality."""

    def test_save_product_success(self, api_client):
        """Test successfully saving a new product."""
        payload = {"item": {
            "barcode": "9876543210987", "name": "New Product", "brand": "New Brand",
            "description": "New description", "size": "250g", "price_current": "5.99",
            "is_on_special": False, "image_url": "https://example.com/image.jpg",
            "product_url": "https://example.com/product", "health_star": "4",
            "allergens": "Milk, Gluten", "serving_size_value": "100", "serving_size_unit": "g",
            "servings_per_pack": "2.5", "nutrition_basis": "per_100g", "primary_source": "user_added",
            "nutrition": {"energy-kcal": {"label": "Energy", "per_100": {"value": 250, "unit": "kcal"},
                                          "per_serving": {"value": 50, "unit": "kcal"}}}
        }}
        response = api_client.post('/api/products/save/', data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == "New Product"
        product = Product.objects.get(barcode="9876543210987")
        assert product.name == "New Product"

    def test_save_product_missing_payload(self, api_client):
        """Test saving product with missing payload."""
        response = api_client.post('/api/products/save/', data={}, content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_save_product_with_nutrients(self, api_client):
        """Test saving product with nutrition data."""
        payload = {"item": {
            "barcode": "1112223334445", "name": "Nutritious Product", "primary_source": "user_added",
            "nutrition": {"energy-kcal": {"label": "Energy", "per_100": {"value": 300, "unit": "kcal"},
                                          "per_serving": {"value": 150, "unit": "kcal"}},
                         "protein": {"label": "Protein", "per_100": {"value": 20, "unit": "g"},
                                     "per_serving": {"value": 10, "unit": "g"}},
                         "fat": {"label": "Fat", "per_100": {"value": 10, "unit": "g"},
                                 "per_serving": {"value": 5, "unit": "g"}}}
        }}
        response = api_client.post('/api/products/save/', data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED
        product = Product.objects.get(barcode="1112223334445")
        assert ProductNutrient.objects.filter(product=product).count() == 3


class TestProductEnrich:
    """Test product enrichment functionality."""

    @patch('apps.services.fatsecret_enrichment.enrich_product_with_fatsecret')
    def test_enrich_product_success(self, mock_enrich, api_client, test_product):
        """Test successfully enriching a product."""
        mock_enrich.return_value = {
            "nutrition": {"protein": {"label": "Protein", "per_100": {"value": 25, "unit": "g"}}},
            "enrichment": {"fatsecret": {"source": "FatSecret API", "confidence": 0.95}}
        }
        response = api_client.post(f'/api/products/{test_product.barcode}/enrich/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'ok'
        assert 'provenance' in response.data

    def test_enrich_product_not_found(self, api_client):
        """Test enriching non-existent product."""
        response = api_client.post('/api/products/nonexistent/enrich/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch('apps.services.fatsecret_enrichment.enrich_product_with_fatsecret')
    def test_enrich_product_persists_nutrients(self, mock_enrich, api_client, test_product):
        """Test that enrichment persists nutrients to database."""
        mock_enrich.return_value = {
            "nutrition": {"protein": {"label": "Protein", "per_100": {"value": 30, "unit": "g"}}},
            "enrichment": {"fatsecret": {"source": "FatSecret API"}}
        }
        ProductNutrient.objects.filter(product=test_product).delete()
        response = api_client.post(f'/api/products/{test_product.barcode}/enrich/')
        assert response.status_code == status.HTTP_200_OK
        nutrients = ProductNutrient.objects.filter(product=test_product)
        assert nutrients.count() == 1
        assert nutrients.first().amount_per_100g == 30


class TestProductPreviewEnrich:
    """Test product preview enrichment functionality."""

    @patch('apps.services.fatsecret_enrichment.enrich_product_with_fatsecret')
    def test_preview_enrich_success(self, mock_enrich, api_client):
        """Test successful preview enrichment."""
        mock_enrich.return_value = {
            "nutrition": {"protein": {"label": "Protein", "per_100": {"value": 20, "unit": "g"}}},
            "enrichment": {"fatsecret": {"source": "FatSecret API"}}
        }
        payload = {"item": {"barcode": "9998887776665", "name": "Preview Product", "primary_source": "user_added"}}
        response = api_client.post('/api/products/preview-enrich/', data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'ok'
        assert 'enriched' in response.data
        assert response.data['enriched']['nutrition']['protein']['per_100']['value'] == 20

    def test_preview_enrich_missing_payload(self, api_client):
        """Test preview enrich with missing payload."""
        response = api_client.post('/api/products/preview-enrich/', data={}, content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    @patch('apps.services.fatsecret_enrichment.enrich_product_with_fatsecret')
    def test_preview_enrich_no_db_save(self, mock_enrich, api_client):
        """Test that preview enrich doesn't save to database."""
        mock_enrich.return_value = {
            "nutrition": {"protein": {"label": "Protein", "per_100": {"value": 15, "unit": "g"}}},
            "enrichment": {"fatsecret": {"source": "FatSecret API"}}
        }
        payload = {"item": {"barcode": "1111111111111", "name": "Temporary Product", "primary_source": "user_added"}}
        response = api_client.post('/api/products/preview-enrich/', data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_200_OK
        assert not Product.objects.filter(barcode="1111111111111").exists()


class TestProductSerializers:
    """Test product serializers."""

    def test_product_read_serializer(self, test_product, test_product_nutrient):
        """Test product read serializer."""
        from apps.api.product_serializers import ProductReadSerializer
        serializer = ProductReadSerializer(test_product)
        data = serializer.data
        assert data['name'] == "Test Product"
        assert data['barcode'] == "1234567890123"
        assert 'product_nutrients' in data
        assert len(data['product_nutrients']) == 1
        assert 'enrichment_status' in data

    def test_product_write_serializer_valid(self):
        """Test product write serializer with valid data."""
        from apps.api.product_serializers import ProductWriteSerializer
        data = {"barcode": "7778889990001", "name": "Written Product", "brand": "Written Brand",
                "size": "750g", "price_current": "12.50", "primary_source": "user_added"}
        serializer = ProductWriteSerializer(data=data)
        assert serializer.is_valid()

    def test_product_write_serializer_invalid(self):
        """Test product write serializer with invalid data."""
        from apps.api.product_serializers import ProductWriteSerializer
        serializer = ProductWriteSerializer(data={})
        assert not serializer.is_valid()


class TestProductEdgeCases:
    """Test edge cases and error handling."""

    def test_list_with_multiple_products(self, api_client):
        """Test listing multiple products."""
        for i in range(5):
            Product.objects.create(barcode=f"TEST{i:04d}", name=f"Product {i}", primary_source="user_added")
        response = api_client.get('/api/products/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_product_with_special_characters(self, api_client):
        """Test product with special characters in name."""
        Product.objects.create(barcode="SPECIAL123", name="Product & Co. - Special Edition!",
                              brand="Test & Brand", primary_source="user_added")
        response = api_client.get('/api/products/')
        assert response.status_code == status.HTTP_200_OK
        assert "Special Edition" in response.data[0]['name']

    def test_product_with_large_price(self, api_client):
        """Test product with large price value."""
        payload = {"item": {"barcode": "PRICE999", "name": "Expensive Product",
                           "price_current": "99999.99", "primary_source": "user_added"}}
        response = api_client.post('/api/products/save/', data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED
        assert float(response.data['price_current']) == 99999.99

    def test_product_with_empty_nutrition(self, api_client):
        """Test saving product with empty nutrition data."""
        payload = {"item": {"barcode": "EMPTY123", "name": "Product Without Nutrition",
                           "primary_source": "user_added", "nutrition": {}}}
        response = api_client.post('/api/products/save/', data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED
        product = Product.objects.get(barcode="EMPTY123")
        assert ProductNutrient.objects.filter(product=product).count() == 0

    def test_product_nutrient_unique_constraint(self, test_product, test_nutrient):
        """Test that product nutrients have unique constraint."""
        ProductNutrient.objects.create(product=test_product, nutrient=test_nutrient, amount_per_100g=100.0)
        ProductNutrient.objects.update_or_create(product=test_product, nutrient=test_nutrient, defaults={'amount_per_100g': 200.0})
        assert ProductNutrient.objects.filter(product=test_product, nutrient=test_nutrient).count() == 1


class TestProductDataIntegrity:
    """Test data integrity and relationships."""

    def test_cascade_delete_product_nutrients(self, test_product, test_nutrient):
        """Test that deleting product cascades to product nutrients."""
        ProductNutrient.objects.create(product=test_product, nutrient=test_nutrient, amount_per_100g=150.0)
        product_id = test_product.id
        test_product.delete()
        assert not ProductNutrient.objects.filter(product_id=product_id).exists()

    def test_nutrient_persists_after_product_delete(self, test_product, test_nutrient):
        """Test that nutrient remains after product deletion."""
        ProductNutrient.objects.create(product=test_product, nutrient=test_nutrient, amount_per_100g=150.0)
        nutrient_id = test_nutrient.id
        test_product.delete()
        assert Nutrient.objects.filter(id=nutrient_id).exists()

    def test_enrichment_status_calculation(self, api_client):
        """Test enrichment status field calculation."""
        product1 = Product.objects.create(barcode="NOENRICH", name="No Enrichment", primary_source="user_added")
        product2 = Product.objects.create(barcode="ENRICHED", name="Enriched Product",
                                          last_enriched_at=timezone.now(), primary_source="user_added")
        from apps.api.product_serializers import ProductReadSerializer
        data1 = ProductReadSerializer(product1).data
        data2 = ProductReadSerializer(product2).data
        assert data1['enrichment_status'] == 'none'
        assert data2['enrichment_status'] == 'ready' 