from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from post.serializers import *
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from photo.models import Photo

# Create your views here.
class CreatePost(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data, context={'request': request}) # here we are passing the data to check
        if serializer.is_valid(raise_exception=True):
            post = serializer.save(author=request.user) # here we are saving the checked data to Django's model
            
            file = request.FILES.get('image')  # Use 'get' with a default value to handle missing 'image' key
            if file:
                extension = str(file).split('.')[-1]
                if extension.lower() == 'gif':
                    return Response({'status': 'You cannot upload a GIF as a post photo.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    post.photo = file

            post.save()

            for uploaded_file in request.FILES.getlist('photos'):
                photo = Photo.objects.create(file=uploaded_file, author=request.user)
                post.photos.add(photo)
            
            id_to_reply = serializer.data.get('id_to_reply')
            if id_to_reply:
                replied_post = Post.objects.get(id=id_to_reply)
                post.reply = replied_post
                post.is_reply = True

            post.save()

            response = Response({'status':'successfully posted'},
                                status=status.HTTP_200_OK)
            return response
        else:
            return Response({'status':'register failed',
                         'error':serializer.errors},
                        status=status.HTTP_200_OK)