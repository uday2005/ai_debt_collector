(() => {
  const wsUrl = (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws';
  let ws;
  let selectedPersonality = '';
  const logEl = document.getElementById('log');
  const analysisEl = document.getElementById('analysis');
  const userInput = document.getElementById('userInput');
  const recordBtn = document.getElementById('recordBtn');

  let mediaRecorder = null;
  let recordedChunks = [];

  function appendLog(text) {
    logEl.textContent += text + '\n';
    logEl.scrollTop = logEl.scrollHeight;
  }

  function playBase64Audio(b64, mime) {
    if (!b64) return;
    const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
    const blob = new Blob([bytes.buffer], {type: mime || 'audio/wav'});
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    audio.play();
    audio.onended = () => URL.revokeObjectURL(url);
  }

  // wire personality buttons
  document.querySelectorAll('.personalities button').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.personalities button').forEach(b=>b.disabled=false);
      btn.disabled = true;
      selectedPersonality = btn.getAttribute('data-perso');
    });
  });

  document.getElementById('start').addEventListener('click', () => {
    if (!selectedPersonality) {
      alert('Please choose a personality first');
      return;
    }
    ws = new WebSocket(wsUrl);
    ws.onopen = () => {
      appendLog('[SYSTEM] Connected. Starting simulation...');
      ws.send(JSON.stringify({type: 'start', personality: selectedPersonality}));
    };

    ws.onmessage = (evt) => {
      let msg = {};
      try { msg = JSON.parse(evt.data); } catch(e){ console.error(e); return; }
      if (msg.type === 'tts') {
        appendLog('Borrower: ' + (msg.text||'') );
        // If server provided audio bytes, play them. Otherwise use SpeechSynthesis.
        if (msg.audio_b64) {
          playBase64Audio(msg.audio_b64, msg.audio_mime || 'audio/wav');
        } else if (msg.text) {
          const utter = new SpeechSynthesisUtterance(msg.text);
          window.speechSynthesis.cancel();
          window.speechSynthesis.speak(utter);
        }
      } else if (msg.type === 'final') {
        analysisEl.innerHTML = '<h4>Compliance</h4><pre>' + msg.compliance + '</pre><h4>Feedback</h4><pre>' + msg.feedback + '</pre>';
        appendLog('[SYSTEM] Simulation finished.');
        ws.close();
      } else if (msg.type === 'error') {
        appendLog('[ERROR] ' + msg.message);
      }
    };

    ws.onclose = () => appendLog('[SYSTEM] Connection closed');
    ws.onerror = (e) => appendLog('[SYSTEM] WebSocket error');
  });

  document.getElementById('stop').addEventListener('click', () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({type: 'stop'}));
    }
  });

  // send text-based reply
  document.getElementById('send').addEventListener('click', () => {
    const text = userInput.value.trim();
    if (!text) return;
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      alert('Not connected');
      return;
    }
    appendLog('You: ' + text);
    ws.send(JSON.stringify({type: 'user_utterance', text}));
    userInput.value = '';
  });

  // Recording flow
  recordBtn.addEventListener('click', async () => {
    if (!mediaRecorder) {
      // start recording
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        recordedChunks = [];
        mediaRecorder.ondataavailable = (e) => { if (e.data && e.data.size) recordedChunks.push(e.data); };
        mediaRecorder.onstop = async () => {
          const blob = new Blob(recordedChunks, { type: mediaRecorder.mimeType || 'audio/webm' });
          const arrayBuffer = await blob.arrayBuffer();
          const bytes = new Uint8Array(arrayBuffer);
          // convert to base64
          let binary = '';
          for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
          const b64 = btoa(binary);
          appendLog('You (audio reply sent)');
          if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'audio_blob', audio_b64: b64, mime: blob.type }));
          } else {
            appendLog('[SYSTEM] Not connected to server');
          }
          // reset
          mediaRecorder = null;
          recordBtn.textContent = 'Record Reply';
        };
        mediaRecorder.start();
        recordBtn.textContent = 'Stop Recording';
      } catch (e) {
        console.error('Microphone access denied or error', e);
        alert('Microphone access is required to record audio replies.');
      }
    } else {
      // stop recording
      mediaRecorder.stop();
    }
  });

})();
