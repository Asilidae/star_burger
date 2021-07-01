from django.http import JsonResponse
from django.templatetags.static import static
import json

from .models import Product, Order, OrderProduct
from rest_framework.decorators import api_view
from .serializers import OrderSerializer
from rest_framework.response import Response


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    order_data = OrderSerializer(data=request.data)
    order_data.is_valid(raise_exception=True)
    order = Order.objects.create(
        firstname=order_data.validated_data['firstname'],
        lastname=order_data.validated_data['lastname'],
        phonenumber=order_data.validated_data['phonenumber'],
        address=order_data.validated_data['address']
    )
    for product in order_data.validated_data['products']:
        OrderProduct.objects.create(
            product=product['product'],
            quantity=product['quantity'],
            order=order,
            total_price=product['product'].price * product['quantity']
        )
    order_serializer = OrderSerializer(order)
    return Response(order_serializer.data, status=201)
