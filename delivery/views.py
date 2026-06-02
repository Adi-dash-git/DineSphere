from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

#from DineSphere.DineSphere import settings
from django.conf import settings

# from turtle import home
from .models import Cart, User
from .models import Restaurant, Item, Cart
#from django.contrib.admin.views.decorators import staff_member_required

import razorpay

# Create your views here.
def index(request):
    #return HttpResponse("Hello Django")
    return render(request, "index.html")


def open_signin(request):
    return render(request, 'signin.html')

def open_signup(request):
    return render(request, 'signup.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')

        # duplicate user not allowed
        if User.objects.filter(email=email).exists():
            return HttpResponse("This email is already registered. please use a diffrent email.")

        user = User(username=username, password = password, email = email, mobile = mobile, address = address)
        user.save()

        # return HttpResponse("Sign up Successful") 
        return render(request,'signin.html') 
    else:
        return HttpResponse("Invaild Response")


# def signin(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')


#     try:
#         User.objects.get(username = username, password = password)
#         if username == 'admin':
#             return render(request, 'admin_home.html')
#         else:
#             return render(request, 'customer_home.html')

#     except User.DoesNotExist:
#         return render(request, 'fail.html')

def signin(request):
    if request.method == 'POST':
        # Fetching data from the form
        username = request.POST.get('username')
        password = request.POST.get('password')

    #     try:
    #         # Check if a user exists with the provided credentials
    #         customer = User.objects.get(username=username, password=password)
    #         return render(request, 'success.html')
    #     except User.DoesNotExist:
    #         # If credentials are invalid, show a failure page
    #         return render(request, 'fail.html')
    # else:
    #     return HttpResponse("Invalid Request")
    try:
        User.objects.get(username = username, password = password)
        if username == "admin":
            #return render(request, 'admin_home.html')
            return admin_home(request)
        
        else:
            restaurantList = Restaurant.objects.all()
            return render(request, 'customer_home.html',{"restaurantList" : restaurantList, "username" : username})
             #return render(request, 'customer_home.html')
        
    except User.DoesNotExist:
        return render(request, 'fail.html')



def admin_home(request):
    total_users = User.objects.count()
    total_restaurants = Restaurant.objects.count()

    context = {
        'total_users': total_users,
        'total_restaurants': total_restaurants,
    }

    return render(request, 'admin_home.html', context)


def open_add_restaurant(request):
    return render(request, 'add_restaurants.html')





def add_restaurant(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')
        
        try:
            Restaurant.objects.get(name = name)
            return HttpResponse("Duplicate restaurant!")
            
        except:
            Restaurant.objects.create(
                name = name,
                picture = picture,
                cuisine = cuisine,
                rating = rating,
            )
    # return HttpResponse("Successfully Added !")        
    return render(request, 'admin_home.html')


def open_show_restaurant(request):    
    restaurantList = Restaurant.objects.all()    
    return render(request, 'show_restaurants.html',{"restaurantList" : restaurantList})



def open_update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    return render(request, 'update_restaurant.html', {"restaurant" : restaurant})

def update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')
        
        restaurant.name = name
        restaurant.picture = picture
        restaurant.cuisine = cuisine
        restaurant.rating = rating

        restaurant.save()

    restaurantList = Restaurant.objects.all()
    return render(request, 'show_restaurants.html',{"restaurantList" : restaurantList})

def delete_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    restaurant.delete()

    restaurantList = Restaurant.objects.all()
    return render(request, 'show_restaurants.html',{"restaurantList" : restaurantList})

def open_update_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    itemList = restaurant.items.all()
    #itemList = Item.objects.all()
    return render(request, 'update_menu.html',{"itemList" : itemList, "restaurant" : restaurant})

def update_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        vegeterian = request.POST.get('vegeterian') == 'on'
        picture = request.POST.get('picture')
        
        try:
            Item.objects.get(name = name)
            return HttpResponse("Duplicate item!")
        except:
            Item.objects.create(
                restaurant = restaurant,
                name = name,
                description = description,
                price = price,
                vegeterian = vegeterian,
                picture = picture,
            )
    return render(request, 'admin_home.html')

def view_menu(request, restaurant_id, username):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    itemList = restaurant.items.all()
    #itemList = Item.objects.all()
    return render(request, 'customer_menu.html'
                  ,{"itemList" : itemList,
                     "restaurant" : restaurant, 
                     "username":username})

# def show_cart(request, username):
#     customer = User.objects.get(username = username)
#     cart = Cart.objects.filter(customer = username)
#     items = cart.items.all() if cart else []
#     total_price = cart.total_price() if cart else 0

#     return render(request, 'cart.html', {"itemList": items, "total_price": total_price, "username": username})



def add_to_cart(request, item_id, username):
    item = Item.objects.get(id = item_id)
    customer = User.objects.get(username = username)

    cart, created = Cart.objects.get_or_create(customer = customer)

    cart.items.add(item)

    return HttpResponse('added to cart')



def show_cart(request, username):
    customer = User.objects.get(username = username)
    cart = Cart.objects.filter(customer=customer).first()
    items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0


    return render(request, 'cart.html',{"itemList" : items, "total_price" : total_price, "username":username})



def checkout(request, username):
    # featch customer & their cart
    customer = get_object_or_404(User, username=username)
    cart = Cart.objects.filter(customer=customer).first()
    cart_items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0
    
    if total_price == 0:
        return render(request, 'checkout.html', {
            'error': 'your cart is empty!',
        })
    
        # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


    # Create Razorpay order
    order_data = {
        'amount': int(total_price * 100),  # Amount in paisa
        'currency': 'INR',
        'payment_capture': '1',  # Automatically capture payment
    }
    order = client.order.create(data=order_data)


    # Pass the order details to the frontend
    return render(request, 'checkout.html', {
        'username': username,
        'cart_items': cart_items,
        'total_price': total_price,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order_id': order['id'],  # Razorpay order ID
        'amount': total_price,
    })
    



def orders(request):
    return render(request, 'orders.html')










# @staff_member_required
# def admin_home(request):
#     return render(request, 'delivery/admin_home.html')