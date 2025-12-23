"""
Test suite for FatSecret enrichment functionality.
Comprehensive testing for FatSecret API integration and product enrichment.
"""

import pytest
from unittest.mock import patch, MagicMock
import datetime
import json

from apps.services.fatsecret_enrichment import (
    extract_nutrients_from_fatsecret,
    enrich_product_with_fatsecret,
    FATSECRET_CANON_MAP
)
from apps.services.woolies_api import DEFAULT_NUTRIENT_UNITS


class TestExtractNutrientsFromFatsecret:
    """Tests for extract_nutrients_from_fatsecret function."""
    
    @patch('apps.services.fatsecret_enrichment.analyze_meal_text')
    def test_extract_nutrients_success(self, mock_analyze_meal_text):
        """Test successful nutrient extraction from FatSecret API."""
        # Mock successful API response
        mock_data = {
            "food_response": [
                {
                    "food_id": "12345",
                    "food_entry_name": "Apple",
                    "eaten": {
                        "total_nutritional_content": {
                            "calories": 52.0,
                            "carbohydrate": 14.0,
                            "protein": 0.3,
                            "fat": 0.2,
                            "fiber": 2.4,
                            "sugar": 10.0
                        }
                    },
                    "food": {
                        "food_id": "12345",
                        "food_name": "Apple",
                        "food_type": "fruit",
                        "food_url": "https://example.com/apple"
                    }
                }
            ]
        }
        mock_analyze_meal_text.return_value = mock_data
        
        result = extract_nutrients_from_fatsecret("apple")
        
        assert "nutrients" in result
        assert "provenance" in result
        assert len(result["nutrients"]) > 0
        assert len(result["provenance"]) == 1
        assert result["provenance"][0]["food_id"] == "12345"
        assert result["provenance"][0]["food_name"] == "Apple"
    
    @patch('apps.services.fatsecret_enrichment.analyze_meal_text')
    def test_extract_nutrients_no_data(self, mock_analyze_meal_text):
        """Test handling when API returns no data."""
        mock_analyze_meal_text.return_value = None
        
        result = extract_nutrients_from_fatsecret("nonexistent food")
        
        assert result == {"nutrients": {}, "provenance": []}
    
    @patch('apps.services.fatsecret_enrichment.analyze_meal_text')
    def test_extract_nutrients_empty_data(self, mock_analyze_meal_text):
        """Test handling when API returns empty data."""
        mock_analyze_meal_text.return_value = {}
        
        result = extract_nutrients_from_fatsecret("empty food")
        
        assert result == {"nutrients": {}, "provenance": []}
    
    @patch('apps.services.fatsecret_enrichment.analyze_meal_text')
    def test_extract_nutrients_no_food_response(self, mock_analyze_meal_text):
        """Test handling when API response has no food_response key."""
        mock_analyze_meal_text.return_value = {"other_key": "value"}
        
        result = extract_nutrients_from_fatsecret("invalid response")
        
        assert result == {"nutrients": {}, "provenance": []}
    
    @patch('apps.services.fatsecret_enrichment.analyze_meal_text')
    def test_extract_nutrients_invalid_values(self, mock_analyze_meal_text):
        """Test handling of invalid nutrient values."""
        mock_data = {
            "food_response": [
                {
                    "food_id": "12345",
                    "food_entry_name": "Invalid Food",
                    "eaten": {
                        "total_nutritional_content": {
                            "calories": "invalid",
                            "carbohydrate": None,
                            "protein": "not_a_number",
                            "fat": 0.2
                        }
                    },
                    "food": {
                        "food_id": "12345",
                        "food_name": "Invalid Food",
                        "food_type": "test",
                        "food_url": "https://example.com/invalid"
                    }
                }
            ]
        }
        mock_analyze_meal_text.return_value = mock_data
        
        result = extract_nutrients_from_fatsecret("invalid food")
        
        # Only valid numeric values should be included
        assert "fat" in result["nutrients"]
        assert "calories" not in result["nutrients"]
        assert "carbohydrate" not in result["nutrients"]
        assert "protein" not in result["nutrients"]
    
    @patch('apps.services.fatsecret_enrichment.analyze_meal_text')
    def test_extract_nutrients_missing_keys(self, mock_analyze_meal_text):
        """Test handling when food entries have missing keys."""
        mock_data = {
            "food_response": [
                {
                    "food_id": "12345",
                    "eaten": {},
                    "food": {}
                }
            ]
        }
        mock_analyze_meal_text.return_value = mock_data
        
        result = extract_nutrients_from_fatsecret("missing keys food")
        
        assert result["nutrients"] == {}
        assert len(result["provenance"]) == 1
        assert result["provenance"][0]["food_id"] == "12345"
    
    @patch('apps.services.fatsecret_enrichment.analyze_meal_text')
    def test_extract_nutrients_multiple_foods(self, mock_analyze_meal_text):
        """Test handling multiple food entries."""
        mock_data = {
            "food_response": [
                {
                    "food_id": "12345",
                    "food_entry_name": "Apple",
                    "eaten": {
                        "total_nutritional_content": {
                            "calories": 52.0,
                            "carbohydrate": 14.0
                        }
                    },
                    "food": {
                        "food_id": "12345",
                        "food_name": "Apple",
                        "food_type": "fruit",
                        "food_url": "https://example.com/apple"
                    }
                },
                {
                    "food_id": "67890",
                    "food_entry_name": "Banana",
                    "eaten": {
                        "total_nutritional_content": {
                            "calories": 89.0,
                            "protein": 1.1
                        }
                    },
                    "food": {
                        "food_id": "67890",
                        "food_name": "Banana",
                        "food_type": "fruit",
                        "food_url": "https://example.com/banana"
                    }
                }
            ]
        }
        mock_analyze_meal_text.return_value = mock_data
        
        result = extract_nutrients_from_fatsecret("apple and banana")
        
        assert len(result["provenance"]) == 2
        assert result["provenance"][0]["food_name"] == "Apple"
        assert result["provenance"][1]["food_name"] == "Banana"
        # Nutrients should be accumulated - check canonical keys
        assert "energy-kcal" in result["nutrients"]
        assert "carbohydrates" in result["nutrients"]
        assert "proteins" in result["nutrients"]
    
    @patch('apps.services.fatsecret_enrichment.analyze_meal_text')
    def test_extract_nutrients_canonical_mapping(self, mock_analyze_meal_text):
        """Test that nutrients are correctly mapped to canonical keys."""
        mock_data = {
            "food_response": [
                {
                    "food_id": "12345",
                    "food_entry_name": "Test Food",
                    "eaten": {
                        "total_nutritional_content": {
                            "calories": 100.0,
                            "carbohydrate": 25.0,
                            "protein": 5.0,
                            "fat": 2.0,
                            "saturated_fat": 1.0,
                            "polyunsaturated_fat": 0.5,
                            "monounsaturated_fat": 0.5,
                            "cholesterol": 10.0,
                            "sodium": 200.0,
                            "potassium": 300.0,
                            "fiber": 3.0,
                            "sugar": 15.0,
                            "vitamin_a": 50.0,
                            "vitamin_c": 20.0,
                            "calcium": 30.0,
                            "iron": 2.0
                        }
                    },
                    "food": {
                        "food_id": "12345",
                        "food_name": "Test Food",
                        "food_type": "test",
                        "food_url": "https://example.com/test"
                    }
                }
            ]
        }
        mock_analyze_meal_text.return_value = mock_data
        
        result = extract_nutrients_from_fatsecret("test food")
        
        # Check that all canonical mappings are applied
        expected_keys = [
            "energy-kcal", "carbohydrates", "proteins", "fat",
            "fat-saturated", "polyunsaturated-fat", "monounsaturated-fat",
            "cholesterol", "sodium", "potassium", "fiber",
            "carbohydrates-sugars", "vitamin-a", "vitamin-c", "calcium", "iron"
        ]
        
        for key in expected_keys:
            assert key in result["nutrients"]
            assert result["nutrients"][key]["per_100"]["value"] is not None
            assert result["nutrients"][key]["per_100"]["unit"] is not None
    
    @patch('apps.services.fatsecret_enrichment.analyze_meal_text')
    def test_extract_nutrients_unknown_nutrients(self, mock_analyze_meal_text):
        """Test that unknown nutrients are ignored."""
        mock_data = {
            "food_response": [
                {
                    "food_id": "12345",
                    "food_entry_name": "Test Food",
                    "eaten": {
                        "total_nutritional_content": {
                            "calories": 100.0,
                            "unknown_nutrient": 50.0,
                            "another_unknown": 25.0
                        }
                    },
                    "food": {
                        "food_id": "12345",
                        "food_name": "Test Food",
                        "food_type": "test",
                        "food_url": "https://example.com/test"
                    }
                }
            ]
        }
        mock_analyze_meal_text.return_value = mock_data
        
        result = extract_nutrients_from_fatsecret("test food")
        
        # Only known nutrients should be included
        assert "energy-kcal" in result["nutrients"]
        assert "unknown_nutrient" not in result["nutrients"]
        assert "another_unknown" not in result["nutrients"]


class TestEnrichProductWithFatsecret:
    """Tests for enrich_product_with_fatsecret function."""
    
    @patch('apps.services.fatsecret_enrichment.extract_nutrients_from_fatsecret')
    def test_enrich_product_success(self, mock_extract_nutrients):
        """Test successful product enrichment."""
        # Mock nutrient extraction
        mock_nutrients = {
            "energy-kcal": {"label": "energy-kcal", "per_100": {"value": 100.0, "unit": "kcal"}},
            "carbohydrates": {"label": "carbohydrates", "per_100": {"value": 25.0, "unit": "g"}}
        }
        mock_provenance = [{"food_id": "12345", "food_name": "Test Food"}]
        mock_extract_nutrients.return_value = {
            "nutrients": mock_nutrients,
            "provenance": mock_provenance
        }
        
        product = {
            "name": "Test Product",
            "nutrition": {}
        }
        
        result = enrich_product_with_fatsecret(product)
        
        assert "nutrition" in result
        assert "energy-kcal" in result["nutrition"]
        assert "carbohydrates" in result["nutrition"]
        assert "enrichment" in result
        assert "fatsecret" in result["enrichment"]
        assert result["enrichment"]["fatsecret"]["source_foods"] == mock_provenance
        assert result["enrichment"]["fatsecret"]["method"] == "fatsecret_nlp"
        assert "timestamp" in result["enrichment"]["fatsecret"]
    
    @patch('apps.services.fatsecret_enrichment.extract_nutrients_from_fatsecret')
    def test_enrich_product_no_name(self, mock_extract_nutrients):
        """Test handling when product has no name or description."""
        product = {"other_field": "value"}
        
        result = enrich_product_with_fatsecret(product)
        
        assert result == product
        mock_extract_nutrients.assert_not_called()
    
    @patch('apps.services.fatsecret_enrichment.extract_nutrients_from_fatsecret')
    def test_enrich_product_empty_name(self, mock_extract_nutrients):
        """Test handling when product has empty name."""
        product = {"name": "", "description": ""}
        
        result = enrich_product_with_fatsecret(product)
        
        assert result == product
        mock_extract_nutrients.assert_not_called()
    
    @patch('apps.services.fatsecret_enrichment.extract_nutrients_from_fatsecret')
    def test_enrich_product_no_nutrients_found(self, mock_extract_nutrients):
        """Test handling when no nutrients are found."""
        mock_extract_nutrients.return_value = {"nutrients": {}, "provenance": []}
        
        product = {"name": "Test Product"}
        
        result = enrich_product_with_fatsecret(product)
        
        assert result == product
        assert "enrichment" not in result
    
    @patch('apps.services.fatsecret_enrichment.extract_nutrients_from_fatsecret')
    def test_enrich_product_existing_nutrition(self, mock_extract_nutrients):
        """Test enrichment when product already has nutrition data."""
        mock_nutrients = {
            "energy-kcal": {"label": "energy-kcal", "per_100": {"value": 100.0, "unit": "kcal"}},
            "carbohydrates": {"label": "carbohydrates", "per_100": {"value": 25.0, "unit": "g"}}
        }
        mock_provenance = [{"food_id": "12345", "food_name": "Test Food"}]
        mock_extract_nutrients.return_value = {
            "nutrients": mock_nutrients,
            "provenance": mock_provenance
        }
        
        product = {
            "name": "Test Product",
            "nutrition": {
                "energy-kcal": {"label": "energy-kcal", "per_100": {"value": 50.0, "unit": "kcal"}},
                "protein": {"label": "protein", "per_100": {"value": 10.0, "unit": "g"}}
            }
        }
        
        result = enrich_product_with_fatsecret(product)
        
        # Existing nutrition should be preserved
        assert result["nutrition"]["energy-kcal"]["per_100"]["value"] == 50.0
        assert result["nutrition"]["protein"]["per_100"]["value"] == 10.0
        # New nutrients should be added
        assert result["nutrition"]["carbohydrates"]["per_100"]["value"] == 25.0
    
    @patch('apps.services.fatsecret_enrichment.extract_nutrients_from_fatsecret')
    def test_enrich_product_missing_per_100(self, mock_extract_nutrients):
        """Test enrichment when existing nutrition has missing per_100 values."""
        mock_nutrients = {
            "energy-kcal": {"label": "energy-kcal", "per_100": {"value": 100.0, "unit": "kcal"}},
            "carbohydrates": {"label": "carbohydrates", "per_100": {"value": 25.0, "unit": "g"}}
        }
        mock_provenance = [{"food_id": "12345", "food_name": "Test Food"}]
        mock_extract_nutrients.return_value = {
            "nutrients": mock_nutrients,
            "provenance": mock_provenance
        }
        
        product = {
            "name": "Test Product",
            "nutrition": {
                "energy-kcal": {"label": "energy-kcal", "per_100": None},
                "protein": {"label": "protein", "per_100": {"value": 10.0, "unit": "g"}}
            }
        }
        
        result = enrich_product_with_fatsecret(product)
        
        # Missing per_100 should be filled
        assert result["nutrition"]["energy-kcal"]["per_100"]["value"] == 100.0
        # Existing valid nutrition should be preserved
        assert result["nutrition"]["protein"]["per_100"]["value"] == 10.0
        # New nutrients should be added
        assert result["nutrition"]["carbohydrates"]["per_100"]["value"] == 25.0
    
    @patch('apps.services.fatsecret_enrichment.extract_nutrients_from_fatsecret')
    def test_enrich_product_uses_description_when_no_name(self, mock_extract_nutrients):
        """Test that function uses description when name is not available."""
        mock_extract_nutrients.return_value = {"nutrients": {}, "provenance": []}
        
        product = {"description": "Test Product Description"}
        
        result = enrich_product_with_fatsecret(product)
        
        mock_extract_nutrients.assert_called_once_with("Test Product Description")
    
    @patch('apps.services.fatsecret_enrichment.extract_nutrients_from_fatsecret')
    def test_enrich_product_existing_enrichment(self, mock_extract_nutrients):
        """Test enrichment when product already has enrichment data."""
        mock_nutrients = {
            "energy-kcal": {"label": "energy-kcal", "per_100": {"value": 100.0, "unit": "kcal"}}
        }
        mock_provenance = [{"food_id": "12345", "food_name": "Test Food"}]
        mock_extract_nutrients.return_value = {
            "nutrients": mock_nutrients,
            "provenance": mock_provenance
        }
        
        product = {
            "name": "Test Product",
            "enrichment": {
                "other_source": {"method": "other_method"}
            }
        }
        
        result = enrich_product_with_fatsecret(product)
        
        # Existing enrichment should be preserved
        assert "other_source" in result["enrichment"]
        assert result["enrichment"]["other_source"]["method"] == "other_method"
        # New enrichment should be added
        assert "fatsecret" in result["enrichment"]
        assert result["enrichment"]["fatsecret"]["method"] == "fatsecret_nlp"


class TestFatsecretEnrichmentIntegration:
    """Integration tests for FatSecret enrichment functionality."""
    
    @patch('apps.services.fatsecret_enrichment.analyze_meal_text')
    def test_full_enrichment_workflow(self, mock_analyze_meal_text):
        """Test complete enrichment workflow from API call to product update."""
        # Mock API response
        mock_data = {
            "food_response": [
                {
                    "food_id": "12345",
                    "food_entry_name": "Apple",
                    "eaten": {
                        "total_nutritional_content": {
                            "calories": 52.0,
                            "carbohydrate": 14.0,
                            "protein": 0.3,
                            "fat": 0.2
                        }
                    },
                    "food": {
                        "food_id": "12345",
                        "food_name": "Apple",
                        "food_type": "fruit",
                        "food_url": "https://example.com/apple"
                    }
                }
            ]
        }
        mock_analyze_meal_text.return_value = mock_data
        
        product = {
            "name": "Fresh Apple",
            "nutrition": {}
        }
        
        result = enrich_product_with_fatsecret(product)
        
        # Verify enrichment was successful
        assert "nutrition" in result
        assert "energy-kcal" in result["nutrition"]
        assert "carbohydrates" in result["nutrition"]
        assert "proteins" in result["nutrition"]
        assert "fat" in result["nutrition"]
        
        assert "enrichment" in result
        assert "fatsecret" in result["enrichment"]
        assert result["enrichment"]["fatsecret"]["method"] == "fatsecret_nlp"
        assert len(result["enrichment"]["fatsecret"]["source_foods"]) == 1
        assert result["enrichment"]["fatsecret"]["source_foods"][0]["food_name"] == "Apple"
    
    def test_fatsecret_canon_map_completeness(self):
        """Test that FATSECRET_CANON_MAP covers expected nutrients."""
        expected_nutrients = [
            "calories", "carbohydrate", "protein", "fat", "saturated_fat",
            "polyunsaturated_fat", "monounsaturated_fat", "cholesterol",
            "sodium", "potassium", "fiber", "sugar", "vitamin_a", "vitamin_c",
            "calcium", "iron"
        ]
        
        for nutrient in expected_nutrients:
            assert nutrient in FATSECRET_CANON_MAP
            assert FATSECRET_CANON_MAP[nutrient] is not None
            assert len(FATSECRET_CANON_MAP[nutrient]) > 0
    
    def test_canon_map_maps_to_valid_units(self):
        """Test that canonical mappings correspond to valid nutrient units."""
        # Check that canonical keys that exist in DEFAULT_NUTRIENT_UNITS are valid
        # Note: energy-kcal maps to energy-kj in the units, but the canonical key is still energy-kcal
        for fatsecret_key, canon_key in FATSECRET_CANON_MAP.items():
            if canon_key == "energy-kcal":
                # energy-kcal maps to energy-kj in units
                assert "energy-kj" in DEFAULT_NUTRIENT_UNITS
                assert DEFAULT_NUTRIENT_UNITS["energy-kj"] is not None
                assert len(DEFAULT_NUTRIENT_UNITS["energy-kj"]) > 0
            elif canon_key in DEFAULT_NUTRIENT_UNITS:
                # Only check keys that exist in DEFAULT_NUTRIENT_UNITS
                assert DEFAULT_NUTRIENT_UNITS[canon_key] is not None
                assert len(DEFAULT_NUTRIENT_UNITS[canon_key]) > 0
            # Note: Some canonical keys like vitamin-a, vitamin-c, iron may not be in DEFAULT_NUTRIENT_UNITS
            # This is expected as the units dictionary may not include all possible nutrients


class TestFatsecretEnrichmentEdgeCases:
    """Edge case tests for FatSecret enrichment functionality."""
    
    @patch('apps.services.fatsecret_enrichment.analyze_meal_text')
    def test_extract_nutrients_malformed_data(self, mock_analyze_meal_text):
        """Test handling of malformed API response data."""
        mock_analyze_meal_text.return_value = {
            "food_response": [
                {
                    "food_id": "12345",
                    "eaten": None,
                    "food": None
                }
            ]
        }
        
        result = extract_nutrients_from_fatsecret("malformed data")
        
        assert result["nutrients"] == {}
        assert len(result["provenance"]) == 1
        assert result["provenance"][0]["food_id"] == "12345"
    
    @patch('apps.services.fatsecret_enrichment.analyze_meal_text')
    def test_extract_nutrients_mixed_data_types(self, mock_analyze_meal_text):
        """Test handling of mixed data types in nutrient values."""
        mock_analyze_meal_text.return_value = {
            "food_response": [
                {
                    "food_id": "12345",
                    "food_entry_name": "Mixed Data Food",
                    "eaten": {
                        "total_nutritional_content": {
                            "calories": 100.0,
                            "carbohydrate": "25.5",
                            "protein": 5,
                            "fat": "invalid",
                            "fiber": None
                        }
                    },
                    "food": {
                        "food_id": "12345",
                        "food_name": "Mixed Data Food",
                        "food_type": "test",
                        "food_url": "https://example.com/mixed"
                    }
                }
            ]
        }
        
        result = extract_nutrients_from_fatsecret("mixed data food")
        
        # Only valid numeric values should be included
        assert "energy-kcal" in result["nutrients"]
        assert "carbohydrates" in result["nutrients"]
        assert "proteins" in result["nutrients"]
        assert "fat" not in result["nutrients"]  # "invalid" should be skipped
        assert "fiber" not in result["nutrients"]  # None should be skipped
    
    @patch('apps.services.fatsecret_enrichment.extract_nutrients_from_fatsecret')
    def test_enrich_product_none_nutrition(self, mock_extract_nutrients):
        """Test handling when product nutrition is None."""
        mock_nutrients = {
            "energy-kcal": {"label": "energy-kcal", "per_100": {"value": 100.0, "unit": "kcal"}}
        }
        mock_provenance = [{"food_id": "12345", "food_name": "Test Food"}]
        mock_extract_nutrients.return_value = {
            "nutrients": mock_nutrients,
            "provenance": mock_provenance
        }
        
        product = {
            "name": "Test Product",
            "nutrition": None
        }
        
        result = enrich_product_with_fatsecret(product)
        
        assert "nutrition" in result
        assert "energy-kcal" in result["nutrition"]
        assert result["nutrition"]["energy-kcal"]["per_100"]["value"] == 100.0
    
    @patch('apps.services.fatsecret_enrichment.extract_nutrients_from_fatsecret')
    def test_enrich_product_empty_nutrition(self, mock_extract_nutrients):
        """Test handling when product nutrition is empty dict."""
        mock_nutrients = {
            "energy-kcal": {"label": "energy-kcal", "per_100": {"value": 100.0, "unit": "kcal"}}
        }
        mock_provenance = [{"food_id": "12345", "food_name": "Test Food"}]
        mock_extract_nutrients.return_value = {
            "nutrients": mock_nutrients,
            "provenance": mock_provenance
        }
        
        product = {
            "name": "Test Product",
            "nutrition": {}
        }
        
        result = enrich_product_with_fatsecret(product)
        
        assert "nutrition" in result
        assert "energy-kcal" in result["nutrition"]
        assert result["nutrition"]["energy-kcal"]["per_100"]["value"] == 100.0
    
    @patch('apps.services.fatsecret_enrichment.extract_nutrients_from_fatsecret')
    def test_enrich_product_very_long_name(self, mock_extract_nutrients):
        """Test handling of very long product names."""
        mock_extract_nutrients.return_value = {"nutrients": {}, "provenance": []}
        
        long_name = "A" * 1000  # Very long name
        product = {"name": long_name}
        
        result = enrich_product_with_fatsecret(product)
        
        mock_extract_nutrients.assert_called_once_with(long_name)
        assert result == product  # No enrichment, so product unchanged
    
    @patch('apps.services.fatsecret_enrichment.extract_nutrients_from_fatsecret')
    def test_enrich_product_special_characters(self, mock_extract_nutrients):
        """Test handling of product names with special characters."""
        mock_extract_nutrients.return_value = {"nutrients": {}, "provenance": []}
        
        special_name = "Product with special chars: @#$%^&*()_+-=[]{}|;':\",./<>?"
        product = {"name": special_name}
        
        result = enrich_product_with_fatsecret(product)
        
        mock_extract_nutrients.assert_called_once_with(special_name)
        assert result == product  # No enrichment, so product unchanged
    
    @patch('apps.services.fatsecret_enrichment.extract_nutrients_from_fatsecret')
    def test_enrich_product_unicode_name(self, mock_extract_nutrients):
        """Test handling of product names with unicode characters."""
        mock_extract_nutrients.return_value = {"nutrients": {}, "provenance": []}
        
        unicode_name = "产品名称 with unicode: 中文测试 🍎🥕🥬"
        product = {"name": unicode_name}
        
        result = enrich_product_with_fatsecret(product)
        
        mock_extract_nutrients.assert_called_once_with(unicode_name)
        assert result == product  # No enrichment, so product unchanged
