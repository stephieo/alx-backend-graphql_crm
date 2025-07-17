import django_filters
from .models import Customer, Product, Order

#defining the filters for each model
class CustomerFilter(django_filters.FilterSet):
    phone_country_code = django_filters.CharFilter(field_name='phone', lookup_expr='iregex')
    class Meta:
        model = Customer
        fields = {
            'name': ['icontains'],
            'email': ['icontains'],
            'created_at': ['year__gte', 'year__lte','month__gte', 'month__lte']
        } 


class ProductFilter(django_filters.FilterSet):
    
    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],
            'price': ['gte', 'lte'],
            'stock': ['gte', 'lte']        
        }


class OrderFilter(django_filters.FilterSet):
    customer_name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    product_name = django_filters.CharFilter(method='filter_by_product_name')
    class Meta:
        model = Order
        fields = {
            'total_amount': ['gte','lte'],
            'order_date': ['year__gte', 'year__lte','month__gte', 'month__lte'],
            'customer_name': ['customer__name__icontains'],
            'product_name': ['product__name__icontains']
        }
        
        def filter_by_product_name(self, queryset, name, value):
            if value:
                return queryset.filter(products__name__icontains=value)
            return queryset