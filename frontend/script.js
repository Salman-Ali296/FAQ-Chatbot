// Flask backend URL
const API_URL = "http://127.0.0.1:5000/api/chat";

const messagesEl = document.getElementById("chatMessages");
const inputEl = document.getElementById("chatInput");
const sendBtn = document.getElementById("chatSend");
const resetBtn = document.getElementById("resetChat");

// Auto-scroll to bottom
function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

// Add message to chat
function appendMessage(text, sender, meta) {
  const wrapper = document.createElement("div");
  wrapper.className = `message message--${sender}`;

  if (sender === "bot") {
    const avatar = document.createElement("div");
    avatar.className = "message__avatar";
    avatar.textContent = "🤖";
    wrapper.appendChild(avatar);
  }

  const content = document.createElement("div");
  content.className = "message__content";

  const bubble = document.createElement("div");
  bubble.className = "message__bubble";
  
  // Handle line breaks in text
  if (text.includes('\n')) {
    bubble.innerHTML = text.replace(/\n/g, '<br>');
  } else {
    bubble.textContent = text;
  }
  
  content.appendChild(bubble);

  if (meta) {
    const metaEl = document.createElement("div");
    metaEl.className = "message__meta";
    metaEl.textContent = meta;
    content.appendChild(metaEl);
  }

  const timestamp = document.createElement("div");
  timestamp.className = "message__timestamp";
  timestamp.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  content.appendChild(timestamp);

  wrapper.appendChild(content);
  messagesEl.appendChild(wrapper);
  scrollToBottom();
  return wrapper;
}

// Show typing indicator
function showTypingIndicator() {
  const wrapper = document.createElement("div");
  wrapper.className = "message message--bot";
  wrapper.id = "typingIndicator";

  const avatar = document.createElement("div");
  avatar.className = "message__avatar";
  avatar.textContent = "🤖";
  wrapper.appendChild(avatar);

  const content = document.createElement("div");
  content.className = "message__content";

  const bubble = document.createElement("div");
  bubble.className = "message__bubble typing";
  bubble.innerHTML = "<span></span><span></span><span></span>";
  content.appendChild(bubble);

  wrapper.appendChild(content);
  messagesEl.appendChild(wrapper);
  scrollToBottom();
}

// Remove typing indicator
function removeTypingIndicator() {
  const el = document.getElementById("typingIndicator");
  if (el) el.remove();
}

// Send message
async function sendMessage() {
  const text = inputEl.value.trim();
  if (!text) return;

  appendMessage(text, "user");
  inputEl.value = "";
  sendBtn.disabled = true;
  showTypingIndicator();

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    if (!res.ok) {
      throw new Error(`Server responded with ${res.status}`);
    }

    const data = await res.json();
    removeTypingIndicator();

    // Determine meta info based on intent
    let meta = "";
    if (data.intent === "greeting") {
      meta = "👋 greeting";
    } else if (data.intent === "thankyou") {
      meta = "🙏 thank you";
    } else if (data.intent === "goodbye") {
      meta = "👋 goodbye";
    } else if (data.intent === "help") {
      meta = "❓ help";
    } else if (data.intent === "fallback") {
      const confidencePct = Math.round((data.score || 0) * 100);
      meta = `🤔 best guess ${confidencePct}%`;
    } else if (data.matched) {
      const confidencePct = Math.round((data.score || 0) * 100);
      meta = `✅ matched: "${data.matched_question}" · ${confidencePct}% confidence`;
    } else {
      const confidencePct = Math.round((data.score || 0) * 100);
      meta = `🤔 best guess ${confidencePct}%`;
    }

    appendMessage(data.answer, "bot", meta);
  } catch (err) {
    removeTypingIndicator();
    appendMessage(
      "⚠️ I couldn't reach the support server. Make sure the backend is running on port 5000.",
      "bot"
    );
    console.error("Error:", err);
  } finally {
    sendBtn.disabled = false;
    inputEl.focus();
  }
}

// Reset chat
function resetChat() {
  const messages = document.getElementById("chatMessages");
  messages.innerHTML = '';
  
  const welcomeDiv = document.createElement("div");
  welcomeDiv.className = "message message--bot";
  welcomeDiv.innerHTML = `
    <div class="message__avatar">🤖</div>
    <div class="message__content">
      <div class="message__bubble">
        Hey! I'm the Tech Deal Store support bot. Ask me about orders,
        shipping, returns, payments, or your account.
      </div>
      <div class="message__timestamp">Just now</div>
    </div>
  `;
  messages.appendChild(welcomeDiv);
  
  inputEl.focus();
}

// Event Listeners
sendBtn.addEventListener("click", sendMessage);
resetBtn.addEventListener("click", resetChat);

inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

inputEl.focus();