import hashlib
import hmac
import random
from decimal import Decimal
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from products.models import Product
from .models import Cart, CartItem, PaymentTransaction

CART_SESSION_ID = 'cart'


def get_user_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


def _sort_and_build_query(params):
    sorted_items = sorted(params.items())
    return urlencode(sorted_items)


def _create_vnpay_secure_hash(params):
    hash_data = _sort_and_build_query(params)
    secret_key = settings.VNPAY_HASH_SECRET.encode('utf-8')
    return hmac.new(secret_key, hash_data.encode('utf-8'), hashlib.sha512).hexdigest()


def _verify_vnpay_response(input_data):
    vnp_secure_hash = input_data.get('vnp_SecureHash', '')
    data = {
        key: value
        for key, value in input_data.items()
        if key not in ['vnp_SecureHash', 'vnp_SecureHashType'] and value != ''
    }

    calculated_hash = _create_vnpay_secure_hash(data)
    return calculated_hash.lower() == vnp_secure_hash.lower()


def _update_transaction_from_vnpay(transaction, input_data):
    transaction.response_code = input_data.get('vnp_ResponseCode', '')
    transaction.transaction_no = input_data.get('vnp_TransactionNo', '')
    transaction.bank_code = input_data.get('vnp_BankCode', '')
    transaction.bank_tran_no = input_data.get('vnp_BankTranNo', '')
    transaction.pay_date = input_data.get('vnp_PayDate', '')
    transaction.raw_response = input_data
    transaction.save(update_fields=[
        'response_code',
        'transaction_no',
        'bank_code',
        'bank_tran_no',
        'pay_date',
        'raw_response',
        'updated_at',
    ])


def _mark_transaction_success(transaction, input_data):
    if transaction.status != PaymentTransaction.STATUS_SUCCESS:
        transaction.status = PaymentTransaction.STATUS_SUCCESS
        _update_transaction_from_vnpay(transaction, input_data)
        transaction.save(update_fields=['status', 'updated_at'])

        try:
            cart = transaction.user.cart
            cart.items.all().delete()
        except Cart.DoesNotExist:
            pass


def _mark_transaction_failed(transaction, input_data):
    if transaction.status == PaymentTransaction.STATUS_PENDING:
        transaction.status = PaymentTransaction.STATUS_FAILED
        _update_transaction_from_vnpay(transaction, input_data)
        transaction.save(update_fields=['status', 'updated_at'])


def cart_add(request, product_id):
    if not request.user.is_authenticated:
        return redirect(f"/accounts/login/?next=/cart/add/{product_id}/")

    product = get_object_or_404(Product, id=product_id)
    cart = get_user_cart(request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart_detail')


@login_required(login_url='login')
def cart_remove(request, product_id):
    cart = get_user_cart(request.user)
    product = get_object_or_404(Product, id=product_id)

    CartItem.objects.filter(cart=cart, product=product).delete()

    return redirect('cart_detail')


@login_required(login_url='login')
def cart_increase(request, product_id):
    cart = get_user_cart(request.user)
    product = get_object_or_404(Product, id=product_id)

    cart_item = get_object_or_404(CartItem, cart=cart, product=product)
    cart_item.quantity += 1
    cart_item.save()

    return redirect('cart_detail')


@login_required(login_url='login')
def cart_decrease(request, product_id):
    cart = get_user_cart(request.user)
    product = get_object_or_404(Product, id=product_id)

    cart_item = get_object_or_404(CartItem, cart=cart, product=product)
    cart_item.quantity -= 1

    if cart_item.quantity <= 0:
        cart_item.delete()
    else:
        cart_item.save()

    return redirect('cart_detail')


@login_required(login_url='login')
def cart_detail(request):
    cart = get_user_cart(request.user)
    cart_items = cart.items.select_related('product')

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, 'cart/detail.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })


@login_required(login_url='login')
def vnpay_payment(request):
    cart = get_user_cart(request.user)
    cart_items = cart.items.select_related('product')

    if not cart_items.exists():
        return redirect('cart_detail')

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if total_price <= 0:
        return redirect('cart_detail')

    now = timezone.localtime()
    txn_ref = f"{now.strftime('%Y%m%d%H%M%S')}{request.user.id}{random.randint(1000, 9999)}"
    order_info = f"Thanh toan don hang {txn_ref}"

    PaymentTransaction.objects.create(
        user=request.user,
        order_ref=txn_ref,
        amount=Decimal(total_price),
        status=PaymentTransaction.STATUS_PENDING,
        order_info=order_info,
    )

    vnp_params = {
        'vnp_Version': '2.1.0',
        'vnp_Command': 'pay',
        'vnp_TmnCode': settings.VNPAY_TMN_CODE,
        'vnp_Amount': int(total_price) * 100,
        'vnp_CurrCode': 'VND',
        'vnp_TxnRef': txn_ref,
        'vnp_OrderInfo': order_info,
        'vnp_OrderType': 'other',
        'vnp_Locale': 'vn',
        'vnp_ReturnUrl': request.build_absolute_uri(reverse('vnpay_return')),
        'vnp_IpAddr': _get_client_ip(request),
        'vnp_CreateDate': now.strftime('%Y%m%d%H%M%S'),
        'vnp_ExpireDate': (now + timezone.timedelta(minutes=15)).strftime('%Y%m%d%H%M%S'),
    }

    secure_hash = _create_vnpay_secure_hash(vnp_params)
    query_string = _sort_and_build_query(vnp_params)
    payment_url = f"{settings.VNPAY_PAYMENT_URL}?{query_string}&vnp_SecureHash={secure_hash}"

    return redirect(payment_url)


def vnpay_return(request):
    input_data = request.GET.dict()
    txn_ref = input_data.get('vnp_TxnRef', '')
    transaction = PaymentTransaction.objects.filter(order_ref=txn_ref).first()

    is_valid_checksum = _verify_vnpay_response(input_data) if input_data else False
    response_code = input_data.get('vnp_ResponseCode', '')
    transaction_status = input_data.get('vnp_TransactionStatus', '')
    amount_from_vnpay = int(input_data.get('vnp_Amount', '0') or 0)

    is_success = (
        transaction is not None and
        is_valid_checksum and
        response_code == '00' and
        transaction_status in ['', '00'] and
        amount_from_vnpay == int(transaction.amount) * 100
    )

    if transaction:
        if is_success:
            _mark_transaction_success(transaction, input_data)
        else:
            _mark_transaction_failed(transaction, input_data)

    return render(request, 'cart/payment_return.html', {
        'transaction': transaction,
        'is_valid_checksum': is_valid_checksum,
        'is_success': is_success,
        'response_code': response_code,
        'transaction_status': transaction_status,
        'input_data': input_data,
    })


def vnpay_ipn(request):
    input_data = request.GET.dict()

    if not input_data:
        return JsonResponse({'RspCode': '99', 'Message': 'Invalid input'})

    if not _verify_vnpay_response(input_data):
        return JsonResponse({'RspCode': '97', 'Message': 'Invalid checksum'})

    txn_ref = input_data.get('vnp_TxnRef', '')
    response_code = input_data.get('vnp_ResponseCode', '')
    transaction_status = input_data.get('vnp_TransactionStatus', '')
    amount_from_vnpay = int(input_data.get('vnp_Amount', '0') or 0)

    transaction = PaymentTransaction.objects.filter(order_ref=txn_ref).first()
    if not transaction:
        return JsonResponse({'RspCode': '01', 'Message': 'Order not found'})

    if amount_from_vnpay != int(transaction.amount) * 100:
        return JsonResponse({'RspCode': '04', 'Message': 'Invalid amount'})

    if transaction.status == PaymentTransaction.STATUS_SUCCESS:
        return JsonResponse({'RspCode': '02', 'Message': 'Order already confirmed'})

    if response_code == '00' and transaction_status in ['', '00']:
        _mark_transaction_success(transaction, input_data)
        return JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})

    _mark_transaction_failed(transaction, input_data)
    return JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})