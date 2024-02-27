import cv2
from flask import Flask, request, jsonify
import os
from collections import deque
import argparse
import json
import threading
from datetime import datetime


app = Flask(__name__)


class RecorderService(object):
    """
    Processes a video stream and keeps the last num_frames in a deque. It assumes that the interval between POST
    requests is smaller than the duration of storing the images. Otherwise an additional service would be
    beneficial to handle storing of the frames, e.g., using asyncio.

    Attributes
    ----------
    frame_buffer : deque
        queue for storing the recent frames
    video_capture : cv2.VideoCapture
        video capture

    Methods
    -------
    process_frames:
        Processes the frames until video ends.
    """
    def __init__(self, frame_buffer, video):
        """
        Parameters
        ----------
        frame_buffer : deque
            reference to global queue for storing the recent frames
        video : str
            video file path
        """
        self.frame_buffer = frame_buffer
        # Initialize video capture
        self.video_capture = cv2.VideoCapture(video)

    def process_frames(self):
        while True:
            ret, frame = self.video_capture.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            with frame_buffer_lock: # Ensure that only frames are added when no storing is in progress
                self.frame_buffer.append(frame)


@app.route('/save_frames', methods=['POST'])
def save_frames():
    """
    HTTP endpoint. When HTTP POST is received store the metadata and the last num_frames as PNGs.
    
    Returns
    -------
    json
    """

    json_data = request.json  # JSON data included in the request

    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs(os.path.join(root_dir, timestamp))

    with frame_buffer_lock: # Ensure that no new frames are added during storing the images
        buffer_length = len(frame_buffer)
        for i in range(buffer_length):
            if frame_buffer:
                frame = frame_buffer.pop()
                # Save the frame to storage as PNG
                cv2.imwrite(os.path.join(root_dir, timestamp, f'saved_frame_{i}.png'), frame)
            else:
                break

    # Save JSON data to a file
    with open(os.path.join(root_dir, timestamp, 'metadata.json'), 'w') as json_file:
        json.dump(json_data, json_file)

    return jsonify({'saved_frames': buffer_length})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Save frames from a video stream')
    parser.add_argument('--root', type=str, default='/storage', help='Directory of storage')
    parser.add_argument('--video', type=str, default='/storage/video.mkv', help='Path to the video file')
    parser.add_argument('--num_frames', type=int, default=10, help='Number of frames to save in each request')
    args = parser.parse_args()

    global frame_buffer, frame_buffer_lock
    frame_buffer = deque(maxlen=args.num_frames)
    frame_buffer_lock = threading.Lock()

    global root_dir
    root_dir = args.root

    recorder_service = RecorderService(frame_buffer, args.video)

    # Start a separate thread to process frames
    frame_thread = threading.Thread(target=recorder_service.process_frames)
    frame_thread.start()

    # Run Flask app
    app.run(host='0.0.0.0', port=8000, debug=True)
 