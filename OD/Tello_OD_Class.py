import socket
import cv2
from time import sleep
import numpy as np


print("start")
TELLO_IP = '192.168.10.1'
TELLO_PORT = 8889
TELLO_VIDEO_PORT = 11111
bufferSize = 1024
# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address = (TELLO_IP, TELLO_PORT)


def send_command(command):
    sock.sendto(command.encode(), tello_address)
    msg = sock.recvfrom(bufferSize)
    return msg



def hover_mode():
    delay = 5
    msg = send_command("left 20")
    print(msg)
    sleep(delay)
    msg = send_command("right 20")
    print(msg)
    sleep(delay)
    msg = send_command("left 20")
    print("msg = ", msg)
    sleep(delay)
    msg = send_command("right 20")
    print(msg)
    sleep(delay)

def camera():
    frame_skip = 20
    frame_count = 0
    cap = cv2.VideoCapture('udp://@0.0.0.0:11111')

    net = cv2.dnn.readNet("./yolov3.weights", "./yolov3.cfg")
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in [net.getUnconnectedOutLayers()]]

    with open("./coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]

    try:
        person_detected = False
        while True:
            ret, frame = cap.read()

            if not ret:
                print("Failed to read frame.")
                break

            frame_count += 1
            if frame_count % frame_skip != 0:
                continue

            frame = cv2.resize(frame, (int(frame.shape[1] * 0.4), int(frame.shape[0] * 0.4)))
            height, width = frame.shape[:2]

            # Object detection
            blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            net.setInput(blob)
            outs = net.forward(output_layers)

            class_ids = []
            confidences = []
            boxes = []

            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5:  # Confidence threshold
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

            person_detected = False  # Reset person detection flag

            for i in range(len(boxes)):
                if i in indexes:
                    label = str(classes[class_ids[i]])
                    if label == "person":  # Detect a "person"
                        confidence = confidences[i]
                        color = (0, 255, 0)
                        x, y, w, h = boxes[i]
                        center_x = x + w // 2
                        center_y = y + h // 2

                        # Draw bounding box and label
                        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                        cv2.putText(frame, f"{label} {round(confidence, 2)}", (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                        # Movement commands based on person's position
                        frame_center_x, frame_center_y = width // 2, height // 2
                        horizontal_threshold = 50

                        if center_x < frame_center_x - horizontal_threshold:
                            print("Person is to the left, rotating counter-clockwise")
                            send_command("ccw 20")  # Rotate counter-clockwise
                        elif center_x > frame_center_x + horizontal_threshold:
                            print("Person is to the right, rotating clockwise")
                            send_command("cw 20")  # Rotate clockwise

                        if center_y < frame_center_y - horizontal_threshold:
                            print("Person is above, moving up")
                            send_command("up 20")
                        elif center_y > frame_center_y + horizontal_threshold:
                            print("Person is below, moving down")
                            send_command("down 20")

                        person_detected = True  # Person detected
                        break  # Only track one person

            if not person_detected:
                # If no person is detected, hover in place and rotate to search
                print("Finding someone to track...")
                send_command("cw 30")  # Rotate clockwise to search

            # Display the frame
            cv2.imshow('Tello Video Stream with Object Tracking', frame)

            # Key handling

    except Exception as e:
        print("An error occurred:", e)
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        send_command('streamoff')
        send_command('land')  # Land the drone safely
        send_command('reboot')

def save_image(frame):
    """Save the current frame to a file."""
    import os
    from datetime import datetime

    # Generate a unique filename using the current timestamp
    filename = datetime.now().strftime("capture_%Y%m%d_%H%M%S.jpg")
    filepath = os.path.join(os.getcwd(), filename)

    # Save the image
    cv2.imwrite(filepath, frame)
    print(f"Image saved as {filename}")


if __name__ == "__main__":
    print("start commands")
    msg = send_command("command")
    print(msg)
    msg = send_command("streamon")
    print(msg)
    msg = send_command("takeoff")
    msg = send_command("battery?")

    camera()
    #sleep(2)
    #hover_mode()





