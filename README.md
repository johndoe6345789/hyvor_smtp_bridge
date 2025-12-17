# Hyvor Relay SMTP → HTTP Bridge (Python)

This project runs a small SMTP server that accepts inbound SMTP messages and
forwards them to Hyvor Relay using the Console API endpoint:

`POST /api/console/sends`

## Why this exists

Some applications can only send email via SMTP. Hyvor Relay exposes a clean HTTP
API. This bridge lets those apps keep using SMTP while Hyvor Relay handles
queueing, DKIM, deliverability controls, etc.

Reference: Hyvor Relay docs for sending emails via API:
- Endpoint: `POST /api/console/sends`
- Auth: `Authorization: Bearer <api-key>`
(See Hyvor Relay docs.)

## Quick start

1) Create a Hyvor Relay API key with scope `sends.send`.

2) Install dependencies:

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3) Configure environment variables:

- `HYVOR_BASE_URL` (default: https://hyvor.wardcrew.com)
- `HYVOR_API_KEY` (required)
- `SMTP_LISTEN_HOST` (default: 0.0.0.0)
- `SMTP_LISTEN_PORT` (default: 2525)
- `SMTP_REQUIRE_TLS` (default: 0)  # bridge accepts plain SMTP by default
- `LOG_LEVEL` (default: INFO)

4) Run:

```bash
python -m smtp_bridge.main
```

## Notes

- This server is intended to sit *behind* a reverse proxy / private network.
- By default it listens on port 2525 (non-privileged). Use a port-forward or
  proxy if you need port 25/587.
- The bridge extracts:
  - From: SMTP envelope sender
  - To: SMTP envelope recipients
  - Subject: parsed from the email
  - body_text/body_html: from multipart
  - attachments: any non-body parts are sent as attachments (base64)

## Testing

```bash
python -m unittest -v
```

## License

MIT
