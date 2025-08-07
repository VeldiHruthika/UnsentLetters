
window.onload = () => {
  const sendBtn = document.getElementById("sendBtn");
  const response = document.getElementById("response");
  const bgMusic = document.getElementById("bg-music");
  const moodSelect = document.getElementById("mood");
  const downloadLatestBtn = document.getElementById("downloadLatestBtn");
  const darkToggle = document.getElementById("darkToggle");
  const voiceToggle = document.getElementById("voiceToggle");
  const micBtn = document.getElementById("micBtn");
  const letterTextarea = document.getElementById("letter");
  const paperThumbnails = document.querySelectorAll(".paper-thumbnails img");
  const signatureInput = document.getElementById("signatureInput");
  let allVoices = [];
window.speechSynthesis.onvoiceschanged = () => {
  allVoices = speechSynthesis.getVoices();
};
  let latestLetter = null;
  let voiceEnabled = voiceToggle ? voiceToggle.checked : true;
  let selectedCustomPaper = null;
  // ===== FONT STYLE CONTROLS ===== //
  let selectedColor = "#2a1f1c";
  let selectedSize = "20px";
  let isBold = false, isItalic = false, isUnderline = false;
  const colorPicker = document.getElementById("fontColorPicker");
  const fontSizeSelect = document.getElementById("fontSizeSelect");
  const boldBtn = document.getElementById("boldToggle");
  const italicBtn = document.getElementById("italicToggle");
  const underlineBtn = document.getElementById("underlineToggle");
  // Apply initial styles to textarea
  letterTextarea.style.color = selectedColor;
  letterTextarea.style.fontSize = selectedSize;
  // Event listeners for controls
  colorPicker?.addEventListener("input", () => {
    selectedColor = colorPicker.value;
    letterTextarea.style.color = selectedColor;
  });
  fontSizeSelect?.addEventListener("change", () => {
    selectedSize = fontSizeSelect.value;
    letterTextarea.style.fontSize = selectedSize;
  });
  boldBtn?.addEventListener("click", () => {
    isBold = !isBold;
    boldBtn.classList.toggle("active");
    letterTextarea.style.fontWeight = isBold ? "bold" : "normal";
  });
  italicBtn?.addEventListener("click", () => {
    isItalic = !isItalic;
    italicBtn.classList.toggle("active");
    letterTextarea.style.fontStyle = isItalic ? "italic" : "normal";
  });
  underlineBtn?.addEventListener("click", () => {
    isUnderline = !isUnderline;
    underlineBtn.classList.toggle("active");
    letterTextarea.style.textDecoration = isUnderline ? "underline" : "none";
  });
  // ===== FONT SELECTION LOGIC ===== //
  const fontOptions = document.querySelectorAll(".font-sample");
  fontOptions.forEach(fontBtn => {
    fontBtn.addEventListener("click", () => {
      fontOptions.forEach(f => f.classList.remove("selected"));
      fontBtn.classList.add("selected");

      selectedFont = fontBtn.getAttribute("data-font");

      // Apply to writing area
      letterTextarea.style.fontFamily = `'${selectedFont}', monospace`;
    });
  });
  const moodMusicMap = {
    "lost-love": "../assets/sounds/one_love_piano.mp3",
    "closure": "../assets/sounds/warm_memories_piano.mp3",
    "anger": "../assets/sounds/burning_wrath.mp3",
    "goodbye": "../assets/sounds/farewell_whispers.mp3",
  };
  const moodTextureMap = {
    "lost-love": "../assets/textures/lost-love.png",
    "closure": "../assets/textures/closure.png",
    "anger": "../assets/textures/anger.png",
    "goodbye": "../assets/textures/goodbye.png",
  };
  moodSelect.addEventListener("change", () => {
    const newSrc = moodMusicMap[moodSelect.value];
    const sourceTag = bgMusic.querySelector("source");
    if (newSrc !== sourceTag.getAttribute("src")) {
      bgMusic.pause();
      sourceTag.setAttribute("src", newSrc);
      bgMusic.load();
      bgMusic.volume = 0.3;
      bgMusic.play().catch(() => {});
    }
  });
  if (voiceToggle) {
    voiceToggle.addEventListener("change", () => {
      voiceEnabled = voiceToggle.checked;
    });
  }
  paperThumbnails.forEach(thumb => {
    thumb.addEventListener("click", () => {
      paperThumbnails.forEach(t => t.classList.remove("selected"));
      thumb.classList.add("selected");
      selectedCustomPaper = thumb.getAttribute("src");
    });
  });
  const flipSound = new Audio("../assets/sounds/page_flip.mp3");
  const crinkleSound = new Audio("../assets/sounds/paper_crinkle.mp3");
  function extractNames(text) {
  let sender = null, recipient = null;
  // Look for From/To pattern
  const fromMatch = text.match(/(?:from[:-]?\s*)([a-zA-Z]+)/i);
  const toMatch = text.match(/(?:to[:-]?\s*)([a-zA-Z]+)/i);
  if (fromMatch) sender = fromMatch[1];
  if (toMatch) recipient = toMatch[1];
  // Fallbacks
  if (!recipient) {
    const greet = text.match(/(?:hi|dear)\s+([a-zA-Z]+)/i);
    if (greet) recipient = greet[1];
  }
  if (!sender) {
    const signOff = text.match(/(?:love|regards|yours)[\s,.!?-]+([a-zA-Z]+)/i);
    if (signOff) sender = signOff[1];
  }
  return { recipient, sender };
}
  async function speakReply(text, recipientName) {
  if (!window.speechSynthesis || !voiceEnabled) return;
  let gender = "female"; // default fallback
  try {
    if (recipientName) {
      const res = await fetch(`https://api.genderize.io?name=${recipientName}`);
      const data = await res.json();
      if (data.gender) gender = data.gender;
    }
  } catch (err) {
    console.warn("⚠️ Genderize failed or offline. Using default female voice.");
  }
  const voices = allVoices.length ? allVoices : speechSynthesis.getVoices();
  let preferredVoices = [];
  if (gender === "male") {
    preferredVoices = [
      "Microsoft Ravi",
      "Microsoft George",
      "Microsoft Mark",
      "Microsoft David",
      "Microsoft Guy Online",
      "Google UK English Male",
      "Google US English Male",
    ];
  } else {
    preferredVoices = [
      "Microsoft Heera",
      "Microsoft Susan",
      "Microsoft Hazel",
      "Microsoft Zira",
      "Microsoft Aria Online",
      "Microsoft Libby Online",
      "Google UK English Female",
      "Google US English Female",
    ];
  }
  let selectedVoice = null;
  // 1️⃣ Try matching by preferred names
  for (const preferred of preferredVoices) {
    selectedVoice = voices.find(v => v.name.toLowerCase().includes(preferred.toLowerCase()));
    if (selectedVoice) break;
  }
  // 2️⃣ Fallback: Any en-IN voice
  if (!selectedVoice) {
    selectedVoice = voices.find(v => v.lang === "en-IN");
  }
  // 3️⃣ Fallback: Just the first available
  if (!selectedVoice && voices.length) {
    selectedVoice = voices[0];
  }
  if (!selectedVoice) {
    console.warn("❌ No voice found.");
    return;
  }
  // ✅ Speak the reply
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.voice = selectedVoice;
  utterance.pitch = 1;
  utterance.rate = 1;
  speechSynthesis.speak(utterance);
  console.log("🔊 Speaking as:", selectedVoice.name);
}
  async function generateLetter(userLetter, mood, recipientName, senderName) {
  const apiKey = "ea1b62c6d441668340582b2cafbdc0bf7baa2ee268ea9f74b6026623e6e3b861"; // <-- replace with your actual valid key
  let moodPrompt = "";
  if (mood === "anger") {
    moodPrompt = `${senderName || "Someone"} wrote an angry letter to ${recipientName || "you"}.\nReply as ${recipientName || "the recipient"}, either defending or explaining your side.`;
  } else if (mood === "closure") {
    moodPrompt = `${senderName || "Someone"} wrote to ${recipientName || "you"} for closure.\nReply as ${recipientName || "the recipient"}, offering peace and sincerity.`;
  } else if (mood === "goodbye") {
    moodPrompt = `${senderName || "Someone"} sent a goodbye to ${recipientName || "you"}.\nReply as ${recipientName || "the one left behind"}, with calm, heartfelt final words.`;
  } else if (mood === "lost-love") {
    moodPrompt = `${senderName || "Someone"} wrote a heartfelt letter to ${recipientName || "their lost love"}.\n\nWrite a poetic reply **as ${recipientName || "the lost love"}**, responding gently and emotionally.`;
  } else {
    moodPrompt = `Reply to this letter: ${userLetter}`;
  }
  try {
    const response = await fetch("https://api.together.xyz/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: "mistralai/Mixtral-8x7B-Instruct-v0.1", // ✅ FREE MODEL
        messages: [
          {
            role: "system",
            content: "You are a poetic, emotionally intelligent letter-writing assistant."
          },
          {
            role: "user",
            content: `${moodPrompt}\n\nTheir Letter:\n${userLetter}`
          }
        ],
        temperature: 0.7
      })
    });
    const data = await response.json();
    console.log("📦 Together API Raw Response:", data);

    if (!data.choices || !data.choices[0]?.message?.content) {
      console.error("❌ AI response is missing or invalid", data);
      throw new Error("Invalid or empty AI reply");
    }
    return data.choices[0].message.content;
  } catch (err) {
    console.error("❌ Error during AI letter generation:", err);
    throw err;
  }
}
 function typeReply(text, element) {
  element.innerHTML = "";
  let index = 0;
  for (const char of text) {
    if (char === "\n") {
      element.appendChild(document.createElement("br"));
      continue;
    }
    const span = document.createElement("span");
    span.classList.add("ink-letter");
    span.style.setProperty("--i", index++);
    // Handle space character safely
    if (char === " ") {
      span.innerHTML = "&nbsp;";
    } else {
      span.textContent = char;
    }
    element.appendChild(span);
  }
}
  function addToArchive(userText, aiReply, mood) {
    const archiveList = document.getElementById("archive-list");
    const entry = document.createElement("div");
    entry.classList.add("archived-letter");
    const userHTML = userText.replace(/\n/g, "<br/>");
    const replyHTML = aiReply.replace(/\n/g, "<br/>");
    const stored = document.createElement("div");
    stored.className = "pdf-content unlocked";
    stored.style.backgroundImage = `url(${selectedCustomPaper || moodTextureMap[mood]})`;
    stored.style.backgroundSize = "cover";
    stored.style.backgroundRepeat = "no-repeat";
    stored.style.backgroundPosition = "top center";
    stored.style.fontFamily = `'${selectedFont}', serif`; // FONT APPLIED TO ARCHIVE
    stored.style.setProperty('color', selectedColor, 'important');
    stored.style.fontSize = selectedSize;
    stored.style.fontWeight = isBold ? "bold" : "normal";
    stored.style.fontStyle = isItalic ? "italic" : "normal";
    stored.style.textDecoration = isUnderline ? "underline" : "none";
    stored.innerHTML = `
      <h2 style="text-align:center;">Unsent Letter</h2>
      <p><strong>Mood:</strong> ${mood}</p>
      <p><strong>Your Letter:</strong><br/>${userHTML}</p>
      <p><strong>Reply:</strong><br/>${replyHTML}</p>
      <br/><br/>
      <p class="signature-line">— ${signatureInput?.value || "Yours, Lost in Silence"} ✍️</p>
`;
    const burnBtn = document.createElement("button");
    burnBtn.className = "export-btn";
    burnBtn.textContent = "Burn 🔥";
    burnBtn.addEventListener("click", () => {
      entry.classList.add("burned");
      setTimeout(() => { archiveList.removeChild(entry); }, 2000);
    });
    entry.appendChild(stored);
    entry.appendChild(burnBtn);
    entry.addEventListener("click", e => {
      if (!e.target.classList.contains("export-btn")) entry.classList.toggle("unlocked");
    });
    archiveList.prepend(entry);
    latestLetter = stored;
    downloadLatestBtn.style.display = "inline-block";
  }
  sendBtn.addEventListener("click", async () => {
  const letterText = letterTextarea.value.trim();
  const mood = moodSelect.value;
  const title = document.getElementById('letterTitle')?.value || '';
  const signature = signatureInput?.value || 'Yours, Lost in Silence';
  const avatar = document.getElementById("selectedAvatar")?.value || '';
  const openDate = (mood === "Time Capsule") ? document.getElementById("openDate")?.value : "";
  const isTimeCapsule = (mood === "Time Capsule") ? 1 : 0;

  if (!letterText) return alert("Write something first, love.");

  const { recipient, sender } = extractNames(letterText);

  bgMusic.muted = false;
  bgMusic.volume = 0.3;
  bgMusic.play().catch(() => {});
  flipSound.play().catch(() => {});
  setTimeout(() => crinkleSound.play().catch(() => {}), 400);

  response.classList.add("show");
  response.innerHTML = "";

  const quoteDiv = document.createElement("div");
  quoteDiv.className = "theme-quote";
  quoteDiv.textContent = "“We were a poem… unfinished.”";
  response.appendChild(quoteDiv);

  const replyWrapper = document.createElement("div");
  response.appendChild(replyWrapper);

  // ✅ If Time Capsule is set for future, skip AI and SAVE it still
  const today = new Date().toISOString().split("T")[0];
  if (mood === "Time Capsule" && openDate && openDate > today) {
    replyWrapper.innerHTML = "<em>This is a message to your future self. No reply generated.</em>";

    // ✅ Save to backend
    const body = `letter=${encodeURIComponent(letterText)}&reply=&title=${encodeURIComponent(title)}&mood=${encodeURIComponent(mood)}&avatar=${encodeURIComponent(avatar)}&openDate=${encodeURIComponent(openDate)}&isTimeCapsule=1`;
    fetch('/create-letter', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: body
    }).then(res => {
      if (res.status === 204) {
        console.log("✅ Time Capsule letter saved for future.");
      }
    });

    addToArchive(letterText, "", mood);
    return;
  }

  // ✅ Generate AI reply for non-future or non-Time Capsule letters
  try {
    let reply = await generateLetter(letterText, mood, recipient, sender);
    if (!reply || reply.trim().length < 10) {
      reply = "(The recipient chose not to reply.)";
    }
    typeReply(reply, replyWrapper);
    addToArchive(letterText, reply, mood);

    // ✅ Save to backend
    const body = `letter=${encodeURIComponent(letterText)}&reply=${encodeURIComponent(reply)}&title=${encodeURIComponent(title)}&mood=${encodeURIComponent(mood)}&avatar=${encodeURIComponent(avatar)}&openDate=${encodeURIComponent(openDate)}&isTimeCapsule=${isTimeCapsule}`;
    fetch('/create-letter', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: body
    });

    await speakReply(reply, recipient);
  } catch (err) {
    console.error("❌ AI Error:", err);
    const fallback = "(AI failed to reply. Try again later.)";
    replyWrapper.textContent = fallback;
    addToArchive(letterText, fallback, mood);

    // ✅ Still save the letter with fallback reply
    const body = `letter=${encodeURIComponent(letterText)}&reply=${encodeURIComponent(fallback)}&title=${encodeURIComponent(title)}&mood=${encodeURIComponent(mood)}&avatar=${encodeURIComponent(avatar)}&openDate=${encodeURIComponent(openDate)}&isTimeCapsule=${isTimeCapsule}`;
    fetch('/create-letter', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: body
    });
  }
});


  downloadLatestBtn.addEventListener("click", () => {
  if (!latestLetter) return;
  const mood = moodSelect.value;
  const wrapper = document.createElement("div");
  // 📏 Perfect size and layout control
  wrapper.style.maxWidth = "720px";
  wrapper.style.margin = "0 auto";
  wrapper.style.padding = "60px";
  wrapper.style.boxSizing = "border-box";
  wrapper.style.fontFamily = `'${selectedFont}', serif`;
  wrapper.style.setProperty('color', selectedColor, 'important');
  wrapper.style.fontSize = selectedSize;
  wrapper.style.fontWeight = isBold ? "bold" : "normal";
  wrapper.style.fontStyle = isItalic ? "italic" : "normal";
  wrapper.style.textDecoration = isUnderline ? "underline" : "none";
  wrapper.style.backgroundImage = `url(${selectedCustomPaper || moodTextureMap[mood]})`;
  // 🧠 Smarter background scaling
if (selectedCustomPaper || mood === "lost love") {
  wrapper.style.backgroundSize = "100% 100%"; // full cover
} else {
  wrapper.style.backgroundSize = "cover"; // natural stretch, maintains ratio
}


  wrapper.style.backgroundRepeat = "no-repeat";
  wrapper.style.backgroundPosition = "top center";
  wrapper.style.minHeight = "1400px"; // give more height for shorter images

wrapper.style.display = "flex";
wrapper.style.flexDirection = "column";
wrapper.style.justifyContent = "space-between";
wrapper.style.backgroundAttachment = "scroll";
wrapper.style.backgroundPosition = "center top";
wrapper.style.backgroundRepeat = "repeat-y"; // important


  // 📝 Content
  const userText = letterTextarea.value.trim().replace(/\n/g, "<br/>");
  const aiText = latestLetter.querySelector("p:nth-of-type(3)")?.innerHTML || "";
  wrapper.innerHTML = `
  <div>
    <h2 style="text-align:center; page-break-inside: avoid;">Unsent Letter</h2>
    <p><strong>Mood:</strong> ${mood}</p>
    <p><strong>Your Letter:</strong><br/><br/>${userText}</p>
     <p class="page-split"></p>
    <p><strong>Reply:</strong><br/><br/>${aiText}</p>
    <br/><br/>
    <p class="signature-line" style="text-align:right; page-break-inside: avoid;">— ${signatureInput?.value || "Yours, Lost in Silence"} ✍️</p>
  </div>
`;

  document.body.appendChild(wrapper);
  // 🧾 PDF Options — clean break, full content, no edge overflow
  const opt = {
    margin: 0,
    filename: `unsent-letter-${Date.now()}.pdf`,
    image: { type: "jpeg", quality: 0.98 },
    html2canvas: {
      scale: 2,
      useCORS: true,
      scrollY: 0,
      ignoreElements: el => el.classList.contains("export-btn")
    },
    jsPDF: {
      unit: "pt",
      format: "a4",
      orientation: "portrait"
    },
    pagebreak: {
  mode: ['css', 'legacy'],
  before: '.page-split', // forces clean break
  avoid: ['.signature-line', 'h2']
}

  };
  html2pdf().set(opt).from(wrapper).save().then(() => {
    document.body.removeChild(wrapper);
  });
});
  if ('webkitSpeechRecognition' in window) {
    const recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-IN';
    let isListening = false;
    recognition.onend = () => {
      if (isListening) recognition.start();
    };
    micBtn.addEventListener("click", () => {
      if (isListening) {
        recognition.stop();
        micBtn.textContent = "🎙️ Dictate Letter";
      } else {
        try {
          recognition.start();
          micBtn.textContent = "🛑 Stop Dictation";
        } catch (e) {
          console.error("Error starting recognition:", e);
        }
      }
      isListening = !isListening;
    });
    recognition.onresult = function (event) {
      let interim = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) letterTextarea.value += event.results[i][0].transcript + ' ';
        else interim += event.results[i][0].transcript;
      }
    };
    recognition.onerror = function (event) {
      console.error("Speech recognition error:", event.error);
      micBtn.textContent = "🎙️ Dictate Letter";
      isListening = false;
      if (["not-allowed", "service-not-allowed"].includes(event.error)) {
        alert("Microphone access was blocked. Please allow it in your browser settings.");
      }
    };
  } else {
    micBtn.disabled = true;
    micBtn.textContent = "🎙️ Not Supported";
  }
  function toggleProfileDropdown() {
  const dropdown = document.getElementById('profile-dropdown');
  dropdown.classList.toggle('hidden');

  // Fetch email when dropdown is shown
  if (!dropdown.classList.contains('hidden')) {
    fetch('/get-user')
      .then(res => res.json())
      .then(data => {
        document.getElementById('user-email').textContent = data.email || 'Unknown';
      })
      .catch(() => {
        document.getElementById('user-email').textContent = 'Error fetching email';
      });
  }
}

};