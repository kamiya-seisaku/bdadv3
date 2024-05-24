from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/image/<filename>')
def image(filename):
    return send_from_directory('path_to_your_image_directory', filename)

class ImageUpdateHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.png'):
            filename = os.path.basename(event.src_path)
            socketio.emit('new_image', {'filename': filename})

if __name__ == '__main__':
    observer = Observer()
    observer.schedule(ImageUpdateHandler(), path='path_to_your_image_directory', recursive=False)
    observer.start()

    try:
        socketio.run(app)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
