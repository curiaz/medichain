import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, Send, Bot, User, Loader2, CheckCircle } from 'lucide-react';
import { aiService } from '../services/aiService';

const ConversationalAI = ({ onDiagnosisComplete }) => {
  const [messages, setMessages] = useState([]);
  const [currentInput, setCurrentInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationStage, setConversationStage] = useState('initial');
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [progress, setProgress] = useState(0);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Initial greeting
    setMessages([{
      id: 1,
      type: 'bot',
      content: "Hello! I'm your AI health assistant. I'll ask you a few questions to better understand your symptoms and provide an accurate diagnosis. Let's start - what symptoms are you experiencing?",
      timestamp: new Date()
    }]);
  }, []);

  const startConversation = async (initialSymptoms) => {
    setIsLoading(true);
    try {
      const response = await aiService.startConversation({ symptoms: initialSymptoms });
      
      if (response.success) {
        const { conversation_data } = response;
        setProgress(conversation_data.progress);
        
        // Add user message
        const userMessage = {
          id: messages.length + 1,
          type: 'user',
          content: initialSymptoms,
          timestamp: new Date()
        };
        
        // Add bot response with follow-up question
        const botMessage = {
          id: messages.length + 2,
          type: 'bot',
          content: `I can see you're experiencing: ${Object.keys(conversation_data.detected_symptoms).filter(k => conversation_data.detected_symptoms[k] === 1).join(', ')}. Let me ask you some follow-up questions for a more accurate diagnosis.`,
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev, userMessage, botMessage]);
        
        if (conversation_data.next_question) {
          setCurrentQuestion(conversation_data.next_question);
          setTimeout(() => {
            askNextQuestion(conversation_data.next_question);
          }, 1000);
        }
        
        setConversationStage('gathering_info');
      }
    } catch (error) {
      console.error('Failed to start conversation:', error);
      addBotMessage('Sorry, I encountered an error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const continueConversation = async (userResponse, questionId) => {
    setIsLoading(true);
    try {
      const response = await aiService.continueConversation({
        response: userResponse,
        question_id: questionId
      });
      
      if (response.success) {
        const { conversation_data } = response;
        setProgress(conversation_data.progress || progress);
        
        if (conversation_data.conversation_stage === 'diagnosis_complete') {
          // Show final diagnosis
          addBotMessage('Thank you for providing all that information. Based on our conversation, here\'s my diagnosis:');
          setTimeout(() => {
            onDiagnosisComplete(conversation_data);
          }, 1000);
        } else if (conversation_data.next_question) {
          setCurrentQuestion(conversation_data.next_question);
          setTimeout(() => {
            askNextQuestion(conversation_data.next_question);
          }, 500);
        } else {
          addBotMessage('Thank you for that information. Let me analyze everything now...');
          // Force complete the conversation if no more questions
          setTimeout(() => {
            onDiagnosisComplete(conversation_data);
          }, 1000);
        }
      }
    } catch (error) {
      console.error('Failed to continue conversation:', error);
      addBotMessage('Sorry, I encountered an error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const askNextQuestion = (questionData) => {
    const questionMessage = {
      id: messages.length + 1,
      type: 'bot',
      content: questionData.question,
      options: questionData.options,
      questionId: questionData.question_id,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, questionMessage]);
  };

  const addBotMessage = (content) => {
    const botMessage = {
      id: messages.length + 1,
      type: 'bot',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, botMessage]);
  };

  const handleSendMessage = () => {
    if (!currentInput.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content: currentInput,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);

    if (conversationStage === 'initial') {
      startConversation(currentInput);
    } else if (currentQuestion) {
      continueConversation(currentInput, currentQuestion.question_id);
    }

    setCurrentInput('');
  };

  const handleOptionClick = (option, questionId) => {
    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content: option,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    continueConversation(option, questionId);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <MessageCircle className="w-6 h-6" />
            <h2 className="text-xl font-semibold">AI Health Assistant</h2>
          </div>
          {progress > 0 && (
            <div className="flex items-center space-x-2">
              <span className="text-sm">Progress: {progress}%</span>
              <div className="w-20 h-2 bg-white/20 rounded-full">
                <div 
                  className="h-full bg-white rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="h-96 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex items-start space-x-2 max-w-xs lg:max-w-md ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                message.type === 'user' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-200 text-gray-600'
              }`}>
                {message.type === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>
              <div className={`rounded-lg p-3 ${
                message.type === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}>
                <p className="text-sm">{message.content}</p>
                
                {/* Option buttons for bot messages */}
                {message.type === 'bot' && message.options && (
                  <div className="mt-3 space-y-2">
                    {message.options.map((option, index) => (
                      <button
                        key={index}
                        onClick={() => handleOptionClick(option, message.questionId)}
                        className="block w-full text-left px-3 py-2 bg-white text-gray-700 rounded border border-gray-200 hover:bg-gray-50 transition-colors text-sm"
                        disabled={isLoading}
                      >
                        {option}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-start space-x-2">
              <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center">
                <Bot className="w-4 h-4" />
              </div>
              <div className="bg-gray-100 rounded-lg p-3">
                <div className="flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-sm text-gray-600">AI is thinking...</span>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={currentInput}
            onChange={(e) => setCurrentInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !currentInput.trim()}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          You can type your response or click the suggested options above
        </p>
      </div>
    </div>
  );
};

export default ConversationalAI;
