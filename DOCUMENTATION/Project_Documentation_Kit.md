
# Final Year Project Documentation Kit
**Project Title**: Agriculture Real-time Monitoring & Intelligent Chatbot

---

## 1. Project Report Structure
A standard chapter breakdown for your final report.

### Chapter 1: Introduction
*   **1.1 Problem Statement**:
    *   Faming faces challenges from undetected diseases and pests.
    *   Manual inspection is time-consuming and prone to error.
    *   Farmers often lack access to real-time expert agricultural advice.
*   **1.2 Objectives**:
    *   To develop a real-time computer vision system for automated disease detection.
    *   To integrate environmental context (Weather) into decision making.
    *   To provide actionable, rule-based remedies via a unified API.
*   **1.3 Scope**:
    *   **Crops**: Potato, Tomato, Corn.
    *   **Input**: Real-time camera feed and Image Upload.
    *   **Platform**: Web-based Dashboard (React + Flask).

### Chapter 2: Literature Review
*   **Existing Solutions**: Discuss limitations of simple IoT sensors (no visual data) and standalone AI apps (no environmental context).
*   **Proposed Solution**: Highlight your **Novelty**—the "Context-Aware Intelligence Pipeline" that fuses Vision + Weather + Expert Rules.

### Chapter 3: System Architecture
*   **Frontend**: React.js Dashboard for visualization and control.
*   **Backend**: Flask (Python) exposing REST APIs (`/vision`, `/remedy`, `/chat`).
*   **Micro-Services**:
    *   *Vision Engine*: YOLOv8 for object detection.
    *   *Weather Service*: OpenWeatherMap API wrapper.
    *   *Remedy Engine*: Logic core for decision making.
*   **Database**: SQLite for storing logs and sensor history.

### Chapter 4: Methodology
*   **Dataset**: Describe the PlantVillage dataset (Classes, Preprocessing).
*   **Training**: Explain YOLOv8 transfer learning process (Image Size: 640/224, Epochs, Loss Function).
*   **Logic Flow**: Detail the IF-THEN logic used in the Remedy Service (e.g., Rain Check, Wind Constraint).

### Chapter 5: Results
*   **Metrics**: mAP scores, Precision/Recall tables.
*   **System Performance**: Latency analysis (Inference time vs API response time).
*   **Screenshots**: Visual proof of system operation (Healthy vs Diseased).

### Chapter 6: Conclusion & Future Scope
*   Summary of achievements and list of future enhancements (Edge devices, Drones).

---

## 2. System Architecture Diagram (Textual Representation)

```plaintext
                                      +------------------+
                                      |   EXTERNAL APIs  |
          User (Farmer)               |  (OpenWeatherMap)|
               |                      +---------+--------+
               v                                |
      +------------------+                      v
      |  FRONTEND APP    |          +--------------------------+
      | (React.js SPA)   | <------> |      BACKEND CORE        |
      | - Dashboard      |   HTTP/  |     (Flask/Python)       |
      | - Live Stream    |   WS     +--------------------------+
      | - Chat Interface |          |                          |
      +------------------+          |  [ API Gateway / Routes ]|
                                    |     /vision, /remedy     |
                                    |                          |
                                    +------------+-------------+
                                                 |
            +------------------------------------+--------------------------------------+
            |                   |                |                  |                   |
    +-------v-------+   +-------v------+  +------v-------+  +-------v------+    +-------v-------+
    | VISION ENGINE |   | WEATHER SVC  |  | SENSOR SVC   |  | REMEDY ENGINE|    | CHATBOT SVC   |
    | (YOLOv8 + CV2)|   | (API Client) |  | (Data Ingest)|  | (Rule Logic) |    | (NLP/Context) |
    +-------+-------+   +-------+------+  +------+-------+  +-------+------+    +-------+-------+
```

---

## 3. Flowcharts

### A. Image Detection Flow
1.  **Input**: Receive Image (Camera Frame or Upload).
2.  **Preprocess**: Resize to 640x640, Normalize.
3.  **Inference**: Pass through YOLOv8 Neural Network.
4.  **Filter**: Apply Non-Maximum Suppression (NMS) & Confidence Threshold (>0.5).
5.  **Output**: Return properties of detected objects (Class, Conf, BBox).

### B. Smart Remedy Prediction Flow
1.  **Start**: Disease Detected (e.g., "Fungal Blight").
2.  **Get Context**: Fetch Weather (Rain: Yes, Wind: 18km/h).
3.  **Rule Check 1 (Safety)**: Is Wind > 15km/h?
    *   *YES*: **STOP**. Return "Delay Spraying (Drift Risk)".
    *   *NO*: Continue.
4.  **Rule Check 2 (Efficacy)**: Is Rain Forecasted?
    *   *YES*: **STOP**. Return "Wait for dry weather".
    *   *NO*: Continue.
5.  **Rule Check 3 (Urgency)**: Is Humidity > 80% & Disease == Fungal?
    *   *YES*: Set Priority = **CRITICAL**.
6.  **Final Output**: Return structured recommendation (Action + Reason + Priority).

---

## 4. Evaluation Metrics
*   **mAP @ 0.5**: Global accuracy score. Higher is better (Target > 0.85).
*   **Precision**: "False Alarm Rate". measures how many detections were correct. High precision = few false alarms.
*   **Recall**: "Miss Rate". Measures how many actual diseases were found. High recall = few missed diseases.
*   **Inference Time**: Time for model to process one image (Target < 100ms on CPU).

---

## 5. Viva Voce Cheat Sheet (Q&A)

**Q1: Why did you choose YOLOv8?**
*   **A:** It is a single-stage detector, offering the best balance of speed (Real-time FPS) and accuracy compared to older models like R-CNN.

**Q2: How does the "Intelligence" work?**
*   **A:** It's not just object detection. We implemented a deterministic Rule Engine that cross-references detections with Weather Data. For example, it prevents recommending pesticide sprays during high winds or rain.

**Q3: Is the Chatbot "AI"?**
*   **A:** It uses a Retrieval-Based approach for safety. Generative AI (LLMs) can hallucinate dangerous advice. We prioritized reliability by using hard-coded expert rules for agricultural queries.

**Q4: What happens if the Camera is blocked?**
*   **A:** The Vision service will simply return no detections. The Dashboard will show "Monitoring..." status.

**Q5: What is the future scope?**
*   **A:** Deployment on Edge Devices (Raspberry Pi), Drones for field scanning, and Multilingual support for local farmers.

---

## 6. Industry Relevance
*   **Precision Agriculture**: Reduces chemical waste by targeting only infected areas and spraying only when weather permits.
*   **Accessibility**: Brings expert agronomist knowledge to anyone with a smartphone.
*   **Scalability**: The modular micro-service design allows adding new crops/models easily.
