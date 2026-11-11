# REGAM Live

One host goes live (camera, screen share, a guest on stage); everyone else watches and comments.

## How it works

```
studio page (Chrome) ──WebRTC──▶ MediaMTX "studio" ──ffmpeg (H.264/AAC)──▶ "air" ──HLS──▶ viewers
        ▲    └─ host voice ───▶ MediaMTX "backstage" ──WebRTC──▶ guest
        └────────── WebRTC ◀── MediaMTX "guest" ◀──WebRTC── guest (phone or computer)

viewers / studio ◀──WebSocket──▶ app (Node.js): comments, moderation, stage requests
```

- `server.js` — pages, chat over WebSocket, studio login, stage requests, and the
  authenticated proxies to MediaMTX (`/api/rtc/...` for WebRTC, `/hls/...` for the audience).
- `public/studio.*` + `compositor.worker.js` — the studio. Camera, screen and guest are mixed
  into one picture in a worker, so the broadcast keeps running while the tab is in the background.
- `public/index.html`, `watch.js` — the viewer page (HLS player, comments, "request to go on stage").
- `deploy/mediamtx.yml.tpl` — media server configuration.

## Install on a VPS

```bash
unzip regam-live.zip && cd regam-live
bash install.sh live.example.com you@example.com
```

Open in the hosting firewall: `80/tcp`, `443/tcp`, `8189/udp`, `8189/tcp`.

## Limits of this version

- The audience stream leaves from the VPS itself. For thousands of viewers put a CDN in front
  of `https://<domain>/hls` and set `HLS_PUBLIC_URL` in `.env`.
- The audience sees the live with a delay of several seconds (HLS). The guest on stage is in real time.
- One guest on stage at a time. Viewers have no accounts: a ban applies to the browser, not the person.
- Comments are kept in memory (last 150); they are lost when the app restarts.
- The studio needs Chrome or Edge on a computer.

## Test

`npm test` runs the whole flow with headless browsers (needs Playwright and ffmpeg). The media
server is replaced by a stand-in, so the MediaMTX configuration itself is not covered by it.
