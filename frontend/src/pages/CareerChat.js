import React, { useState, useEffect, useRef } from "react";
import { useAuth } from "@/contexts/AuthContext";
import Layout from "@/components/Layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Send, Bot, User, MessageCircle, Loader2, Lightbulb, BookOpen, Target } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";

const CareerChat = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Add welcome message
    setMessages([
      {
        id: 1,
        type: "bot",
        content: `Hello ${user?.full_name}! I'm your AI career counselor. I'm here to help you with career guidance, job search strategies, interview preparation, and skill development. What would you like to discuss today?`,
        timestamp: new Date(),
      },
    ]);
  }, [user?.full_name]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || loading) return;

    const newUserMessage = {
      id: Date.now(),
      type: "user",
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newUserMessage]);
    setInputMessage("");
    setLoading(true);

    try {
      const response = await axios.post(`${API}/ai/career-chat`, {
        message: inputMessage,
        history: messages.map((msg) => ({
          role: msg.type === "user" ? "user" : "assistant",
          content: msg.content,
        })),
      });

      const botMessage = {
        id: Date.now() + 1,
        type: "bot",
        content: response.data.message,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      toast.error("Failed to send message. Please try again.");
      
      const errorMessage = {
        id: Date.now() + 1,
        type: "bot",
        content: "I'm sorry, I'm having trouble responding right now. Please try again in a moment.",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const quickQuestions = [
    {
      icon: Target,
      title: "Career Path",
      question: "What career path should I consider based on my skills?",
    },
    {
      icon: BookOpen,
      title: "Skill Development",
      question: "What skills should I learn to advance my career?",
    },
    {
      icon: MessageCircle,
      title: "Interview Tips",
      question: "Can you give me tips for my upcoming interview?",
    },
    {
      icon: Lightbulb,
      title: "Job Search",
      question: "How can I improve my job search strategy?",
    },
  ];

  const handleQuickQuestion = (question) => {
    setInputMessage(question);
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <Layout title="Career Chat">
      <div className="max-w-4xl mx-auto h-[calc(100vh-12rem)]">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-full">
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">AI Career Counselor</CardTitle>
                <CardDescription>
                  Get personalized career guidance and advice
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Bot className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium">Online</span>
                  </div>
                  <div className="text-sm text-gray-600">
                    Ask me about:
                  </div>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Career planning</li>
                    <li>• Skill development</li>
                    <li>• Interview preparation</li>
                    <li>• Resume improvement</li>
                    <li>• Job search strategies</li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            {/* Quick Questions */}\n            <Card>\n              <CardHeader>\n                <CardTitle className="text-lg">Quick Start</CardTitle>\n              </CardHeader>\n              <CardContent className="space-y-2">\n                {quickQuestions.map((q, index) => (\n                  <Button\n                    key={index}\n                    variant="outline"\n                    size="sm"\n                    className="w-full justify-start text-left h-auto p-3"\n                    onClick={() => handleQuickQuestion(q.question)}\n                  >\n                    <q.icon className="h-4 w-4 mr-2 flex-shrink-0" />\n                    <div>\n                      <div className="font-medium">{q.title}</div>\n                      <div className="text-xs text-gray-600 mt-1">\n                        {q.question.substring(0, 40)}...\n                      </div>\n                    </div>\n                  </Button>\n                ))}\n              </CardContent>\n            </Card>\n          </div>\n\n          {/* Chat Area */}\n          <Card className="lg:col-span-3 flex flex-col">\n            <CardHeader className="border-b">\n              <CardTitle className="flex items-center gap-2">\n                <MessageCircle className="h-5 w-5" />\n                Career Counseling Chat\n              </CardTitle>\n            </CardHeader>\n\n            {/* Messages */}\n            <CardContent className="flex-1 p-0">\n              <ScrollArea className="h-[calc(100vh-20rem)] p-4">\n                <div className="space-y-4">\n                  {messages.map((message) => (\n                    <div\n                      key={message.id}\n                      className={`flex gap-3 ${\n                        message.type === "user" ? "flex-row-reverse" : ""\n                      }`}\n                    >\n                      <Avatar className="h-8 w-8">\n                        <AvatarFallback>\n                          {message.type === "user" ? (\n                            <User className="h-4 w-4" />\n                          ) : (\n                            <Bot className="h-4 w-4" />\n                          )}\n                        </AvatarFallback>\n                      </Avatar>\n                      <div\n                        className={`flex-1 space-y-2 ${\n                          message.type === "user" ? "text-right" : ""\n                        }`}\n                      >\n                        <div\n                          className={`inline-block p-3 rounded-lg max-w-xs sm:max-w-md lg:max-w-lg ${\n                            message.type === "user"\n                              ? "bg-blue-600 text-white"\n                              : "bg-gray-100 text-gray-900"\n                          }`}\n                        >\n                          <p className="whitespace-pre-wrap">{message.content}</p>\n                        </div>\n                        <p className="text-xs text-gray-500">\n                          {formatTime(message.timestamp)}\n                        </p>\n                      </div>\n                    </div>\n                  ))}\n                  \n                  {loading && (\n                    <div className="flex gap-3">\n                      <Avatar className="h-8 w-8">\n                        <AvatarFallback>\n                          <Bot className="h-4 w-4" />\n                        </AvatarFallback>\n                      </Avatar>\n                      <div className="flex-1">\n                        <div className="inline-block p-3 rounded-lg bg-gray-100">\n                          <div className="flex items-center gap-2">\n                            <Loader2 className="h-4 w-4 animate-spin" />\n                            <span className="text-sm text-gray-600">\n                              Thinking...\n                            </span>\n                          </div>\n                        </div>\n                      </div>\n                    </div>\n                  )}\n                  \n                  <div ref={messagesEndRef} />\n                </div>\n              </ScrollArea>\n            </CardContent>\n\n            {/* Input */}\n            <div className="border-t p-4">\n              <form onSubmit={handleSendMessage} className="flex gap-2">\n                <Input\n                  value={inputMessage}\n                  onChange={(e) => setInputMessage(e.target.value)}\n                  placeholder="Ask me anything about your career..."\n                  disabled={loading}\n                  className="flex-1"\n                />\n                <Button type="submit" disabled={loading || !inputMessage.trim()}>\n                  <Send className="h-4 w-4" />\n                </Button>\n              </form>\n            </div>\n          </Card>\n        </div>\n      </div>\n    </Layout>\n  );\n};\n\nexport default CareerChat;