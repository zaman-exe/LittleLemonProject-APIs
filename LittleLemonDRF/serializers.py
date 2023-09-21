from rest_framework import serializers
from .models import MenuItem, Category, Order ,Cart , OrderItem
from django.contrib.auth.models import User, Group
from rest_framework.validators import UniqueTogetherValidator


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only = True)
    category_id = serializers.IntegerField(write_only = True)
    
    class Meta:
       model = MenuItem
       fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']   

class UserSerializer(serializers.ModelSerializer):  
    class Meta:
        model = User
        fields = ['username'] 

class CartItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    quantity = serializers.IntegerField()
    
    def validate(self, attrs, initial_data):
        attrs['menuitem'] = initial_data.menuitem
        attrs['menuitem_id'] = initial_data.menuitem_id
        attrs['quantity'] = initial_data.quantity
        return attrs
    
    class Meta:
        model = Cart
        fields = ['menuitem','quantity','price','menuitem_id']     
        depth = 2           
        validators = UniqueTogetherValidator(
            queryset=Cart.objects.all,
            fields=['order', 'menuitem']
        )

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    delivery_crew =UserSerializer(read_only=True)
    status =serializers.SerializerMethodField(method_name='get_status')

    def get_status(self, initial_data):
        if initial_data.status == '0':
            delivery_status = 'The order is out for delivery'
            return delivery_status
        elif initial_data.status == '1':
            delivery_status = 'The order has been delivered'
            return delivery_status

    class Meta:
        model = Order
        fields =['user','delivery_crew','status','total','date']   
        
class OrderItemsSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    menuitem = MenuItemSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['order','menuitem','quantity','unit_price','price']
        validators = UniqueTogetherValidator(
            queryset=OrderItem.objects.all,
            fields=['order', 'menuitem']
        )
    
