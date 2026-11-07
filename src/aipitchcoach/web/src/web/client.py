"""Streaming browser audio chat client for the AIPitchCoach audio protocol."""

from __future__ import annotations

import os

import gradio as gr


DEFAULT_ENDPOINT = os.getenv(
    "AIPITCHCOACH_AUDIO_WEBSOCKET",
    "ws://127.0.0.1:8000/audio",
)

CLIENT_JS = r"""
() => {
  let socket;
  let context;
  let processor;
  let source;
  let stream;
  let running = false;

  const status = (text, error = false) => {
    const element = document.querySelector("#audio-status");
    if (element) {
      element.textContent = text;
      element.style.color = error ? "#b91c1c" : "";
    }
  };

  const appendMessage = (text, role = "assistant") => {
    const chat = document.querySelector("#audio-chat");
    if (!chat) return;
    const line = document.createElement("div");
    line.className = `audio-message ${role}`;
    line.textContent = `${role === "user" ? "You" : "Coach"}: ${text}`;
    chat.appendChild(line);
    chat.scrollTop = chat.scrollHeight;
  };

  const packet = (samples, sampleRate) => {
    const result = new ArrayBuffer(6 + samples.length * 4);
    const view = new DataView(result);
    view.setUint32(0, sampleRate, false);
    view.setUint8(4, 1);
    view.setUint8(5, 0);
    for (let index = 0; index < samples.length; index += 1) {
      view.setFloat32(6 + index * 4, samples[index], true);
    }
    return result;
  };

  const stop = () => {
    running = false;
    if (processor) processor.disconnect();
    if (source) source.disconnect();
    if (context) context.close();
    if (stream) stream.getTracks().forEach((track) => track.stop());
    if (socket && socket.readyState === WebSocket.OPEN) socket.close();
    processor = source = stream = context = socket = undefined;
    status("Disconnected");
  };

  const start = async () => {
    if (running) return;
    const endpoint = document.querySelector("#audio-endpoint").value.trim();
    if (!endpoint) {
      status("Enter a WebSocket endpoint.", true);
      return;
    }
    try {
      stream = await navigator.mediaDevices.getUserMedia({audio: true});
      context = new AudioContext({sampleRate: 16000});
      socket = new WebSocket(endpoint);
      socket.binaryType = "arraybuffer";
      socket.onopen = () => {
        running = true;
        status("Streaming");
        appendMessage("Listening...", "user");
        source = context.createMediaStreamSource(stream);
        processor = context.createScriptProcessor(4096, 1, 1);
        processor.onaudioprocess = (event) => {
          if (running && socket.readyState === WebSocket.OPEN) {
            socket.send(packet(event.inputBuffer.getChannelData(0), context.sampleRate));
          }
        };
        source.connect(processor);
        processor.connect(context.destination);
      };
      socket.onmessage = (event) => {
        if (typeof event.data === "string") appendMessage(event.data);
      };
      socket.onerror = () => status("WebSocket connection failed.", true);
      socket.onclose = () => { if (running) stop(); };
    } catch (error) {
      stop();
      status(error.message || "Could not start microphone streaming.", true);
    }
  };

  document.querySelector("#audio-start").onclick = start;
  document.querySelector("#audio-stop").onclick = stop;
}
"""


def create_app() -> gr.Blocks:
    """Build the browser audio chat UI."""
    with gr.Blocks(title="AI Pitch Coach") as app:
        gr.Markdown("# AI Pitch Coach\nSpeak naturally with your pitch coach.")
        gr.Textbox(
            DEFAULT_ENDPOINT,
            label="Audio WebSocket endpoint",
            elem_id="audio-endpoint",
        )
        gr.HTML(
            """
            <div id="audio-chat" style="height: 220px; overflow-y: auto; margin: 1rem 0"></div>
            <p id="audio-status">Disconnected</p>
            <button id="audio-start">Start conversation</button>
            <button id="audio-stop">Stop</button>
            """
        )
    return app


def main() -> None:
    """Launch the Gradio client."""
    create_app().launch(js=CLIENT_JS)


if __name__ == "__main__":
    main()
