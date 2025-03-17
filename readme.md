# **Rasa NutriBot**  

**Rasa NutriBot** is an AI-powered **intelligent nutrition assistant** that provides personalized dietary recommendations and meal suggestions based on user preferences. The chatbot leverages **Natural Language Processing (NLP)** and integrates with the **Nutritionix API** to offer **scientifically-backed nutrition guidance** in real time.  

This project is built using **Rasa for conversational AI**, **Flask as the backend**, and a **React-based frontend**, ensuring a smooth and interactive user experience.

---

## **🚀 Features**  

✔ **AI-Driven Conversational Chatbot** – Understands and responds to nutrition-related queries.  
✔ **Personalized Meal Recommendations** – Suggests meals based on diet preferences (vegan, keto, high-protein, etc.).  
✔ **Calorie & Nutrient Tracking** – Retrieves real-time nutritional data from the **Nutritionix API**.  
✔ **Diet-Based Customization** – Adapts meal suggestions according to **user goals** (weight loss, muscle gain, etc.).  
✔ **Interactive Web Interface** – Seamless user experience with a modern **React-based UI**.  
✔ **Scalable & Modular Architecture** – Backend powered by **Flask**, making it **lightweight and extendable**.  
✔ **Real-Time Response Optimization** – Utilizes NLP models to process user queries accurately.  

---

## **📌 Project Structure**  
```
rasa-nutribot/
│── frontend/         # Frontend (React)
│── backend/          # Flask API Backend
│── rasa/             # Rasa Chatbot (Conversational AI)
│── README.md         # Project Documentation
```

---

## **🔧 Installation & Setup**  

### **1️⃣ Frontend (React) Setup**  
1. Navigate to the `frontend` directory:  
   ```sh
   cd frontend
   ```
2. Install dependencies:  
   ```sh
   npm install
   ```
3. Start the development server:  
   ```sh
   npm run dev
   ```
The frontend will be accessible at the local server URL provided.

---

### **2️⃣ Backend (Flask) Setup**  
1. Navigate to the `backend` directory:  
   ```sh
   cd backend
   ```
2. Install required Python dependencies:  
   ```sh
   pip install -r requirements.txt
   ```
3. Run the Flask backend server:  
   ```sh
   python app.py
   ```
---

### **3️⃣ Rasa Chatbot Setup**  
1. Navigate to the `rasa` directory:  
   ```sh
   cd rasa
   ```
2. Train the Rasa model (if not already trained):  
   ```sh
   rasa train
   ```
3. Start the Rasa actions server:  
   ```sh
   rasa run actions
   ```
4. Run the Rasa chatbot in interactive mode:  
   ```sh
   rasa shell
   ```
---

## **🛠 Technical Stack**  

- **Frontend:** React.js, TailwindCSS  
- **Backend:** Flask (Python-based API server)  
- **Chatbot Engine:** Rasa (NLP, Intent Recognition, Entity Extraction)  
- **Machine Learning:** SpaCy, nltk
- **Database Integration:** Nutritionix API (Real-time food & calorie data)  

---

## **📜 License**  
This project is licensed under the **MIT License**.  

---

🚀 **Rasa NutriBot – Your AI Nutrition Assistant!** 🚀