from django.contrib.auth.models import User
from rest_framework import serializers
from django.conf import settings
from .models import Item, Likes, MyUser, Order, OrderItem, Address





class ItemSerializer(serializers.ModelSerializer):
    # likes_rate = serializers.SerializerMethodField(source='get_like_rate')
    class Meta:
        model = Item
        fields = ('title','price','discount_price','slug','description','image','vendor','comment','likes_rate')
        depth = 1

    def get_like_rate(self, inst):
        return inst.likes_rate


    def to_representation(self, instance):
        data = super().to_representation(instance)
        for key, value in data.items():
            try:
                if not value:
                    data[key] = "null"
            except KeyError:
                pass
        return data

    

class OderItemSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = OrderItem
        fields = "__all__"
        depth = 1


class OderItemSummarySerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = OrderItem
        fields = "__all__"
        depth = 1


class OrderSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField(source='get_total')
    items = OderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('ref_code', 'items', 'start_date', 'ordered_date', 'ordered', 'shipping_address', 'billing_address', 'payment', 'coupon', 'being_delivered', 'received', 'refund_requested', 'refund_granted', 'total')
        # fields = "__all__"
        depth = 1

    def get_total(self, inst):
        # return print(sum([item.items for item in items.all()]))
        # return print(sum([item.items for item in inst.items.all()]))
        # return print(inst.items.get_queryset())
        # return print(Item.objects.all())
        return inst.total

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        # fields = ('street_address', 'country', 'zip', 'address_type', 'default')
        fields = "__all__"

class LikesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Likes
        fields = ('items',)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields =  "__all__" 
        # ('id', 'email', 'first_name', 'last_name')
        # write_only_fields = ('password',)
        # read_only_fields = ('id',)

    # def create(self, validated_data):
    #     user = User.objects.create(
    #         username=validated_data['username'],
    #         email=validated_data['email'],
    #         first_name=validated_data['first_name'],
    #         last_name=validated_data['last_name']
    #     )

    #     user.set_password(validated_data['password'])
    #     user.save()

        # return user

# class CreateUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = settings.AUTH_USER_MODE
#         fields = ['email', 'username', 'password']
#         extra_kwargs = {'password': {'write_only': True}}
#
#     def create(self, validated_data):
#         user = User(
#             email=validated_data['email'],
#             username=validated_data['username']
#         )
#         user.set_password(validated_data['password'])
#         user.save()
#         return user
