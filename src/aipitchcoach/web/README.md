## Gradio audio chat client

Run the browser client with:

```shell
uv run --package web aipitchcoach-web
```

The client opens a persistent WebSocket and streams microphone PCM frames while
the conversation is active. Set `AIPITCHCOACH_AUDIO_WEBSOCKET` to change the
default endpoint, or edit the URL in the UI.

Each binary message uses the same wire format as
`common.audio_protocol.pack_audio`; the receiving service can decode each
message with `common.audio_protocol.unpack_audio`. Text WebSocket messages are
shown as coach responses in the chat panel.