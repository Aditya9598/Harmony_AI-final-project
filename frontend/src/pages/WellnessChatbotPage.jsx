import { useState } from "react";
import { api } from "../api/client";

export default function WellnessChatbotPage() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (event) => {
    event.preventDefault();
    if (!message.trim()) return;

    const userMsg = { role: "user", content: message.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setMessage("");
    setLoading(true);

    try {
      const { data } = await api.post("/chat", { message: userMsg.content });
      setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
    } catch (error) {
      const fallback = error?.response?.data?.detail || "Chat service is unavailable right now.";
      setMessages((prev) => [...prev, { role: "assistant", content: fallback }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="grid gap-6 lg:grid-cols-[1fr_280px]">
      <div className="glass-card p-6">
        <h2 className="text-2xl font-semibold text-white">Mental Wellness Chatbot</h2>
        <p className="mt-2 text-sm text-slate-300">
          Ask about stress, anxiety, loneliness, motivation, confidence, and inner peace.
        </p>

        <div className="mt-5 h-[420px] overflow-y-auto rounded-xl border border-white/20 bg-black/20 p-4">
          {messages.length === 0 && (
            <p className="text-sm text-slate-300">Start with: "I feel overwhelmed and anxious lately."</p>
          )}
          {messages.map((item, index) => (
            <div key={`${item.role}-${index}`} className={`mb-3 flex ${item.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap ${
                  item.role === "user" ? "bg-harmony-500 text-white" : "bg-white/15 text-slate-100"
                }`}
              >
                {item.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="mb-3 flex justify-start">
              <div className="rounded-2xl bg-white/15 px-4 py-3 text-sm text-slate-100">Harmony AI is typing...</div>
            </div>
          )}
        </div>

        <form onSubmit={sendMessage} className="mt-4 flex gap-3">
          <input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Share what you are feeling..."
            className="w-full rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-sm text-white placeholder:text-slate-300"
          />
          <button
            type="submit"
            disabled={loading}
            className="rounded-xl bg-harmony-500 px-5 py-3 text-white disabled:opacity-60"
          >
            Send
          </button>
        </form>
      </div>

      <aside className="glass-card p-5">
        <h3 className="text-lg font-semibold text-white">Allowed Topics</h3>
        <ul className="mt-3 space-y-2 text-sm text-slate-200">
          {[
            "depression",
            "anxiety",
            "loneliness",
            "stress",
            "overthinking",
            "motivation",
            "sadness",
            "emotional pain",
            "self doubt",
            "fear",
            "confidence",
            "life balance",
            "inner peace",
          ].map((topic) => (
            <li key={topic} className="rounded-lg bg-white/10 px-3 py-2">
              {topic}
            </li>
          ))}
        </ul>
      </aside>
    </section>
  );
}
