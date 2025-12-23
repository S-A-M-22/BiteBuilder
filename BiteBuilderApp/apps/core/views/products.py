from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import models

from apps.api.product_serializers import ProductReadSerializer, ProductWriteSerializer
from apps.core.models import Product, ProductNutrient, Nutrient, SavedProduct
from apps.services.woolies_api import fetch_woolies


CANONICAL_MAP = {
    "energy-kj": "energy_kj",
    "energy-kcal": "energy_kcal",
    "protein": "protein",
    "fat": "fat_total",
    "fat-saturated": "fat_saturated",
    "carbohydrates": "carbohydrate",
    "carbohydrates-sugars": "sugars",
    "fiber": "fiber",
    "sodium": "sodium",
    "calcium": "calcium",
    "potassium": "potassium",
    "cholesterol": "cholesterol",
    "iron": "iron",
    "magnesium": "magnesium",
    "vitamin-c": "vitamin_c",
    "vitamin-d": "vitamin_d",
    "vitamin-b12": "vitamin_b12",
    "zinc": "zinc",
}

class ProductViewSet(viewsets.ModelViewSet):
    """
    Hijacked behavior:
    /api/products/ → return only the current user’s saved products.
    /api/products/save → create global product + save link.
    All other endpoints unchanged.
    """

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ProductWriteSerializer
        return ProductReadSerializer

    # 🔹 Fetch only products the current user has saved
    def get_queryset(self):
        user_id = self.request.session.get("sb_user_id")
        if not user_id:
            return Product.objects.none()
        return Product.objects.filter(saved_by_users__user_id=user_id).order_by("-updated_at")

    # 🔹 No need for perform_create — users save via /save
    def perform_create(self, serializer):
        pass

    # 🔹 Return saved products (for “My Foods”)
    def list(self, request):
        queryset = self.get_queryset().select_related()
        serializer = ProductReadSerializer(queryset, many=True)
        return Response(serializer.data)

    # 🔹 External search (unchanged)
    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        term = request.query_params.get("q")
        if not term:
            return Response({"error": "Missing query"}, status=400)
        try:
            results = fetch_woolies(term)
            return Response({"status": "ok", "items": results})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    # 🔹 Product detail (still by barcode)
    @action(detail=True, methods=["get"], url_path="detail")
    def get_detail(self, request, pk=None):
        product = get_object_or_404(
            Product.objects.prefetch_related("product_nutrients__nutrient"), barcode=pk
        )
        return Response(ProductReadSerializer(product).data)

    # 🔹 Save product (create global entry + SavedProduct link)
    @action(detail=False, methods=["post"], url_path="save")
    def save(self, request):
        user_id = request.session.get("sb_user_id")
        if not user_id:
            return Response(
                {"error": "User not authenticated"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        payload = request.data.get("item")
        if not payload:
            return Response({"error": "Missing product payload"}, status=400)

        # Validate and extract
        write_serializer = ProductWriteSerializer(data=payload)
        write_serializer.is_valid(raise_exception=True)
        validated = write_serializer.validated_data
        barcode = validated.get("barcode")

        json_fields = {"product_url": payload.get("product_url")}

        # Create or update global product
        product, _ = Product.objects.update_or_create(
            barcode=barcode,
            defaults={
                **validated,
                **json_fields,
                "last_enriched_at": timezone.now(),
            },
        )

        # Rebuild nutrients
        ProductNutrient.objects.filter(product=product).delete()
        for key, entry in (payload.get("nutrition") or {}).items():
            if not entry or key not in CANONICAL_MAP:
                continue

            code = CANONICAL_MAP[key]
            nutrient, _ = Nutrient.objects.get_or_create(
                code=code,
                defaults={
                    "name": entry.get("label") or code,
                    "unit": ((entry.get("per_100") or {}).get("unit") or "g"),
                    "category": "macronutrient",
                },
            )

            per_100g = (entry.get("per_100") or {}).get("value")
            per_serving = (entry.get("per_serving") or {}).get("value")
            if per_100g is None and per_serving is None:
                continue

            ProductNutrient.objects.create(
                product=product,
                nutrient=nutrient,
                amount_per_100g=per_100g,
                amount_per_serving=per_serving,
            )

        # Link user ↔ product
        SavedProduct.objects.get_or_create(user_id=user_id, product=product)

        return Response(ProductReadSerializer(product).data, status=status.HTTP_201_CREATED)
