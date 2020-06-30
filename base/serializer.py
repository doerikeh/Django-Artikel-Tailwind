from django.shortcuts import get_object_or_404
from .models import MessageModel, User
from rest_framework.serializers import ModelSerializer, CharField


class MessageModelSerializer(ModelSerializer):
    user = CharField(source='user.username_user', read_only=True)
    recipient = CharField(source='recipient.username_user')

    def create(self, validated_data):
        user = self.context['request'].user
        recipient = get_object_or_404(
            User, username_user=validated_data['recipient']['username_user'])
        msg = MessageModel(recipient=recipient,
                           body=validated_data['body'],
                           user=user)
        msg.save()
        return msg

    class Meta:
        model = MessageModel
        fields = ('id', 'user', 'recipient', 'timestamp', 'body')


class UserModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username_user', "image_profile")
