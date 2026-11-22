# Classifier report (Neural network)

Tokenizer: `simple_v1`  (local test run, NOT the Netlify model)
Test set: seed questions, split=test
Train rows: 192  Test rows: 48
Accuracy: 0.750  Macro F1: 0.744

| Category | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| printer | 0.83 | 0.83 | 0.83 | 6 |
| email | 1.00 | 0.50 | 0.67 | 4 |
| wifi | 0.50 | 0.60 | 0.55 | 5 |
| passwords | 1.00 | 0.56 | 0.71 | 9 |
| slow | 1.00 | 0.83 | 0.91 | 6 |
| phone_apps | 0.56 | 1.00 | 0.71 | 5 |
| files | 0.67 | 1.00 | 0.80 | 6 |
| video_calls | 0.83 | 0.71 | 0.77 | 7 |

## Mistakes (up to 5)
- "my modem has 5 lights and only one is green, is that bad": true wifi, predicted printer (0.34)
- "the screen freezes for like 30 seconds and then comes back, over and over": true slow, predicted files (0.53)
- "Can I use Face ID to unlock my Windows laptop?": true passwords, predicted video_calls (0.88)
- "Internet is fine on the computer but Zoom says no network. I don't understand": true video_calls, predicted wifi (0.97)
- "Canon printer not connecting to wifi after i changed my router": true printer, predicted wifi (0.85)
