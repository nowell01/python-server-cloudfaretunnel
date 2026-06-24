# Dahab Server

A lightweight static-file web server written from scratch in Python using raw
sockets — no frameworks, no `http.server`. It serves the static site contained
in the `dahab/` folder (a restaurant/menu site with HTML, CSS, JS and images).

## Features

- **Raw socket HTTP/1.1 server** — handcrafted request parsing and responses.
- **Multi-threaded** — each connection is handled on its own thread, so one slow
  client doesn't block others.
- **Concurrency cap** — a bounded semaphore limits the number of simultaneous
  connections (`MAX_CONNECTIONS`, default 100).
- **Per-connection timeout** — slow/idle clients are dropped after 10 seconds.
- **Correct content types** — MIME types are detected per file (`mimetypes`), so
  CSS, JS and images are served correctly, not as `text/html`.
- **Path-traversal protection** — requests are resolved and validated to stay
  inside the `dahab/` directory, blocking attacks like `/../secret.txt`.
- **Clean shutdown** — `Ctrl+C` stops the server and closes the socket.

## Project structure

```
dahab_server/
├── main.py        # the server
└── dahab/         # static site served by the server
    ├── index.html
    ├── menu.html
    ├── css/
    ├── js/
    └── *.jpg / *.png ...
```

## Requirements

- Python 3.x (standard library only — no external dependencies)

## Usage

From the project folder:

```bash
python main.py
```

You should see:

```
Serving on http://127.0.0.1:2000/ (Ctrl+C to stop)
```

Then open <http://127.0.0.1:2000/> in your browser.

## Configuration

Settings live at the top of `main.py`:

| Setting           | Default       | Description                                  |
| ----------------- | ------------- | -------------------------------------------- |
| `ROOT`            | `dahab`       | Folder whose files are served.               |
| `HOST`            | `127.0.0.1`   | Interface to bind. Use `0.0.0.0` to expose.  |
| `PORT`            | `2000`        | Port to listen on.                           |
| `MAX_CONNECTIONS` | `100`         | Max simultaneous client connections.         |

## Making it accessible online

The server binds to `127.0.0.1` (local only). To share it publicly without
opening your network, run it behind a [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/):

```bash
cloudflared tunnel --url http://127.0.0.1:2000
```

This prints a public HTTPS URL that stays live while both the server and the
tunnel are running.

## Notes

This is a learning/hobby project. While it includes basic hardening (threading,
connection caps, timeouts, path-traversal checks), it is not intended as a
production-grade web server.
