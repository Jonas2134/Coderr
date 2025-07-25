from django_filters.rest_framework import FilterSet, NumberFilter

from offers_app.models import Offer


class OfferFilterSet(FilterSet):
    creator_id = NumberFilter(field_name='creator__id')
    min_price = NumberFilter(method='filter_min_price')
    max_delivery_time = NumberFilter(method='filter_max_delivery_time')

    class Meta:
        model = Offer
        fields = ["creator_id", "min_price", "max_delivery_time"]

    def filter_min_price(self, queryset, name, value):
        return queryset.filter(details__price__lte=value)

    def filter_max_delivery_time(self, queryset, name, value):
        return queryset.filter(details__delivery_time_in_days__lte=value)
