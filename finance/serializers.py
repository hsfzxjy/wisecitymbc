from rest_framework import serializers
import time
import models

def get_log_serializer_class(log_model_class):

    class Serializer(serializers.ModelSerializer):

        timestamp = serializers.SerializerMethodField('get_timestamp')
        status    = serializers.Field(source = 'status')

        def get_timestamp(self, obj, *args):
            return time.mktime(obj.created_time.timetuple())

        class Meta:
            model = log_model_class
            exclude = ('finance_object', )

    return Serializer

def get_serializer_class(model_class):

    class Serializer(serializers.ModelSerializer):

        last_log = get_log_serializer_class(model_class.get_log_class())()
        url = serializers.Field(source = 'url')

        class Meta:
            model = model_class

    return Serializer

class DataLogSerializer(serializers.ModelSerializer):

    timestamp = serializers.SerializerMethodField('get_timestamp')

    def get_timestamp(self, obj, *args):
        return time.mktime(obj.created_time.timetuple())

    class Meta:
        model = models.DataLog
        exclude = ('data',)

class ExtraDataSerializer(serializers.ModelSerializer):

    value = serializers.SerializerMethodField('get_value')

    def get_value(self, obj, *args):
        value = obj.value
        try:
            from decimal import Decimal 
            value = round(Decimal(value), 4)
        except:
            pass

        return value 

    class Meta:
        model = models.ExtraData 
        fields = ('display_name', 'value')

class PlayerDataLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PlayerDataLog