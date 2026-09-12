<div align="center">
  <h1>🖱️ VirtualMouse</h1>
  <p><b>Revolutionizing Human-Computer Interaction</b></p>
  <p>Control your entire PC hands-free using Advanced AI Facial Tracking & Zero-Delay Voice Dictation.</p>

  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
  [![Developer](https://img.shields.io/badge/Developed_by-Sidharth_Kumar-ec4899.svg)](#)
</div>

---

## 🌟 Overview
**VirtualMouse** is a 100% locally-run, AI-powered system that eliminates the need for physical hardware like keyboards and mice. By utilizing Google's MediaPipe for precise 468-point facial landmark tracking and a custom Voice Activity Detector (VAD) for real-time dictation, it offers an unmatched hands-free computing experience.

Designed, developed, and optimized specifically for **BHARAT**.

---

## ✨ Next-Gen Capabilities

### 👁️ Precision Face Tracking (Cursor Control)
- **Nose Tracking**: Highly sensitive nose movement mapped perfectly to screen coordinates.
- **Wink Gestures**: Wink left eye to left-click (hold to drag/select). Wink right eye for right-click.
- **Mouth Scrolling**: Simply open your mouth and move your head up/down to scroll seamlessly.
- **Safety Lock**: Close both eyes for `1.2 seconds` to turn the entire tracking system ON/OFF to prevent accidental clicks.

### 🎙️ Zero-Delay Voice Keyboard
- **Indian Accent Support (`en-IN`)**: Optimized for flawless dictation with lightning-fast Google APIs.
- **Custom VAD**: Smart silence detection prevents your sentences from being cut off prematurely.
- **Advanced Commands**: Speak natural commands like *"Scroll Down"*, *"Delete Word"*, *"Enter"*, *"Select All"*, and *"Keyboard Off"*.
- **Audio Feedback**: Built-in Windows SAPI voice confirms every command you execute (e.g., "Left Click", "Scrolling Down").

---

## 📦 How to Run

### Method 1: Pre-built App (No Python Required)
1. Navigate to the `VirtualMouse` folder.
2. Double-click the **`build_app.bat`** script. This will automatically package the AI models and Python script into a standalone Windows `.exe` application.
3. Open the newly created `dist/` folder and run **`VirtualMouseApp.exe`**.

### Method 2: Python Environment
1. Ensure Python 3.8+ is installed.
2. Install the necessary dependencies:
   ```bash
   cd app
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```
*(Note: An internet connection is required on the first launch to download the MediaPipe `face_landmarker.task` model).*

---

## 🌐 Premium Website
This project includes a **Futuristic Landing Page** designed to showcase the app.
- Open [`https://virtual-mouse-two.vercel.app/`](https://virtual-mouse-two.vercel.app/) in your browser.
- Contains 8K Cinematic Animated Backgrounds, a detailed Commands Guide, and an App Download portal.

---

## 👨‍💻 Developer
**Developed by Sidharth Kumar**  
Contact: [siddharthkr170@gmail.com](mailto:siddharthkr170@gmail.com)

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
