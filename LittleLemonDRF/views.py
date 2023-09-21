from decimal import Decimal
from datetime import date
import random
from django.forms import ValidationError, model_to_dict
from django.shortcuts import get_list_or_404, get_object_or_404, render
from .models import Category, MenuItem, Cart, Order, OrderItem
from rest_framework.response import Response
from .serializers import MenuItemSerializer, UserSerializer , CartItemSerializer , OrderItemsSerializer
from rest_framework.decorators import api_view, action, permission_classes, throttle_classes
from .serializers import MenuItemSerializer 
from rest_framework import viewsets 
from rest_framework.permissions import IsAuthenticated



from django.contrib.auth.models import User, Group
# Create your views here.

class MenuItemViewset(viewsets.ModelViewSet):
    #declaring attributes
    queryset= MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields =['price', 'category']
    search_fields = ['title','category__title']
    permission_classes = [IsAuthenticated]
    
    #customizing actions
    def create(self, request):
        if request.user.groups.filter(name='Manager').exists():
            serialized = MenuItemSerializer(data=request.data)
            serialized.is_valid(raise_exception=True)
            serialized.save()
            return Response(serialized.data, status=201)
        else:
            return Response({'message':"You dont have the permission to create menu items"}, 403)
        
    def update(self, request, pk=None):
        if request.user.groups.filter(name='Manager').exists():
            instance = get_object_or_404(MenuItem, pk=pk)
            serialized = MenuItemSerializer(data=request.data, instance=instance)
            serialized.is_valid(raise_exception=True)
            serialized.save()
            return Response(serialized.data, status=201)
        else:
            return Response({'message':"You dont have the permission to update menu items"}, 403)
        
    def partial_update(self, request, pk=None):
        if request.user.groups.filter(name='Manager').exists():
            instance = get_object_or_404(MenuItem, pk=pk)
            serialized = MenuItemSerializer(data=request.data, instance=instance, partial=True)
            serialized.is_valid(raise_exception=True)
            serialized.save()
            return Response(serialized.data, status=201)
        else:
            return Response({'message':"You dont have the permission to partially update menu items"}, 403)
    
    def destroy(self, request, pk=None):
        if request.user.groups.filter(name='Manager').exists():
            try:
                menu_item = MenuItem.objects.get(pk=pk)
                menu_item.delete()
                return Response({'message':"Menu item deleted successfully."}, status=204)
            except MenuItem.DoesNotExist:
                return Response({'message':"Menu item does not exist."}, status=404)
        else:
            return Response({'message':"You dont have the permission to delete menu items."}, 403)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def managerAdminView(request):
    if request.user.groups.filter(name='Manager').exists():
        if request.method == "GET":
            managers = list(User.objects.filter(groups__name="Manager"))
            serialized_item = UserSerializer(managers, many=True)
            return Response(serialized_item.data, status=201) 
          
        elif request.method == "POST":
            instance = get_object_or_404(User, username=request.data['username'])
            if instance.groups.filter(name='Manager').exists() != True:
                manager = Group.objects.get(name='Manager')
                manager.user_set.add(instance)
            else:
                return Response({'message':'User is already a manager'}, status=404)
            serialized_instance = UserSerializer(instance)
            return Response(serialized_instance.data, status=201)
        
    else:    
        return Response({'message':"You dont have the permission for"}, status=403)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def managerAdminDeleteView(request, username):
    if request.user.groups.filter(name='Manager').exists():  
            user = get_object_or_404(User, username=username)
            manager = Group.objects.get(name='Manager')
            manager.user_set.remove(user)
            return Response({'message':'User succesfuly removed as a manager'}, status=200)
    else:
        return Response({'message':"You dont have the permission to remove this user as a manager"}, status=403)


@api_view(['POST','GET'])
@permission_classes([IsAuthenticated])
def deliveryCrewAdminView(request):
    if request.user.groups.filter(name='Manager').exists():
        if request.method == "GET":
            delivery_crew = list(User.objects.filter(groups__name="Delivery crew"))
            serialized_item = UserSerializer(delivery_crew, many=True)
            return Response(serialized_item.data, status=201) 
          
        elif request.method == "POST":
            instance = get_object_or_404(User, username=request.data['username'])
            if instance.groups.filter(name='Delivery crew').exists() != True:
                delivery_crew = Group.objects.get(name='Delivery crew')
                delivery_crew.user_set.add(instance)
            else:
                return Response({'message':'User is already in a delivery crew'}, status=404)
            serialized_instance = UserSerializer(instance)
            return Response(serialized_instance.data, status=201)
                   
    else:    
        return Response({'message':"You dont have the permission for this"}, status=403)
    
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deliveryCrewAdminDeleteView(request, username):   
    if request.user.groups.filter(name='Manager').exists():  
            user = get_object_or_404(User, username=username)
            manager = Group.objects.get(name='Delivery crew')
            manager.user_set.remove(user)
            return Response({'message':'User succesfuly removed as a delivery crew member'}, status=200)
    else:
        return Response({'message':"You dont have the permission to delete this user as a delivery crew member"}, status=403)



# Cart management 

@api_view(['POST','GET','DELETE'])
@permission_classes([IsAuthenticated])
def cartItemsView(request):
    if request.user.groups.filter(name='Customer').exists():
        if request.method == 'GET':
            user_cart = list(Cart.objects.prefetch_related('user','menuitem').filter(user=request.user))
            serialized_cart = CartItemSerializer(user_cart, many=True)
            return Response(serialized_cart.data, status=200)
        
        if request.method == 'POST':   
            item = request.data['menuitem_id']
            quantity = request.data['quantity']
            menuitem = MenuItem.objects.get(pk=item)
            user = request.user
            unit_price = Decimal(menuitem.price)
            price = unit_price * Decimal(quantity)
            cart = Cart(user=user, menuitem=menuitem, quantity=quantity, unit_price=unit_price, price=price)
            cart.save()
            serialized_cart = CartItemSerializer(cart)
            return Response(serialized_cart.data, status=201)

        if request.method == 'DELETE':   
            cart = get_list_or_404(Cart, user=request.user)
            for item in cart:
                item.delete()
            return Response({'message':'All cart items have been deleted. Cart empty'}, status=200)
        
    else:
        return Response({'message':'you dont have the permission for this'}, status=403)


class ManageOrdersViewset(viewsets.ModelViewSet):
    queryset = OrderItem.objects.select_related('order').all()
    serializer_class = OrderItemsSerializer
    permission_classes =[IsAuthenticated]
    ordering_fields =['user','delivery_crew','status','date']
    search_fields = ['delivery_crew__username', 'user__username', 'featured']

    def list(self, request):
        if request.user.groups.filter(name='Customer').exists():
            order = list(self.queryset.filter(order__user=request.user))
            serialized_order = OrderItemsSerializer(order, many=True)
            return Response(serialized_order.data, status=200)
        elif request.user.groups.filter(name='Manager').exists():
            orders = list(self.queryset)
            serialized_order = OrderItemsSerializer(orders, many=True)
            return Response(serialized_order.data, status=200)
        else:
            return Response({'message':'you dont have the permision to see these orders'}, status=403)
        
    def create(self, request):
        if request.user.groups.filter(name='Customer').exists():
            user=request.user
            cart = list(Cart.objects.filter(user=user))
            status = 0
            total = 0
            date1 = date.today()
            order = Order(user=user, total=total, date=date1, status=status)
            order.save()
            order_items = []
            for item in cart:
                menuitem = item.menuitem 
                quantity = item.quantity
                unit_price = item.unit_price
                price = item.price
                order_item = OrderItem(order=order, menuitem=menuitem, quantity=quantity, unit_price=unit_price, price=price)
                order_item.save()
                order.total += price
                order.save()
                order_items.append(order_item)
                item.delete()
            serialized_order = OrderItemsSerializer(order_items, many=True)
            return Response(serialized_order.data, status=200)           
        else:
            return Response({'message':'you dont have the permision to create an order'}, status=403)

    def retrieve(self, request, pk):
        if request.user.groups.filter(name='Customer').exists():
            order = Order.objects.get(pk=pk)
            if order.user == request.user:
                order_item = get_list_or_404(OrderItem, order=order)
                serialized_order_item = OrderItemsSerializer(order_item, many=True)
                return Response(serialized_order_item.data, status=200)
            else:
                return Response({'message':'you cant view this order because it belongs to another user'}, status=403)

    def update(self, request, pk):
        if request.user.groups.filter(name='Manager').exists():
            order = Order.objects.get(pk=pk)
            delivery_crew_id = request.data['delivery_crew']
            delivery_crew = User.objects.get(pk=delivery_crew_id)
            order.delivery_crew = delivery_crew
            delivery_status = request.data['status']
            order.status = delivery_status
            order.save()
            if order.delivery_crew:
                if order.status == '0':
                    return Response({'message':'The order is out for delivery'}, status=200)
                elif order.status == '1':
                    return Response({'message':'The order has been delivered'}, status=200)
            else:
                return Response({'message':'Kindly assign a delivery crew to the order'}, status=200)
        else:
            return Response({'message':'you dont have the permision to update this order'}, status=403)
        
    
    def partial_update(self, request, pk):
        if request.user.groups.filter(name='Manager').exists():
            order = Order.objects.get(pk=pk)
            delivery_crew_id = request.data['delivery_crew']
            delivery_crew = User.objects.get(pk=delivery_crew_id)
            order.delivery_crew = delivery_crew
            delivery_status = request.data['status']
            order.status = delivery_status
            order.save()
            if order.delivery_crew:
                if order.status == '0':
                    return Response({'message':'The order is out for delivery'}, status=200)
                elif order.status == '1':
                    return Response({'message':'The order has been delivered'}, status=200)
            else:
                return Response({'message':'Kindly assign a delivery crew to the order'}, status=200)
            
        elif request.user.groups.filter(name='Delivery crew').exists():
            order = Order.objects.get(pk=pk)            
            delivery_status = request.data['status']
            order.status = delivery_status
            order.save()
            if order.status == '0':
                return Response({'message':'The order is out for delivery'}, status=200)
            elif order.status == '1':
                return Response({'message':'The order has been delivered'}, status=200)
        else:
            return Response({'message':'you dont have the permision to update this order'}, status=403)

    def destroy(self, request, pk):
        if request.user.groups.filter(name='Manager').exists():
            order = get_object_or_404(Order, pk=pk)
            order.delete()
            return Response({'message':'Order has been succesfully deleted'}, status=200)
        else:
            return Response({'message':'you dont have the permision to delete this order'}, status=403)
 


