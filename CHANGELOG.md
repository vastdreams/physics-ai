# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2026-02-14

### Added
- **Sign Up page**: Full user registration — no API keys, no credit card. Just name, email, and password
- **Password strength meter**: Real-time visual indicator with 5-point scale (Weak/Fair/Good/Strong)
- **Password rules display**: Live check marks for 8+ chars, uppercase, number, special character
- **What's New dashboard card**: Automatically shows latest release notes and git commits
- **Changelog API** (`/api/v1/changelog`): Parses CHANGELOG.md, fetches git commits, and generates AI summaries via DeepSeek
- **DeepSeek integration for release notes**: Auto-generates user-friendly release notes from git commit history
- **Version manifest system**: Proper build hashing with git SHA for reliable update detection
- **Security headers middleware**: X-Content-Type-Options, X-Frame-Options, HSTS, CSP, Permissions-Policy
- **Injection detection**: SQL injection, XSS, and command injection patterns blocked in request bodies
- **Scanner/bot auto-blocking**: IPs probing for .env, wp-admin, phpinfo, path traversal get auto-blocked
- **IP auto-ban**: 50+ bad requests in 5 minutes triggers a 30-minute block

### Changed
- **Landing page CTAs**: Changed from "Launch App" to "Get Started Free" linking to signup
- **Login page**: Added "Don't have an account? Sign up free" link, removed default credential hints
- **Update banner**: Redesigned light-themed with expandable release notes and proper cache-busting refresh
- **Version bumped to 2.0.0**: Reflects the major authentication and security overhaul

### Security
- **Account lockout**: 5 failed login attempts locks the account for 15 minutes (per IP and per email)
- **Rate limiting on auth**: Login and register endpoints rate-limited to 10 requests/minute per IP
- **Password strength enforcement**: Requires 8+ chars, uppercase, number; blocks common passwords like "password" and "admin123"
- **Email validation**: Strict RFC-compliant regex with 254-char limit
- **Input sanitization**: HTML tag stripping, null byte removal, length limits on all text inputs
- **Proxy-aware IP detection**: Uses X-Forwarded-For for real client IP behind Nginx
- **Request size limits**: 10MB max body size (configurable via MAX_REQUEST_SIZE_MB)

### Fixed
- **Auto-update banner always showing**: Build hash was generated independently in `define` and `version.json` causing permanent mismatch
- **Version showing 0.0.0**: package.json had placeholder version; now properly set and used
- **Refresh button not working**: Added service worker unregistration and cache-busting URL reload

## [1.1.0] - 2026-02-13

### Added
- **Landing page**: Premium light-themed design with animated mesh gradients, floating orbs, 3D hover effects
- **Login page**: Beautiful split-layout with animated gradient background
- **Authentication system**: JWT-based auth with AuthContext, ProtectedRoute, token refresh
- **Light theme overhaul**: Complete CSS rewrite — radiant white palette, glassmorphism, scroll animations
- **Prometheus metrics endpoint**: `/metrics` for monitoring
- **Redis cache configuration**: REDIS_URL environment variable support
- **LLM circuit breaker**: Configurable threshold and cooldown via environment variables

### Changed
- **All UI components**: Migrated from dark to light theme with gradient accents
- **Dashboard**: Mesh gradient welcome banner, animated stat cards, hover glow effects
- **Sidebar**: Light glass background, gradient active indicators, user info display
- **Header**: White glass with backdrop blur, gradient status indicators

## [1.0.0] - 2026-02-02

### Added
- **Neurosymbolic Engine**: Full implementation with neural and symbolic components
  - Embedding-based pattern matching
  - Rule-based symbolic inference
  - Configurable hybrid integration
- **Four Reasoning Types**: Complete reasoning engine
  - Deductive reasoning (modus ponens, syllogisms)
  - Inductive reasoning (pattern generalization)
  - Abductive reasoning (hypothesis generation)
  - Analogical reasoning (structure mapping)
- **Rule Engine**: Pattern matching with conflict resolution
  - Operators: `$gt`, `$lt`, `$in`, `$and`, `$or`, etc.
  - Variable binding with `$var` syntax
  - Priority, specificity, and recency-based resolution
- **Equation Solver**: SymPy-based symbolic mathematics
  - Symbolic equation solving
  - Numerical fallback with scipy
  - Differentiation and integration
  - Physical constants database
- **Physics Models**: Simulation with conservation validation
  - Harmonic oscillator
  - Pendulum (small and large angle)
  - Two-body gravitational systems
  - Projectile motion with drag
  - RK4 and adaptive integration methods
- **AST-based Code Validator**: Security improvements
  - Dangerous pattern detection
  - Complexity analysis
  - Safe code generation validation
- **Knowledge Synthesis**: Entity extraction and conflict resolution
- **REST API**: 41 endpoints across 11 categories
- **Comprehensive Tests**: Test coverage for all major modules

### Changed
- Moved from placeholder implementations to full functionality
- Reorganized documentation structure
- Updated README as project landing page

### Security
- Removed hardcoded SECRET_KEY (now uses environment variable)
- AST-based validation prevents code injection bypasses

### Documentation
- New comprehensive README with vision and quick start
- API Reference documentation
- Organized docs/ folder structure

## [0.1.0] - 2024-12-05

### Added
- Initial project structure
- Core neurosymbolic engine (placeholder)
- Rule-based system framework
- Self-evolution module structure
- Physics integration module
- Validation framework
- Logging system
- Test suite skeleton
- CI/CD pipelines
- Basic documentation
