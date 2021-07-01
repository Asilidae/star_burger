from django.http import JsonResponse
from django.templatetags.static import static
import json

from .models import Product, Order, OrderProduct
from rest_framework.decorators import api_view
from .serializers import OrderSerializer
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
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
    order_data.is_valid()

    required_fields = ['firstname', 'lastname', 'phonenumber', 'address']
    for field_name in required_fields:
        field_value = order_data.data.get(field_name)
        if not field_value:
            return Response({'Error': f'Field {field_name} can\'t be null.'},
                            status=HTTP_400_BAD_REQUEST)
        elif not isinstance(field_value, str):
            return Response({'Error': f'Field {field_name} must be string.'},
                            status=HTTP_400_BAD_REQUEST)


    products = order_data.data.get('products')
    if not products:
        return Response({'Error': 'Got null products.'}, status=HTTP_400_BAD_REQUEST)
    if not isinstance(products, list):
        return Response({'Error': 'Wrong products type, list expected.'},
                        status=HTTP_400_BAD_REQUEST)

    for product_data in products:
        if isinstance(product_data, int):
            Product.objects.get(pk=product_data['product'])
        else:
            return Response({'Error': f'No such product: {product_data["product"]}'},
                            status=HTTP_404_NOT_FOUND)


    order = Order.objects.create(
        firstname=order_data.data['firstname'],
        lastname=order_data.data['lastname'],
        phonenumber=order_data.data['phonenumber'],
        address=order_data.data['address']
    )
    for product in order_data.data['products']:
        OrderProduct.objects.create(
            product=Product.objects.get(pk=product['product']),
            quantity=product['quantity'],
            order=order
        )

    return JsonResponse({})
