# 🎧 Adaptive Volume Controller

This project is a Python-based desktop application that automatically adjusts the system audio volume based on the surrounding environmental sound picked up by the microphone.

When ambient noise increases, the output volume is increased slightly so the audio remains clearly audible. When the environment becomes quieter, the volume is reduced — but **never below a user-defined minimum level**.

The application includes a graphical interface that shows live input and output levels and allows real-time control over volume behavior.

---

## ⚙️ How It Works

1. **Microphone Input**

   * The app continuously listens to ambient sound using the system microphone.
   * Sound intensity is measured using RMS (Root Mean Square), which represents loudness in a linear and stable way.

2. **Adaptive Volume Logic**

   * Ambient loudness is mapped to a system volume level.
   * A compensation factor makes the output volume slightly louder than the surroundings.
   * A fixed minimum volume ensures the sound never becomes too quiet.
   * A maximum volume limit protects hearing.

3. **Speaker Feedback Protection**

   * Small sound changes (such as the speaker’s own output being picked up by the mic) are ignored.
   * Volume changes are applied slowly to prevent runaway feedback.

4. **Smoothing**

   * Recent sound measurements are averaged to avoid sudden volume jumps.
   * Volume transitions happen gradually for a natural listening experience.

---

## 🖥️ Graphical Interface

The GUI provides:

* **Live Ambient Volume (Input dB)** – shows surrounding sound level
* **Live System Volume (Output dB)** – shows current output loudness (estimated)
* **Minimum Volume Slider** – locks a volume floor that the system will not go below
* **Compensation Slider** – controls how much louder the output is compared to the surroundings
* **Start / Stop buttons** – to enable or disable adaptive control

Changes made using the sliders are applied **immediately**.

---

## ▶️ How to Run

### Requirements

```bash
pip install sounddevice numpy pycaw comtypes
```

> Recommended (stable):

```bash
pip install pycaw==20181226 comtypes==1.1.14
```

### Run the application

```bash
python adaptive_volume_complete.py
```

---

## 🔊 Usage Notes

* The application works with **both speakers and headphones**.
* For best results:

  * Keep the microphone unobstructed.
  * Adjust the minimum volume slider to a comfortable baseline.
  * Increase the compensation slider if you are in noisy environments.

---

## 🧠 Key Design Choices

* **RMS-based control** instead of raw dB to ensure correct volume direction
* **dB values are used only for display**, not control logic
* **Thread-safe GUI updates** using a background control loop
* **Immediate slider response** for better user experience

---

## 📌 Summary

This project demonstrates:

* Real-time audio processing
* Adaptive system-level volume control
* GUI integration with background threads
* Safe and user-friendly audio behavior
