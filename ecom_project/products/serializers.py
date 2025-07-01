from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Product, Category, ProductImage, ProductVariant

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main']

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'size', 'stock']

class ProductListSerializer(serializers.ModelSerializer):
    main_image_url = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'discount_price', 'main_image_url','category'
        ]

    def get_main_image_url(self, obj):
        if obj.main_image:
            return obj.main_image.url
        main_img_obj = obj.images.filter(is_main=True).first()
        if main_img_obj and main_img_obj.image:
            return main_img_obj.image.url
        return None

class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    main_image_url = serializers.SerializerMethodField()
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'  # or list all fields explicitly + 'images' + 'main_image_url' + 'variants'

    def get_main_image_url(self, obj):
        if obj.main_image:
            return obj.main_image.url
        main_img_obj = obj.images.filter(is_main=True).first()
        if main_img_obj and main_img_obj.image:
            return main_img_obj.image.url
        return None

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image']  # Include image
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }


