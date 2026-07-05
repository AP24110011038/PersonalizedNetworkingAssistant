# Task 2: Model Research & Selection

## Overview

Choosing the right AI model is an important step in building the Personalized Networking Assistant. The selected models should provide accurate results while maintaining fast response times and efficient resource usage.

---

## Theme Extraction Model

### Selected Model
**DistilBERT**

### Reason for Selection

DistilBERT was selected for event theme extraction because it supports zero-shot text classification, allowing the application to classify event descriptions without requiring task-specific training data.

### Advantages

- Fast inference speed
- Good classification accuracy
- Lightweight architecture
- Suitable for real-time applications
- Efficient deployment on limited hardware

### Use Case

The model analyzes event descriptions and identifies important themes, enabling the application to generate relevant networking suggestions.

---

## Conversation Generation Model

### Selected Model
**GPT-2 Small**

### Reason for Selection

GPT-2 Small was chosen because it generates natural and contextually relevant conversation starters while remaining lightweight enough to run efficiently on standard hardware.

### Advantages

- Generates coherent text
- Fast inference without GPU
- Easy integration using the Hugging Face Pipeline API
- Suitable for short professional conversation starters

### Use Case

The model creates engaging conversation starters based on the user's profile and event context to improve networking interactions.

---

## Conclusion

DistilBERT and GPT-2 Small together provide an effective balance between performance, accuracy, and computational efficiency. DistilBERT handles event theme classification, while GPT-2 Small generates natural conversation starters, making them well suited for the Personalized Networking Assistant.
