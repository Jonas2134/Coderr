from django_filters.rest_framework import FilterSet, NumberFilter

from offers_app.models import Offer


class OfferFilterSet(FilterSet):
    """
    FilterSet for querying Offer instances based on creator, price, and delivery time.

    Provides filters to:
      - Select offers by the creator’s user ID.
      - Limit offers to those at or below a maximum price.
      - Limit offers to those with a delivery time at or below a given threshold.

    Available filters:
        creator_id (int): Filters offers created by the given user ID.
        min_price (decimal): Filters offers whose `details.price` is less than
                             or equal to this value.
        max_delivery_time (int): Filters offers whose `details.delivery_time_in_days`
                                 is less than or equal to this value.
    """
    creator_id = NumberFilter(field_name='creator__id')
    min_price = NumberFilter(method='filter_min_price')
    max_delivery_time = NumberFilter(method='filter_max_delivery_time')

    class Meta:
        """
        Meta options for OfferFilterSet.

        Attributes:
            model (Model): The Django model to filter (Offer).
            fields (list): Names of filterable fields exposed by this FilterSet.
        """
        model = Offer
        fields = ["creator_id", "min_price", "max_delivery_time"]

    def filter_min_price(self, queryset, name, value):
        """
        Filter offers by maximum price.

        Args:
            queryset (QuerySet): Initial Offer queryset.
            name (str): Name of the filter ('min_price').
            value (decimal): The price ceiling to apply.

        Returns:
            QuerySet: Offers with details.price ≤ value.
        """
        return queryset.filter(details__price__lte=value)

    def filter_max_delivery_time(self, queryset, name, value):
        """
        Filter offers by maximum delivery time.

        Args:
            queryset (QuerySet): Initial Offer queryset.
            name (str): Name of the filter ('max_delivery_time').
            value (int): Maximum allowed delivery time in days.

        Returns:
            QuerySet: Offers with details.delivery_time_in_days ≤ value.
        """
        return queryset.filter(details__delivery_time_in_days__lte=value)
