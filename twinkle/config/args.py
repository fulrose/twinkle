import argparse
from twinkle.config import threshold


def arg():
    # ap = argparse.ArgumentParser()
    # ap.add_argument("-p", "--shape-predictor",default="shape_predictor_68_face_landmarks.dat",
    # 	help="path to facial landmark predictor")
    # ap.add_argument("-v", "--video", type=str, default="camera",
    # 	help="path to input video file")
    # ap.add_argument("-t", "--threshold", type = float, default=0.20,
    # 	help="threshold to determine closed eyes")
    # ap.add_argument("-f", "--frames", type = int, default=2,
    # 	help="the number of consecutive frames the eye must be below the threshold")
    ap = {}
    ap['shape_predictor'] = "shape_predictor_68_face_landmarks.dat"
    ap['video'] = "camera"
    ap['threshold'] = threshold.load_config()
    ap['frames'] = 2

    return ap
