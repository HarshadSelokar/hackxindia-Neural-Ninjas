let audioContext;
let processor;
let source;
let ws;

const startBtn = document.getElementById("start");
const stopBtn = document.getElementById("stop");
const output = document.getElementById("output");

startBtn.onclick = startRecording;
stopBtn.onclick = stopRecording;

async function startRecording() {
  ws = new WebSocket(`ws://${window.location.host}/stt`);
  ws.binaryType = "arraybuffer";

  ws.onmessage = (event) => {
    if (event.data.trim()) {
      output.textContent = event.data + "\n";
    }
  };

  ws.onopen = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    audioContext = new AudioContext({ sampleRate: 16000 });
    source = audioContext.createMediaStreamSource(stream);

    processor = audioContext.createScriptProcessor(4096, 1, 1);

    source.connect(processor);
    processor.connect(audioContext.destination);

    processor.onaudioprocess = (e) => {
      const input = e.inputBuffer.getChannelData(0);
      const pcm16 = new Int16Array(input.length);

      for (let i = 0; i < input.length; i++) {
        pcm16[i] = Math.max(-1, Math.min(1, input[i])) * 32767;
      }

      if (ws.readyState === WebSocket.OPEN) {
        ws.send(pcm16.buffer);
      }
    };

    startBtn.disabled = true;
    stopBtn.disabled = false;
  };
}

function stopRecording() {
  processor.disconnect();
  source.disconnect();
  audioContext.close();
  ws.close();

  startBtn.disabled = false;
  stopBtn.disabled = true;
}
