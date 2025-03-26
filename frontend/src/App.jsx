import React, { useState, useEffect, useRef } from "react";
import { FiSend } from "react-icons/fi";
import { AiOutlineLoading3Quarters } from "react-icons/ai";
import ScrollToBottom from "react-scroll-to-bottom";
import axios from "axios";
import logo from "./assets/nutribot_logo.webp"; // ✅ NutriBot Logo
import "./index.css";

const ChatDashboard = () => {
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [showOptions, setShowOptions] = useState(true); // ✅ Show Quick Action Buttons Initially
  const [inputEnabled, setInputEnabled] = useState(false); // ❌ Hide Input Initially
  const bottomRef = useRef(null);

  const handleSend = async (text) => {
    const userMessage = text || message.trim();
    if (!userMessage) return;

    setMessages((prev) => [...prev, { text: userMessage, user: true }]);
    setMessage("");
    setLoading(true);
    setShowOptions(false); // ✅ Hide Options After First Message
    setInputEnabled(true); // ✅ Show Input Box

    try {
      const response = await axios.post("http://localhost:5000/webhook", {
        queryResult: { intent: { displayName: userMessage }, queryText: userMessage },
      });
      console.log("🔹 Full Response from Backend:", response.data.fulfillmentText); // ✅ Debugging

      const botResponse = response.data.fulfillmentText || "Failed to get a response from the backend.";
      setMessages((prev) => [...prev, { text: botResponse, user: false }]);
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [...prev, { text: `Error: ${error.message}`, user: false }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && inputEnabled) {
      e.preventDefault();
      handleSend();
    }
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex justify-center w-full h-screen py-5 bg-gray-50">
      <div className="flex flex-col w-11/12 h-full overflow-hidden bg-white rounded-lg shadow-lg md:w-8/12 lg:w-6/12">
        {/* ✅ Header with Logo */}
        <header className="flex items-center justify-between p-4 bg-blue-600 text-white">
          <div className="text-xl font-semibold">NutriBot</div>
          <img src={logo} alt="NutriBot Logo" className="w-10 h-10 rounded-full" />
        </header>

        {/* ✅ Centered Grid Menu for Quick Actions */}
        {showOptions ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="p-4 grid grid-cols-2 gap-3 text-center">
              {["What is Balanced Diet?", "Vegan Meal Ideas", "Recommend Recipes", "Healthy Meal"].map((option) => (
                <button
                  key={option}
                  className="px-3 py-2 text-blue-600 bg-white border border-blue-500 rounded-lg hover:bg-blue-500 hover:text-white"
                  onClick={() => handleSend(option)}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {/* ✅ Chat Messages */}
            <div className="flex-1 p-4 overflow-y-auto">
              <ScrollToBottom className="flex-1">
                {messages.length === 0 && <div className="text-gray-400 text-center mt-10">Ask me anything about nutrition! 🍏</div>}
                {messages.map((msg, index) => (
                  <div key={index} className={`mb-4 flex ${msg.user ? "justify-end" : "justify-start"}`}>
                    <span className={`inline-block max-w-lg break-words px-4 py-2 rounded-lg shadow ${msg.user ? "bg-blue-100 text-right" : "bg-gray-100 text-left"}`}>
                      {msg.text.split("\n").map((line, i) => (
                        <React.Fragment key={i}>
                          {line}
                          <br />
                        </React.Fragment>
                      ))}
                    </span>
                  </div>
                ))}


                {/* ✅ Typing Indicator */}
                {loading && (
                  <div className="mb-4 flex justify-start">
                    <span className="inline-block px-4 py-2 text-gray-600 bg-gray-200 rounded-lg shadow">
                      <AiOutlineLoading3Quarters className="animate-[spin_1.5s_linear_infinite] inline mr-2" />
                      Thinking... 🤔
                    </span>
                  </div>
                )}

                <div ref={bottomRef} />
              </ScrollToBottom>
            </div>

            {/* ✅ Input Box (Appears After Option Selection) */}
            {inputEnabled && (
              <form className="flex p-4 space-x-2 bg-gray-100" onSubmit={(e) => e.preventDefault()}>
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={handleKeyDown} // ✅ Handle "Enter" Key
                  placeholder="Type a message e.g., Track Meal, Recommend Recipes..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg outline-none bg-white"
                  aria-label="Message Input"
                />
                <button
                  type="button"
                  onClick={() => handleSend()}
                  className="flex items-center justify-center px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={loading}
                  aria-label="Send Message"
                >
                  <FiSend className="text-xl" />
                </button>
              </form>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default ChatDashboard;


