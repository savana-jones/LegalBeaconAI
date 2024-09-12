import { useState, useEffect, useRef } from "react";
import { FaArrowUp } from "react-icons/fa";
import { marked } from 'marked';

// Configure marked to support line breaks and bullet points
marked.setOptions({
  gfm: true, // GitHub Flavored Markdown
  breaks: true, // Preserve newlines
});

const Chatbot = () => {
  const [messages, setMessages] = useState<{ text: string; type: "user" | "bot" }[]>([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const typeWriterEffect = (text: string) => {
    let index = 0;
    setTyping("");

    const typingInterval = setInterval(() => {
      setTyping((prev) => (prev || "") + text.charAt(index));
      index += 1;
      if (index >= text.length) {
        clearInterval(typingInterval);
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: text, type: "bot" }
        ]);
        setTyping(null);
      }
    }, 5);
  };

  const handleSendMessage = async () => {
    if (input.trim()) {
      const userMessage = { text: input, type: "user" as const };
      setMessages((prevMessages) => [...prevMessages, userMessage]);

      try {
        const response = await fetch("http://localhost:5000/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ messages: input }),
        });

        const data = await response.json();
        let botResponse = data.response || "";
        botResponse = botResponse.replace(/^ANSWER>\s*/, "");
        typeWriterEffect(botResponse);

      } catch (error) {
        console.error("Error:", error);
      }

      setInput("");
      autoResizeTextarea(); // Ensure it resizes back when message is sent
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const autoResizeTextarea = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  // Call autoResizeTextarea whenever input changes
  useEffect(() => {
    autoResizeTextarea();
  }, [input]);

  return (
    <div className="flex flex-col h-screen">
      <div className="flex-grow p-4 overflow-y-auto">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`my-2 p-2 max-w-3xl ${
              msg.type === "user"
                ? "ml-auto bg-blue-500 text-white"
                : "bg-gray-200 text-black inline-block"
            } rounded-lg`}
          >
            <div
              dangerouslySetInnerHTML={{ __html: marked(msg.text) }}
              className="preserve-markdown-content"
            />
          </div>
        ))}
        {typing && (
          <div className="my-2 p-2 max-w-3xl bg-gray-200 text-black inline-block rounded-lg">
            {typing}
          </div>
        )}
      </div>
      <div className="p-4 bg-gray-100">
        <div className="flex items-center">
          <textarea
            ref={textareaRef}
            className="flex-grow p-3 border border-gray-300 rounded-md resize-none overflow-auto"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            onInput={autoResizeTextarea} // Resize as user types
            placeholder="Type your message..."
            rows={1} // Start with one row
          />
          <button
            onClick={handleSendMessage}
            className="ml-2 p-2 text-white bg-black rounded-full flex items-center justify-center"
          >
            <FaArrowUp />
          </button>
        </div>
        <div className="text-xs text-center text-gray-500 mt-1">
          LegalBeacon may make mistakes.
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
