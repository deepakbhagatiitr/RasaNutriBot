import React, { useState, useEffect, useRef } from 'react';
import { MdFace } from "react-icons/md";
import { FiSend } from "react-icons/fi";
import { AiOutlineLoading3Quarters } from "react-icons/ai";
import ScrollToBottom from 'react-scroll-to-bottom';
import axios from 'axios';
import logo from './assets/nutribot_logo.webp'; // ✅ Add Logo
import './index.css';

const ChatDashboard = () => {
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  const handleSend = async (e) => {
    e.preventDefault();
    if (message.trim()) {
      setMessages((prevMessages) => [...prevMessages, { text: message, user: true }]);
      setMessage('');
      setLoading(true);

      try {
        const response = await axios.post('http://localhost:5000/webhook', {
          queryResult: { intent: { displayName: message }, queryText: message }
        });

        const botResponse = response.data.fulfillmentText || 'Failed to get an answer from the backend.';
        setMessages((prevMessages) => [...prevMessages, { text: botResponse, user: false }]);
      } catch (error) {
        console.error('Error:', error);
        setMessages((prevMessages) => [...prevMessages, { text: `Error contacting backend: ${error.message}`, user: false }]);
      } finally {
        setLoading(false);
      }
    } else {
      alert("Enter a message");
    }
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex justify-center w-full h-screen py-5 bg-gray-50">
      <div className="flex flex-col w-11/12 h-full overflow-hidden bg-white rounded-lg shadow-lg md:w-8/12 lg:w-6/12">

        {/* Header with Logo */}
        <header className="flex items-center justify-between p-4 bg-blue-600 text-white">
          <div className="flex items-center">
            <div className="text-xl font-semibold">NutriBot</div>
          </div>
          <img src={logo} alt="NutriBot Logo" className="w-10 h-10 mr-3 rounded-full" />

        </header>

        {/* Chat Messages */}
        <div className="flex-1 p-4 overflow-y-auto">
          <ScrollToBottom className="flex-1">
            {messages.length === 0 && (
              <div className="text-gray-400 text-center mt-10">Ask me anything about nutrition! 🍏</div>
            )}
            {messages.map((msg, index) => (
              <div key={index} className={`mb-4 flex ${msg.user ? 'justify-end' : 'justify-start'}`}>
                <span className={`inline-block max-w-lg break-words px-4 py-2 rounded-lg shadow ${msg.user ? 'bg-blue-100 text-right' : 'bg-gray-100 text-left'}`}>
                  {msg.text}
                </span>
              </div>
            ))}

            {/* Typing Indicator with Animated Dots */}
            {loading && (
              <div className="mb-4 flex justify-start">
                <span className="inline-block px-4 py-2 text-gray-600 bg-gray-200 rounded-lg shadow">
                  <AiOutlineLoading3Quarters className="animate-spin inline mr-2" /> NutriBot is typing<span className="dot-flash">...</span>
                </span>
              </div>
            )}

            <div ref={bottomRef} />
          </ScrollToBottom>
        </div>

        {/* Input Box */}
        <form className="flex p-4 space-x-2 bg-gray-100" onSubmit={handleSend}>
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type a message e.g., Track Meal, Recommend Recipes..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg outline-none bg-white"
            aria-label="Message Input"
          />

          <button
            type="submit"
            className="flex items-center justify-center px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
            aria-label="Send Message"
          >
            <FiSend className="text-xl" />
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatDashboard;
