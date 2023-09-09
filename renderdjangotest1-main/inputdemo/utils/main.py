from ultralytics import YOLO
import cv2
import base64
from PIL import Image
from io import BytesIO

import json

model = YOLO('yolov8n.pt')
def LCR(bbox,x_img, y_img):
    x1 = bbox[0]/x_img
    x2 = bbox[2]/x_img
    if x1 < 0.2 and x2 < 0.2 :
        location = "On the left"
    elif x1 > 0.8 and x2 > 0.8:
        location = "On the right"
    elif x1 < 0.2 and (x2 <= 0.8 and x2 >= 0.2):
        if (x1 + x2) < 0.4:
            location = "On the left"
        else:
            location = "At the center" 
    elif x2 > 0.8 and (x1 <= 0.8 and x1 >= 0.2):
        if (x1 + x2) > 1.6:
            location = "On the right"
        else:
            location = "At the center" 
    else:
        location = "At the center"
    return location

def ACB(bbox, x_img, y_img, location):
    y1 = bbox[1]/y_img
    y2 = bbox[3]/y_img
    if location == "At the center":
        if y1 < 0.33333 and y2 < 0.33333 :
            location = "On the top"
        elif y1 > 0.66667 and y2 > 0.66667:
            location = "On the bottom"
        elif y1 < 0.33333 and (y2 <= 0.66667 and y2 >= 0.33333):
            if (y1 + y2) < 0.66667:
                location = "On the top"
            else:
                location = "At the center" 
        elif y2 > 0.66667 and (y1 <= 0.66667 and y1 >= 0.33333):
            if (y1 + y2) > 1.33333:
                location = "On the bottom"
            else:
                location = "At the center" 
        else:
            location = "At the center"
    else:
        pass
    
    return location

def depth_value(bbox, IW, IH, map_depth_pixels, depthWidth, depthHeight):
    x_left_pixel_location = round(bbox[0]/IW * depthWidth)
    y_left_pixel_location = round(bbox[1]/IH * depthHeight)
    x_right_pixel_location = round(bbox[2]/IW * depthWidth)
    y_right_pixel_location = round(bbox[3]/IH * depthHeight)
    value = 0
    count = 0
    pxvalue = 0
    for matrix in map_depth_pixels[y_left_pixel_location:(y_right_pixel_location+1)]:
        for pixel in matrix[x_left_pixel_location:(x_right_pixel_location+1)]:
            if pixel >= 0:
                count += 1
                pxvalue += pixel
    value = pxvalue/count

    return value

def imgae_to_text(data) : 
    count = {}
    for index, infor in enumerate(data):
        key = infor['Location']  + ':' + infor['Class']
        if key in count:
            count[key] += 1
        else:
            count[key] = 1
    text = ""

    for index1, infor1 in enumerate(count):
        name_class =""
        value = count[infor1]
        parts = infor1.split(":")
        if value > 1 :
            vbare = "are"
            if parts[1] =='person':
                name_class = 'people'
            else:
                name_class = parts[1] + 's'
        else:
            name_class = parts[1] 
            vbare = "is"
        text +=  parts[0] + ", there" + " " + vbare + " " + f"{value}" + " " + name_class +'.' +" "
    return text  

def detect_object(image, userId, device, createdAt, dangerous_classes=None, object_need_to_find=None):
    objects = []
    results = model(image)
    boxes = results[0].boxes
    #print(boxes)
    conf_scores = boxes.conf.tolist()
    class_id = boxes.cls.tolist()
    box = boxes.xyxy.tolist()
    imageH, imageW = boxes.orig_shape
    has_dangerous_object = False
    found = False

    objects.append({
        'imageH': imageH,
        'imageW': imageW,
        'device': device,
        'userId': userId,
        'createdAt': createdAt
    })

    for item in range(len(class_id)):
        class_name = results[0].names[class_id[item]]
        bbox = box[item]
        #print(bbox)
        bbox = [int(coord) for coord in bbox]
        confidence = conf_scores[item]

        if dangerous_classes:
            if class_name in dangerous_classes:
                has_dangerous_object = True

        if object_need_to_find:
            if class_name == object_need_to_find:
                found = True
        
        location = LCR(bbox, imageW, imageH)
        location = ACB(bbox, imageW, imageH, location)

        objects.append({
            'Class': class_name,
            'BoundingBox': bbox,
            'Location': location,
            'Confidence': confidence
        })
    text = imgae_to_text(objects[1:])
    obj_info = objects
    return text, obj_info, has_dangerous_object, found


def draw_bbox(image, results):
    boxes = results[0].boxes
    class_id = boxes.cls.tolist()
    box = boxes.xyxy
    for item in range(len(class_id)):
        class_name = results[0].names[class_id[item]]
        bbox = box[item]
        bbox = [int(coord) for coord in bbox]
        
        #Draw bbox and class name
        cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
        text = class_name
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.8
        thickness = 2
        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        cv2.putText(image, text, (bbox[0], bbox[1] - 5), font, font_scale, (0, 255, 0), thickness, cv2.LINE_AA)
        print(f'Class name: {class_name}, bbox: {bbox}')


def detect_and_alert(image_data, dangerous_classes):

    min_value = 10
    data = []
    base64_image = image_data['image']
    imageW = image_data['imageWidth']
    imageH = image_data['imageHeight']
    depth = image_data['depth']
    depthW = image_data['depthWidth']
    depthH = image_data['depthHeight']
    device = image_data['device']
    created_at = image_data['createdAt']
    #print(base64_image)
    userid = image_data['userId']
    image_bytes = base64.b64decode(base64_image)

    # Create PIL Image object from bytes
    rgb_image = Image.open(BytesIO(image_bytes))
    user_info = {
        "imageH": imageH,
        "imageW": imageW,
        "device": device,
        "userId": userid,
        "createdAt": created_at
    }
    try:
        # Detect objects and get results
        _, object_info, has_dangerous_object, _ = detect_object(rgb_image, userid, device, created_at, dangerous_classes=dangerous_classes)

        # Check if there's a dangerous object detected
        if has_dangerous_object:
            # Loop through the detected objects and trigger alert for each dangerous object
            for detected_object in object_info[1:]:
                if detected_object['Class']:
                    class_name = detected_object['Class']
                    if class_name in dangerous_classes:
                        value_depth = (depth_value(detected_object["BoundingBox"],
                                                   imageW,
                                                   imageH,
                                                   depth,
                                                   depthW,
                                                   depthH)/0.7)
                        location = LCR(detected_object["BoundingBox"],
                                                   imageW,
                                                   imageH)
                        location = ACB(detected_object["BoundingBox"],
                                                   imageW,
                                                   imageH, 
                                                   location)
                        
                        if value_depth < 2:
                            min_value = min(min_value,value_depth)
                            data.append({
                                        'Class': class_name,
                                        'Location': location,
                                    })
                        
            text = imgae_to_text(data)
            if text != '':
                summary = 'Warning! ' + text + "Away from you approximate " + f'{round(min_value)}' + " arms "
            else :
                summary = "None"

            alert_response = {
                'user_info': user_info,
                'summary': summary
            }
            return alert_response

    except Exception as e:
        print("An error occurred:", e)



def check_object_need_to_find(image, userId, device, createdAt, depth, depthW , depthH, object_need_to_find):
    # try:
    # Detect objects and get results
    summary = ''
    _, object_info, _, found = detect_object(image, userId, device, createdAt, object_need_to_find=object_need_to_find)
    imageH = object_info[0]["imageH"]
    imageW = object_info[0]["imageW"]
    # Check if there's a founded object detected
    if found:
        for detected_object in object_info[1:]:
            if detected_object['Class']:
                if detected_object['Class'] == object_need_to_find:
                    value_depth = round(depth_value(detected_object["BoundingBox"],
                                                    imageW,
                                                    imageH,
                                                    depth,
                                                    depthW,
                                                    depthH)/0.7)
                    location = LCR(detected_object["BoundingBox"],imageW, imageH)
                    location = ACB(detected_object["BoundingBox"], imageW, imageH, location)
                    if value_depth <= 1:
                        unit = "arm"
                    else :
                        unit = "arms"
                    
                    summary = summary + f"The {object_need_to_find} is away from you approximate {value_depth} {unit} {location}. "
    else:
        summary = f"The {object_need_to_find} is not in front of you"
 
    find_response = {'user_info': object_info[0], 'summary': summary}
    return find_response
