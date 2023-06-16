from rest_framework import serializers
from post.models import Post
from photo.models import Photo

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    id_to_reply = serializers.IntegerField(write_only=True)
    photos = PhotoSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ['header', 'content', 'image', 'photos', 'is_edited', 'reply', 'id_to_reply']

    def validate(self, data):
        request = self.context['request']
        upload_photos = request.FILES.getlist('photos')
        if len(upload_photos) > 4:
            raise serializers.ValidationError('Maximum amount of photos - 4')
        return data

    def create(self, validated_data):
        id_to_reply = validated_data.pop('id_to_reply')
        photos_data = validated_data.pop('photos', [])  # Get the photos data (if any)

        post = Post.objects.create(**validated_data)

        # Set the reply if id_to_reply is provided
        if id_to_reply:
            post.reply = Post.objects.get(id=id_to_reply)
            post.is_reply = True

        # Create and associate the photos (if any)
        for photo_data in photos_data:
            photo = Photo.objects.create(**photo_data, author=post.author)
            post.photos.add(photo)

        post.save()
        return post