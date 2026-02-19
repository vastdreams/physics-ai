# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.x     | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, **please do not open a public issue**.

Instead, email **admin@beyondfrontier.local** with:

1. A description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if any)

We will acknowledge receipt within 48 hours and aim to release a patch within 7 days for critical issues.

## Security Measures

This project implements multiple layers of defense:

### Authentication & Authorization
- JWT-based authentication with secure random secrets
- Account lockout after repeated failed login attempts
- Password strength enforcement (minimum 8 chars, uppercase, number)
- Disposable email domain blocking on registration
- Registration rate limiting per IP
- Role-based access control (user, researcher, admin)

### Input Validation & Sanitization
- HTML tag stripping on all user-supplied text
- SQL/XSS/command injection pattern detection
- Request body size limits (configurable, default 10 MB)
- Null byte removal from inputs
- Path traversal blocking

### HTTP Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (HSTS)
- `Content-Security-Policy`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy` (camera, microphone, geolocation, payment, usb disabled)
- `X-Permitted-Cross-Domain-Policies: none`
- `Cross-Origin-Opener-Policy: same-origin`
- `Cross-Origin-Resource-Policy: same-origin`
- Server header removed

### Rate Limiting & Abuse Prevention
- Global rate limiting (configurable per-window)
- Authentication endpoint rate limiting
- Per-account daily/monthly API usage quotas
- Automatic IP blocking after suspicious activity threshold

### Production Hardening
- Debug mode auto-disabled when `FLASK_ENV=production`
- CORS restricted to configured origins (no wildcard default)
- Prometheus `/metrics` endpoint protectable via bearer token
- Sensitive data files (users.json, usage.json) excluded from git
- No hardcoded secrets — all credentials loaded from environment variables
