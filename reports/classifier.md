# Classifier report (Neural network)

Tokenizer: `simple_v1`  (local test run, NOT the Netlify model)
Test set: seed questions, split=test
Train rows: 192  Test rows: 48
Accuracy: 0.667  Macro F1: 0.639

| Category | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| printer | 0.62 | 0.83 | 0.71 | 6 |
| email | 1.00 | 0.17 | 0.29 | 6 |
| wifi | 0.57 | 0.67 | 0.62 | 6 |
| passwords | 0.40 | 0.33 | 0.36 | 6 |
| slow | 0.86 | 1.00 | 0.92 | 6 |
| phone_apps | 0.71 | 0.83 | 0.77 | 6 |
| files | 0.80 | 0.67 | 0.73 | 6 |
| video_calls | 0.62 | 0.83 | 0.71 | 6 |

## Mistakes (up to 5)
- "my modem has 5 lights and only one is green, is that bad": true wifi, predicted printer (0.57)
- "why does my laptop ask for a password when I wake it up from sleep": true passwords, predicted printer (0.59)
- "Can I use Face ID to unlock my Windows laptop?": true passwords, predicted video_calls (0.80)
- "Canon printer not connecting to wifi after i changed my router": true printer, predicted wifi (0.98)
- "My Apple ID is asking for a verification code but my phone number changed": true passwords, predicted phone_apps (0.69)
