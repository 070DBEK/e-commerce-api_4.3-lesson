import json

import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name="category__id")
    min_price = django_filters.NumberFilter(
        field_name="price", lookup_expr="gte"
    )
    max_price = django_filters.NumberFilter(
        field_name="price", lookup_expr="lte"
    )
    attributes = django_filters.CharFilter(method="filter_attributes")

    class Meta:
        model = Product
        fields = ["category", "min_price", "max_price", "attributes"]

    def filter_attributes(self, queryset, name, value):
        try:
            attributes = json.loads(value)
            for key, val in attributes.items():
                queryset = queryset.filter(attributes__contains={key: val})
        except (json.JSONDecodeError, TypeError):
            pass
        return queryset
