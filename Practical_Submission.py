import socket
import cv2
from time import sleep
from threading import Thread
import numpy as np
import time

from numpy.f2py.crackfortran import endifs

print("start")
TELLO_IP = '192.168.10.1'
TELLO_PORT = 8889
TELLO_VIDEO_PORT = 11111
bufferSize = 1024
# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address = (TELLO_IP, TELLO_PORT)


# Send command to Tello
def send_command(command):
    sock.sendto(command.encode('utf-8'), tello_address)
    msg = sock.recvfrom(bufferSize)
    return msg
print("start commands")
msg = send_command("command")
print(msg)

def Task1():
    msg = send_command('takeoff')
    print(msg)
    msg = send_command('up 30')
    print(msg)
    msg = send_command('forward 50')
    print(msg)
    msg = send_command('cw 50')
    print(msg)
    msg = send_command('back 50')
    print(msg)
    msg = send_command('ccw 50')
    print(msg)
    msg = send_command('forward 50')
    print(msg)
    msg = send_command('curve -60 -60 0 0 -120 0 20')
    print(msg)
    msg = send_command('cw 180')
    print(msg)
    # drone return to 0,0,0 and rotates 180 degrees
    msg = send_command('curve -60 60 0 0 120 0 20')
    print(msg)
    # S shape finishes, drone returns to original position
    msg = send_command('cw 180')
    print(msg)
    msg = send_command('curve -60 60 0 0 120 0 20')
    print(msg)
    msg = send_command('cw 180')
    print(msg)
    msg = send_command('curve -60 -60 0 0 -120 0 20')
    print(msg)
    msg = send_command('cw 180')
    print(msg)


def Task2():
        msg = send_command('takeoff')
        print(msg)
        msg = send_command('flip f')
        print(msg)
        msg = send_command('flip l')
        print(msg)
        msg = send_command('flip r')
        print(msg)
        msg = send_command('flip b')
        print(msg)
        msg = send_command('speed?')
        print(msg)
        msg = send_command('speed 20')
        print(msg)
        msg = send_command('speed?')
        print(msg)
        msg = send_command('battery?')
        print(msg)
        msg = send_command('time?')
        print(msg)
        msg = send_command('height?')
        print(msg)
        msg = send_command('land')
        print(msg)

def Task3():
    send_command("streamon")
    time.sleep(2)  # Wait for the stream to initialize

    video_url = f'udp://{TELLO_IP}:{TELLO_VIDEO_PORT}?overrun_nonfatal=1&fifo_size=50000000'
    cap = cv2.VideoCapture(video_url, cv2.CAP_FFMPEG)

    if not cap.isOpened():
        print("❌ Failed to open video stream. Check your network and Tello connection.")
        return

    print("🎥 Video stream started...")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("⚠️ Warning: Failed to read frame.")
                continue

            cv2.imshow('Tello Video Stream', frame)

            # Press 's' to capture an image
            if cv2.waitKey(1) & 0xFF == ord('s'):
                timestamp = int(time.time())
                filename = f"tello_photo_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"📸 Photo saved as {filename}")

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"⚠️ Exception: {e}")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        send_command("streamoff")
        print("🚀 Stream stopped and socket closed.")



def thread():
    Thread(target=Task2).start()
    Thread(target=Task3).start()




Task1()

thread()

