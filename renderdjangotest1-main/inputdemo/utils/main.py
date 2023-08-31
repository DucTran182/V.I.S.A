# Import libraries
from ultralytics import YOLO
import cv2
import base64
from PIL import Image
from io import BytesIO
from gtts import gTTS
import playsound
import json
import os
import uuid

# Upload model
model = YOLO('yolov8n.pt')

# Object Detection Function
def detect_object(image, dangerous_classes):
    objects = []
    results = model(image)
    boxes = results[0].boxes
    print(boxes)
    conf_scores = boxes.conf.tolist()
    class_id = boxes.cls.tolist()
    box = boxes.xyxy.tolist()
    has_dangerous_object = False

    for item in range(len(class_id)):
        class_name = results[0].names[class_id[item]]
        bbox = box[item]
        print(bbox)
        bbox = [int(coord) for coord in bbox]
        confidence = conf_scores[item]

        if class_name in dangerous_classes:
            has_dangerous_object = True

        objects.append({
            'Class': class_name,
            'BoundingBox': bbox,
            'Confidence': confidence
        })
    
    json_output = objects

    alert_file_path = os.path.join(r'C:\Users\james\Downloads\Visual Impaired Cam\renderdjangotest1-main\JSON', 'detected_objects.json') #replace with the actual path to save

    # Save the detected object information to a JSON file
    with open(alert_file_path, 'w') as json_file:
        json.dump(json_output, json_file)

    return results, json_output, has_dangerous_object

# Draw bounding box function
def draw_bbox(image, results):
    boxes = results[0].boxes
    class_id = boxes.cls.tolist()
    box = boxes.xyxy
    squeeze_box = box.squeeze().tolist()

    # List to store detected object information
    objects = []

    for item in range(len(class_id)):
        class_name = results[0].names[class_id[item]]
        bbox = box[item]
        bbox = [int(coord) for coord in bbox]

        # Append object info to the list
        objects.append({
            'Class': class_name,
            'BoundingBox': bbox
        })

        #Draw bbox and class name
        cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
        text = class_name
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.8
        thickness = 2
        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        cv2.putText(image, text, (bbox[0], bbox[1] - 5), font, font_scale, (0, 255, 0), thickness, cv2.LINE_AA)
        print(f'Class name: {class_name}, bbox: {bbox}')

    alert_file_path = os.path.join(r'C:\Users\james\Downloads\Visual Impaired Cam\renderdjangotest1-main\JSON', 'detected_objects_drawn.json') #replace with the actual path to save

    # Save the detected object information to a JSON file
    with open(alert_file_path, 'w') as json_file:
        json.dump(objects, json_file)

# Trigger alert function
def trigger_alert(dangerous_object):
    print(f"Dangerous object detected: {dangerous_object}")
    alert_message = f"A {dangerous_object} is infront of you!"

    # Generate a unique filename using UUID
    unique_filename = f"alert_{uuid.uuid4()}.json"

    # Determine the path to save the alert information JSON file
    alert_info = {
        'Object': dangerous_object,
        'AlertMessage': alert_message
    }
    alert_file_path = os.path.join(r'C:\Users\james\Downloads\Visual Impaired Cam\renderdjangotest1-main\JSON', unique_filename) #replace with the actual path to save

    # Save the alert information to the unique JSON file path
    with open(alert_file_path, 'w') as json_file:
        json.dump(alert_info, json_file)
    
# Main function    
def main():
    # Load the image
    api_input_path = r'C:\Users\james\Downloads\Visual Impaired Cam\renderdjangotest1-main\inputdemo\utils\glovik-house-norm-oslo-norway-residential-architecture_dezeen_2364_col_7-852x1191.jpg'
    image = cv2.imread(api_input_path)

    # Define the list of dangerous object classes
    dangerous_classes = ['chair', 'couch', 'dining table']

    try:
        # Detect objects and get results
        detection_results, object_info, has_dangerous_object = detect_object(image, dangerous_classes)

        # Check if there's a dangerous object detected
        if has_dangerous_object:
            # Loop through the detected objects and trigger alert for each dangerous object
            for detected_object in object_info:
                class_name = detected_object['Class']
                if class_name in dangerous_classes:
                    trigger_alert(class_name)

        # Draw bounding boxes and class names on the image
        draw_bbox(image, detection_results)

        # Resize the image to a smaller size
        smaller_size = (800, 600)  # Change the dimensions as needed
        resized_image = cv2.resize(image, smaller_size)

        # Display the annotated image
        cv2.imshow('Annotated Image', resized_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    except Exception as e:
        print("An error occurred:", e)

    # Trigger an alert if dangerous objects are detected
        if has_dangerous_object:
            # Trigger the alert mechanism here (e.g., send notification, sound alarm)
            print("Dangerous object detected! Alert triggered.")

# Call the main function
if __name__ == "__main__":
    main()