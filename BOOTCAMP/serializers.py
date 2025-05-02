from rest_framework import serializers,permissions,validators
from .models import Bootcamp, BootcampCategory,BootcampRegistration

class BootcampCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BootcampCategory
        fields = ['id', 'name', 'description']

class BootcampSerializer(serializers.ModelSerializer):
    category = BootcampCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=BootcampCategory.objects.all(),
        source='category',
        write_only=True,
        required=True
    )

    class Meta:
        model = Bootcamp
        fields = [
            'id', 'title', 'description', 'category', 'category_id',
            'start_date', 'end_date', 'schedule_days', 'schedule_time',
            'capacity', 'status', 'is_advance', 'price'
        ]
        read_only_fields = ['status']  # وضعیت فقط از طریق اکشن‌های خاص تغییر کند

    def validate_capacity(self, value):
        if value < 1:
            raise serializers.ValidationError("ظرفیت باید حداقل ۱ باشد.")
        return value
    

    class BootcampRegistrationSerializer(serializers.ModelSerializer):

    bootcamp_title = serializers.CharField(source='bootcamp.title', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = BootcampRegistration
        fields = [
            'id', 'user', 'user_phone', 'bootcamp', 'bootcamp_title',
            'status', 'created_at', 'updated_at', 'payment_receipt'
        ]
        read_only_fields = ['user', 'status']  # کاربر فقط می‌تواند بوتکمپ را انتخاب کند

    def validate(self, data):
        if BootcampRegistration.objects.filter(user=self.context['request'].user, bootcamp=data['bootcamp']).exists():
            raise serializers.ValidationError("شما قبلاً در این بوتکمپ ثبت‌نام کرده‌اید.")
        return data