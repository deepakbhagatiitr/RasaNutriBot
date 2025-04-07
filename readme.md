# 🥗 NutriBot — AI-Powered Personalized Nutrition Chatbot

NutriBot is an **AI-driven conversational chatbot** designed to provide **personalized nutrition and meal recommendations** based on user preferences like diet type (e.g., keto, vegan), nutrient focus (e.g., high-protein), and meal type (breakfast, lunch, dinner). It integrates **Natural Language Processing (NLP)** using **Rasa**, a **Flask backend**, and a modern **React + Tailwind CSS frontend** to deliver real-time, interactive dietary guidance.

> “Eat smart, chat smarter — NutriBot’s got your plate covered!”

---

## 🧠 Core Features

- ✅ **Conversational AI**: Built with Rasa 3.6.21 for intent classification and dialogue flow
- 🍱 **Personalized Meal Suggestions**: Responds to queries like _"Suggest a vegan dinner high in protein"_
- 🔍 **Real-Time Nutrition Data**: Fetches calorie and macro info using the **Nutritionix API**
- 💬 **Multi-turn Conversation**: Remembers context during interactions (slot filling)
- 🖥️ **Modern UI**: Clean, responsive frontend using React.js and Tailwind CSS
- 🐳 **Dockerized Setup**: Easy deployment via Docker Compose across environments
- 🔄 **Custom Actions**: Built-in logic to call APIs and format dynamic responses
- 🚫 **Graceful Fallbacks**: Handles incomplete or irrelevant queries naturally

---

## 🛠️ Tech Stack

| Layer         | Technology              |
|---------------|--------------------------|
| NLP & Dialogue | Rasa (NLU + Core)        |
| Backend       | Flask (Python 3.10.16)    |
| Frontend      | React.js + Tailwind CSS   |
| NLP Libraries | spaCy, Rasa NLU pipeline  |
| Data Source   | [Nutritionix API](https://developer.nutritionix.com/) |
| Deployment    | Docker + Docker Compose   |
| Hosting       | Compatible with Render, Heroku, etc. |

---

## 📁 Project Structure

```
nutribot/
├── rasa/               # Rasa NLU, Core, Actions, Config
├── backend/            # Flask Middleware Server
├── frontend/           # React + Tailwind UI
├── docker-compose.yml  # Multi-service deployment
└── README.md           # Project documentation
```

---

## 🚀 Quick Start Guide

### 🧱 Prerequisites

- Docker & Docker Compose installed
- Node.js (for frontend dev) and Python 3.10+

---

### 🐳 1. Docker-Based Deployment (Recommended)

```bash
# From project root directory
docker-compose up --build
```

- **Frontend:** http://localhost:3000  
- **Backend (Flask):** http://localhost:5001  
- **Rasa Server:** http://localhost:5005  

---

### 🔧 2. Manual Setup (For Development)

#### ➤ Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

#### ➤ Backend (Flask)
```bash
cd backend
pip install -r requirements.txt
python app.py
```

#### ➤ Rasa Chatbot
```bash
cd rasa
rasa train
rasa run actions &
rasa run --enable-api
```

---

## 💬 Example User Queries

| User Message                          | Bot Response                              |
|---------------------------------------|-------------------------------------------|
| "Suggest a low-carb lunch"            | Meal options: Grilled chicken, salad...   |
| "How many calories are in a banana?"  | "A banana has ~105 calories..."           |
| "I want a vegan dinner high in protein" | Suggestions: Tofu quinoa, chickpea salad... |

---

## 🧪 Evaluation

| Metric                   | Result           |
|--------------------------|------------------|
| Intent Accuracy          | > 90% F1-Score   |
| Entity Extraction        | High precision   |
| Response Latency         | < 2 seconds      |
| Error Handling           | Handled with fallback policy |

---

## 🎯 Future Enhancements

- 🧍 Personalized user profiles (health goals, allergies)
- 🌐 Multilingual support using Hugging Face models
- 📱 Voice interaction with Web Speech API
- 🏃 Fitness tracker integrations (Fitbit, Google Fit)
- ⏰ Meal reminders and daily plans (PWA support)
- 📊 Admin dashboard for monitoring usage & logs

---

## ❌ Known Limitations

- Relies on external APIs (rate-limiting may occur)
- No persistent memory or long-term user profiles (yet)
- English-only interface
- No mobile app integration (planned in roadmap)

---

## 📜 References

- [Rasa Open Source](https://rasa.com/)
- [Nutritionix API](https://developer.nutritionix.com/)
- [React Documentation](https://reactjs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Flask Framework](https://flask.palletsprojects.com/)
- [Docker Docs](https://docs.docker.com/)

---

## 📄 License

This project is licensed under the **MIT License**.  

---

🚀 **Rasa NutriBot – Your AI Nutrition Assistant!** 🚀