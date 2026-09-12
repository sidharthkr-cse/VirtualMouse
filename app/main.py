import sys
import codecs
import cv2
import mediapipe as mp
import pyautogui
import time
import os
import warnings
import urllib.request
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import threading
import queue
import pyttsx3
import pythoncom
import win32com.client

# ------------------ TTS ENGINE ------------------
tts_queue = queue.Queue()

def tts_thread():
    pythoncom.CoInitialize()
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    speaker.Volume = 100 # Maximum volume
    while True:
        text = tts_queue.get()
        speaker.Speak(text)
        tts_queue.task_done()

threading.Thread(target=tts_thread, daemon=True).start()

def speak(text):
    tts_queue.put(text)

# ------------------ SETUP ------------------
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings("ignore", category=UserWarning)

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

print("🚀 VIRTUAL MOUSE STARTED")
print("👁️ Close BOTH eyes for 1.2s to turn ON/OFF")
print("✅ Loop-protection active: Must open eyes to reset toggle.\n")

# ------------------ INIT MODEL ------------------
MODEL_PATH = "face_landmarker.task"
if not os.path.exists(MODEL_PATH):
    print("Downloading face_landmarker model...")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
        MODEL_PATH
    )

# ------------------ STATE ------------------
cursor_active = False
is_dragging = False
scroll_mode = False
keyboard_active = False
audio_queue = queue.Queue()
recognizer = sr.Recognizer()

# Click/Drag Timing
last_left_blink_time = 0
left_eye_closed_start = 0
double_click_threshold = 0.4
long_press_threshold = 0.5

# Toggle State
both_eyes_closed_start = 0
toggle_locked = False
eyes_open_since = 0

# Smoothing
prev_x, prev_y = 0, 0
smooth_factor = 0.15 # Decreased to 0.15 to absorb camera jitter and make movement buttery smooth

# Scroll State
scroll_anchor_y = None
last_scroll_dir = ""

# Thresholds
BLINK_THRESH = 0.012
MOUTH_THRESH = 0.03

# Setup MediaPipe
options = mp.tasks.vision.FaceLandmarkerOptions(
    base_options=mp.tasks.BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=mp.tasks.vision.RunningMode.VIDEO)
face_mesh = mp.tasks.vision.FaceLandmarker.create_from_options(options)

# ------------------ VOICE KEYBOARD ------------------
def process_audio():
    global keyboard_active
    while True:
        audio_data = audio_queue.get()
        try:
            text = recognizer.recognize_google(audio_data, language="en-IN")
            if text:
                text = text.lower()
                print(f"🗣️ Heard: {text}")
                if "keyboard on" in text or "start keyboard" in text:
                    keyboard_active = True
                    print("⌨️ KEYBOARD ACTIVATED")
                    speak("Keyboard Activated")
                elif "keyboard of" in text or "stop keyboard" in text:
                    keyboard_active = False
                    print("⌨️ KEYBOARD DEACTIVATED")
                    speak("Keyboard Deactivated")
                elif keyboard_active:
                    # Advanced Voice Commands
                    if "scroll down" in text or "page down" in text:
                        print("📜 VOICE SCROLL DOWN")
                        pyautogui.press('pagedown')
                        speak("Scrolling down")
                    elif "scroll up" in text or "page up" in text:
                        print("📜 VOICE SCROLL UP")
                        pyautogui.press('pageup')
                        speak("Scrolling up")
                    elif "delete word" in text or "delete" in text:
                        print("🔙 VOICE DELETE")
                        pyautogui.hotkey('ctrl', 'backspace')
                        speak("Deleted")
                    elif "new line" in text or "enter" in text:
                        print("⏎ VOICE ENTER")
                        pyautogui.press('enter')
                        speak("Enter")
                    elif "select all" in text:
                        print("🟦 VOICE SELECT ALL")
                        pyautogui.hotkey('ctrl', 'a')
                        speak("Select all")
                    elif "copy" in text:
                        print("📋 VOICE COPY")
                        pyautogui.hotkey('ctrl', 'c')
                        speak("Copied")
                    elif "paste" in text:
                        print("📋 VOICE PASTE")
                        pyautogui.hotkey('ctrl', 'v')
                        speak("Pasted")
                    elif "backspace" in text:
                        print("🔙 VOICE BACKSPACE")
                        pyautogui.press('backspace')
                    elif "space" == text.strip():
                        print("␣ VOICE SPACE")
                        pyautogui.press('space')
                    else:
                        # Basic symbol replacements & typing
                        text = text.replace(" comma", ",").replace(" full stop", ".").replace(" question mark", "?")
                        # Format as sentence
                        text = text.capitalize()
                        pyautogui.write(text + " ")
        except sr.UnknownValueError:
            pass # Silence or unrecognized
        except Exception as e:
            pass
        audio_queue.task_done()

def voice_recognition_thread():
    threading.Thread(target=process_audio, daemon=True).start()
    fs = 16000
    chunk_duration = 0.5 # 0.5 second chunks
    chunk_samples = int(fs * chunk_duration)
    
    audio_buffer = []
    silence_chunks = 0
    is_speaking = False
    
    print("🎙️ Smart Voice Keyboard Listening (Zero-Delay VAD)...")
    
    try:
        with sd.InputStream(samplerate=fs, channels=1, dtype=np.int16) as stream:
            while True:
                audio_chunk, overflowed = stream.read(chunk_samples)
                volume = np.max(np.abs(audio_chunk))
                
                if volume > 80: # Highly sensitive threshold
                    is_speaking = True
                    silence_chunks = 0
                    audio_buffer.append(audio_chunk)
                elif is_speaking:
                    silence_chunks += 1
                    audio_buffer.append(audio_chunk)
                    
                    if silence_chunks >= 3: # 1.5 seconds of silence
                        complete_audio = np.concatenate(audio_buffer)
                        audio_data = sr.AudioData(complete_audio.tobytes(), fs, 2)
                        audio_queue.put(audio_data)
                        
                        audio_buffer = []
                        is_speaking = False
                        silence_chunks = 0
    except Exception as e:
        print(f"Mic Error: {e}")

threading.Thread(target=voice_recognition_thread, daemon=True).start()

cam = cv2.VideoCapture(0)
screen_w, screen_h = pyautogui.size()

# ------------------ MAIN LOOP ------------------
def run_app():
    global cursor_active, is_dragging, scroll_mode
    global last_left_blink_time, left_eye_closed_start, both_eyes_closed_start
    global toggle_locked, eyes_open_since, prev_x, prev_y
    global scroll_anchor_y, last_scroll_dir

    while True:
        success, frame = cam.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        frame_h, frame_w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        output = face_mesh.detect_for_video(mp_image, int(time.time() * 1000))

        if output.face_landmarks:
            landmarks = output.face_landmarks[0]

            # 1. NOSE TRACKING (CURSOR) - SUPER FAST MODE
            nose = landmarks[1]
            
            # Scale coordinates to make very small nose movements cover the whole screen
            SENSITIVITY = 5.0 # Drastically increased for maximum screen coverage
            scaled_x = 0.5 + (nose.x - 0.5) * SENSITIVITY
            scaled_y = 0.5 + (nose.y - 0.5) * SENSITIVITY
            
            screen_x = max(0, min(screen_w, scaled_x * screen_w))
            screen_y = max(0, min(screen_h, scaled_y * screen_h))
            
            curr_x = prev_x + (screen_x - prev_x) * smooth_factor
            curr_y = prev_y + (screen_y - prev_y) * smooth_factor

            # 2. MOUTH (SCROLL)
            mouth_top, mouth_bottom = landmarks[13], landmarks[14]
            mouth_dist = abs(mouth_top.y - mouth_bottom.y)

            scroll_mode = False
            if cursor_active:
                if mouth_dist > MOUTH_THRESH and not keyboard_active:
                    scroll_mode = True
                    if scroll_anchor_y is None:
                        scroll_anchor_y = curr_y
                    
                    diff_y = scroll_anchor_y - curr_y
                    if abs(diff_y) > 10: # Smaller Deadzone
                        scroll_speed = int(diff_y * 3) # Much slower, comfortable speed multiplier
                        pyautogui.scroll(scroll_speed)
                        
                        if scroll_speed > 0 and last_scroll_dir != "UP":
                            print("📜 SCROLL UP")
                            speak("Scroll up")
                            last_scroll_dir = "UP"
                        elif scroll_speed < 0 and last_scroll_dir != "DOWN":
                            print("📜 SCROLL DOWN")
                            speak("Scroll down")
                            last_scroll_dir = "DOWN"
                else:
                    scroll_anchor_y = None
                    last_scroll_dir = ""
                    pyautogui.moveTo(curr_x, curr_y)
            else:
                scroll_anchor_y = None
                last_scroll_dir = ""

            prev_x, prev_y = curr_x, curr_y

            # 3. EYE DISTANCES
            left_dist = abs(landmarks[159].y - landmarks[145].y)
            right_dist = abs(landmarks[386].y - landmarks[374].y)
            both_closed = left_dist < BLINK_THRESH and right_dist < BLINK_THRESH

            # 4. TOGGLE LOGIC
            current_time = time.time()
            if both_closed:
                if not toggle_locked:
                    if both_eyes_closed_start == 0:
                        both_eyes_closed_start = current_time
                    
                    elapsed = current_time - both_eyes_closed_start
                    if elapsed >= 1.2:
                        cursor_active = not cursor_active 
                        state_str = 'ON' if cursor_active else 'OFF'
                        print(f"🔄 SYSTEM {state_str}")
                        speak(f"System {state_str}")
                        toggle_locked = True
                        both_eyes_closed_start = 0
                    
                    remaining = max(0, 1.2 - elapsed)
                    cv2.putText(frame, f"TOGGLE: {remaining:.1f}s", (frame_w//2-100, frame_h//2), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3)
                else:
                    cv2.putText(frame, "EYES OPEN TO RESET", (frame_w//2-140, frame_h//2 + 40), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                eyes_open_since = 0
            else:
                if eyes_open_since == 0:
                    eyes_open_since = current_time
                if current_time - eyes_open_since > 0.5:
                    toggle_locked = False
                    both_eyes_closed_start = 0

            # 5. MOUSE ACTIONS (IF ACTIVE)
            if cursor_active:
                # LEFT CLICK / DRAG
                if left_dist < BLINK_THRESH and not both_closed:
                    if left_eye_closed_start == 0:
                        left_eye_closed_start = current_time

                    if not is_dragging and (current_time - left_eye_closed_start) > long_press_threshold:
                        pyautogui.mouseDown()
                        is_dragging = True
                        print("📂 DRAG START")
                        speak("Drag start")
                elif left_eye_closed_start != 0:
                    if is_dragging:
                        pyautogui.mouseUp()
                        is_dragging = False
                        print("📂 DRAG END")
                        speak("Drag end")
                    else:
                        if (current_time - last_left_blink_time) < double_click_threshold:
                            pyautogui.doubleClick()
                            print("🖱️ DOUBLE CLICK")
                            speak("Double click")
                        else:
                            pyautogui.click()
                            print("🖱️ LEFT CLICK")
                            speak("Left click")
                        last_left_blink_time = current_time
                    left_eye_closed_start = 0

                # RIGHT CLICK
                if right_dist < BLINK_THRESH and not both_closed:
                    pyautogui.rightClick()
                    print("🖱️ RIGHT CLICK")
                    speak("Right click")
                    time.sleep(0.4)

            # 6. HUD DISPLAY
            status = "OFF"
            color = (0, 0, 255)
            if cursor_active:
                status = "ACTIVE"
                color = (0, 255, 0)
                if is_dragging: status = "DRAGGING"; color = (255, 0, 0)
                if scroll_mode: status = "SCROLLING"; color = (255, 255, 0)

            cv2.putText(frame, f"MODE: {status}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            if cursor_active:
                cv2.circle(frame, (int(nose.x * frame_w), int(nose.y * frame_h)), 5, color, -1)

        cv2.imshow("VIRTUAL MOUSE", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_app()
