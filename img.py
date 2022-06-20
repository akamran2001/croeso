import os
import subprocess


def unzip():
    for fname in os.listdir('media/images'):
        if fname.endswith('.jpg'):
            return None
    subprocess.run(["unzip", "media/images/images.zip", "-d", "media/images"])
