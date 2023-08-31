from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.parsers import JSONParser 

from inputdemo.models import ImageModel
from inputdemo.serializers import ImageSerializer
from rest_framework.decorators import api_view
import base64
from .utils import *
from PIL import Image
from io import BytesIO
# Create your views here.

@api_view(['GET', 'DELETE'])
def images_list(request):
    # GET list of tutorials, POST a new tutorial, DELETE all tutorials
    if request.method == 'GET':
        images = ImageModel.objects.all()
        
        createTime = request.GET.get('created_at', None)
        if createTime is not None:
            images = images.filter(title__icontains=createTime)
        
        images_serializer = ImageSerializer(images, many=True)
        return JsonResponse(images_serializer.data, safe=False)
        # 'safe=False' for objects serialization
    elif request.method == 'DELETE':
        count = ImageModel.objects.all().delete()
        return JsonResponse({'message': '{} ImageModel were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)
 
@api_view(['GET', 'DELETE'])
def image_detail(request, pk):
    # find tutorial by pk (id)
    try: 
        image = ImageModel.objects.get(pk=pk) 
    except ImageModel.DoesNotExist: 
        return JsonResponse({'message': 'The image does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
    if request.method == 'GET': 
        image_serializer = ImageSerializer(image)
        base64_image = image.image
        userid = image.userid
        command = image.command
        created_time = image.created_at
        # Decode base64 string to bytes
        image_bytes = base64.b64decode(base64_image)
        # Create PIL Image object from bytes
        rgb_image = Image.open(BytesIO(image_bytes))

        # Save the image as .jpg
        rgb_image.save('output.jpg', "JPEG")
        response_data = {
            'image': base64_image,
            'userid': userid,
            'command': command,
            'created_at': created_time,
        }
        return JsonResponse(response_data)
    elif request.method == 'DELETE': 
        image.delete() 
        return JsonResponse({'message': 'image was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
    
@api_view(['POST'])
def image_receive_and_process(request):
    if request.method == 'POST':
        image_data = JSONParser().parse(request)
        image_serializer = ImageSerializer(data=image_data)
        if image_serializer.is_valid():
            base64_image = image_data['image']
            userid = image_data['userid']
            command = image_data['command']
            # Decode base64 string to bytes
            image_bytes = base64.b64decode(base64_image)
            # Create PIL Image object from bytes
            rgb_image = Image.open(BytesIO(image_bytes))
            #rgb_image.save('restored_image.jpg', "JPEG")
            if command == 'detect':
                results, response_data = detect_object(rgb_image)

            elif command == 'obstacle':
                pass

            elif command == 'color':
                pass

            elif command == 'find':
                pass

            return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)
    return JsonResponse({'message': 'wrong request type!'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def test_mobile(request):
    if request.method == 'POST':
        response_data = [{
                    'ImageW': 4000,
                    'ImageH': 6000,
                    'Class': 'person',
                    'BoundingBox': [1128, 1470, 2292, 5140],
                    'Confidence': 0.867745041847229
                },
                {
                    'ImageW': 4000,
                    'ImageH': 6000,
                    'Class': 'person',
                    'BoundingBox': [0, 1317, 1332, 5965],
                    'Confidence': 0.867745041847229
                },
                {
                    'ImageW': 4000,
                    'ImageH': 6000,
                    'Class': 'person',
                    'BoundingBox': [1956, 1160, 3162, 5956],
                    'Confidence': 0.867745041847229
                },
                {
                    'ImageW': 4000,
                    'ImageH': 6000,
                    'Class': 'person',
                    'BoundingBox': [3453, 2255, 3672, 2723],
                    'Confidence': 0.867745041847229
                },
                {
                    'ImageW': 4000,
                    'ImageH': 6000,
                    'Class': 'cell phone',
                    'BoundingBox': [204, 2109, 492, 2692],
                    'Confidence': 0.867745041847229
                }]
    return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)
