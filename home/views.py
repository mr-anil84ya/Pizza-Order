from django.shortcuts import render,redirect
from home.models import Pizza
from home.models import *
from django.contrib import messages
from django.contrib.auth import login,authenticate,logout
from instamojo_wrapper import Instamojo
from django.conf import settings
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)
api = Instamojo(api_key=settings.API_KEY,
                auth_token=settings.AUTH_TOKEN, endpoint="https://test.instamojo.com/api/1.1/")
# Create your views here.
def home(request):
    pizzas = Pizza.objects.all()
    context = {'pizzas':pizzas}
    return render(request, "index.html", context)

def login_page(request):
    if request.method == "POST":
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user_obj = User.objects.filter(username = username)
            if not user_obj.exists():
                messages.error(request, "User not Found.")
                return redirect('/login/')
            user_obj = authenticate(username = username, password = password)
            if user_obj:
                login(request,user_obj)
                return redirect('/')
            messages.error(request, "password is wrong!")
            return redirect('/login/')
        except Exception as e:
            messages.error(request, "Something went Wrong.")
            return redirect('/login/')
    return render(request, "login.html")

#logout code
@login_required(login_url="/login/")
def logout_view(request):
    logout(request)
    return redirect('/login/')
def register_page(request):
    if request.method == "POST":
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            user_obj = User.objects.filter(username = username)
            if user_obj.exists():
                messages.error(request, "Username is Taken.")
                return redirect('/register/')
            user_obj = User.objects.create(username = username, email = email)
            user_obj.set_password(password)
            user_obj.save()
            messages.success(request, "Account Created!.")
            return redirect('/login/')
        except Exception as e:
            messages.error(request, "Something went Wrong.")
            return redirect('/register/')
    return render(request, "register.html")

@login_required(login_url="/login/")
def add_cart(request, pizza_uid):
    user = request.user
    print(user)
    pizza_obj = Pizza.objects.get(uid = pizza_uid)
    cart ,_ = Cart.objects.get_or_create(user = user ,is_paid = False)
    cart_items = CartItems.objects.create(
        cart = cart,
        pizza = pizza_obj,
    ) 
    return redirect('/')

# @login_required(login_url="/login/")
# def cart(request):
#     cart = Cart.objects.get(is_paid = False, user = request.user)
    
#     response = api.payment_request_create(
#         amount= cart.get_cart_total(),
#         purpose= "Orders",
#         buyer_name= request.user.username,
#         email= "ak7379jaiswal@gmail.com",
#         redirect_url="http://127.0.0.1:8000/success"
#     )
#     cart.instamojo_id = response['payment_request']['id']
#     cart.save()
#     context = {"carts": cart, "payment_url": response['payment_request']['longurl']}
#     print(response)
#     return render(request, "cart.html", context)

# @login_required(login_url="/login/")
# def remove_cart_items(request, cart_item_uid):
#     try:
#         CartItems.objects.get(uid = cart_item_uid).delete()
#         return redirect('/cart/')
#     except Exception as e:
#         print(e)

@login_required(login_url="/login/")
def cart(request):
    try:
        cart = Cart.objects.get(is_paid=False, user=request.user)
        # buyer_mail = Cart.objects.get(request.user.email)
        response = api.payment_request_create(
            amount=cart.get_cart_total(),
            purpose="Orders",
            buyer_name=request.user.username,
            email=request.user.email,
            redirect_url="http://127.0.0.1:8000/success"
        )
        
        # Debugging output to check the response structure
        logger.debug(f"Payment request response: {response}")

        # Check if 'payment_request' key exists in response
        if 'payment_request' in response:
            cart.instamojo_id = response['payment_request']['id']
            cart.save()
            context = {"carts": cart, "payment_url": response['payment_request']['longurl']}
            return render(request, "cart.html", context)
        else:
            logger.error(f"Key 'payment_request' not found in response: {response}")
            # Handle the error appropriately here, maybe show an error message to the user
            return render(request, "cart.html", {"error": "There was an error processing your payment. Please try again."})
    
    except Cart.DoesNotExist:
        logger.error("Cart not found for user: %s", request.user.username)
        # Handle the case where the cart does not exist
        return render(request, "cart.html", {"error": "No cart found."})
    
    except Exception as e:
        logger.exception("An error occurred in the cart view.")
        # Handle any other exceptions
        return render(request, "cart.html", {"error": "An unexpected error occurred. Please try again later."})

@login_required(login_url="/login/")
def remove_cart_items(request, cart_item_uid):
    try:
        CartItems.objects.get(uid=cart_item_uid).delete()
        return redirect('/orders/')
    except CartItems.DoesNotExist:
        logger.error(f"Cart item with UID {cart_item_uid} does not exist.")
        # Handle the case where the cart item does not exist
        return redirect('/cart/')
    except Exception as e:
        logger.exception(f"An error occurred while removing cart item {cart_item_uid}.")
        # Handle any other exceptions
        return redirect('/cart/')

@login_required(login_url="/login/")
def orders(request):
    orders = Cart.objects.filter(is_paid = True, user = request.user)
    context = {"orders":orders}

    return render(request, "orders.html", context)


@login_required(login_url="/login/")
def success(request):
    payment_request = request.GET.get('payment_request_id')
    paymentid = request.GET.get('payment_id')
    print(paymentid,"anil")
    cart = Cart.objects.get(instamojo_id = payment_request)
    cart.payment_id = paymentid
    cart.is_paid = True
    cart.save()
    return redirect('/orders/')