# interview_ai.py

import cv2
import numpy as np
import tensorflow as tf
import speech_recognition as sr
from tensorflow.keras import layers
from moviepy import *
import os
import subprocess

FACE_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
FILLER_WORDS = [
    "um", "uh", "like", "so", "you know", "I mean", "actually",
    "basically", "literally", "okay", "right", "well", "er", "hmm",
    "sort of", "kind of", "just", "you see", "indeed", "uh-huh",
    "you know what I mean", "anyway", "exactly", "really", "I guess",
    "supposedly", "apparently", "essentially", "in fact", "sure"
]
interview_model = None

def load_interview_model():
    global interview_model
    model = tf.keras.Sequential([
        layers.Input(shape=(3,)),
        layers.Dense(16, activation='relu'),
        layers.Dense(8, activation='relu'),
        layers.Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='mse')
    interview_model = model
    print("Interview model loaded (placeholder).")

def run_ffmpeg_copy(src_path):
    base, ext = os.path.splitext(src_path)
    copy_path = base + "_copy_to_use.webm"
    cmd = [
        "ffmpeg",
        "-i", src_path,
        "-vcodec", "copy",
        "-acodec", "copy",
        "-y",  
        copy_path
    ]
    print(f"Running ffmpeg copy:\n{' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    return copy_path

def analyze_video(video_path):
    copy_path = run_ffmpeg_copy(video_path)

    cap = cv2.VideoCapture(copy_path)
    if not cap.isOpened():
        print("Could not open video file:", copy_path)
        return None

    total_frames = 0
    face_frames = 0
    confident_frames = 0

    face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        total_frames += 1

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)

        if len(faces) > 0:
            face_frames += 1
            h_img, w_img = frame.shape[:2]
            max_area = 0
            chosen_face = None
            for (x, y, w, h) in faces:
                area = w*h
                if area > max_area:
                    max_area = area
                    chosen_face = (x, y, w, h)

            if chosen_face:
                (x, y, w, h) = chosen_face
                frame_cx, frame_cy = w_img/2, h_img/2
                face_cx, face_cy = x + w/2, y + h/2
                dist_x = abs(face_cx - frame_cx)
                dist_y = abs(face_cy - frame_cy)

                area_threshold = 0.10 * w_img * h_img
                dist_threshold = 0.20 * w_img

                if (max_area >= area_threshold) and (dist_x < dist_threshold) and (dist_y < dist_threshold):
                    confident_frames += 1

    cap.release()

    if total_frames == 0:
        face_ratio = 0
        conf_ratio = 0
    else:
        face_ratio = face_frames / total_frames
        conf_ratio = confident_frames / total_frames

    recognized_text = ""
    filler_count = 0
    try:
        clip = VideoFileClip(copy_path)
        audio = clip.audio
        temp_audio_path = "temp_audio.wav"
        audio.write_audiofile(temp_audio_path, codec='pcm_s16le')

        r = sr.Recognizer()
        with sr.AudioFile(temp_audio_path) as source:
            audio_data = r.record(source)
            try:
                recognized_text = r.recognize_google(audio_data)
            except sr.UnknownValueError:
                recognized_text = ""
            except sr.RequestError as e:
                print("SpeechRec Error:", e)
                recognized_text = ""

        filler_count = sum(1 for w in recognized_text.lower().split() if w in FILLER_WORDS)
    except Exception as e:
        print("Error extracting audio or recognition:", e)

    return {
        "face_presence_ratio": face_ratio,
        "confidence_ratio": conf_ratio,
        "filler_count": filler_count,
        "recognized_text": recognized_text
    }

def get_interview_feedback(video_path):
    if interview_model is None:
        return "Interview model not loaded!"

    stats = analyze_video(video_path)
    if stats is None:
        return "Could not analyze video."

    fc = stats["filler_count"]
    fr = stats["face_presence_ratio"]
    cr = stats["confidence_ratio"]
    text = stats["recognized_text"]

    feat = np.array([[fc, fr, cr]], dtype=np.float32)
    raw_score = interview_model.predict(feat)[0][0]

    if raw_score < 0.3:
        rating = "Bad"
    elif raw_score < 0.7:
        rating = "Okay"
    else:
        rating = "Great"

    feedback = f"""
    === Interview Analysis ===
    Face Presence : {fr:.2f}%
    Confidence    : {cr:.2f}%
    Filler Words   : {fc}
    Score (0..1)        : {raw_score:.2f}
    Overall Rating      : {rating}

    Transcript:
    "{text}"
    """
    return feedback