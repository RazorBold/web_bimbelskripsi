# Implementation Plan
**Project**: SkripsiEngineer - Bimbingan Skripsi Teknik & Teknologi

Follow this step-by-step plan to implement the platform.

---

## Phase 1: Environment & Database Setup
- [ ] Initialize Python environment and check for requirements (Flask, Flask-Bcrypt, etc.).
- [ ] Create `db.py` to handle SQLite3 setup, connection pool, and table structures.
  - Create table `users`.
  - Create table `requests`.
- [ ] Test database queries and connectivity inside local Python shell.

## Phase 2: Flask App & Backend API
- [ ] Implement `app.py` skeleton with imports and config.
- [ ] Implement user authentication endpoints:
  - `/api/register`
  - `/api/login`
  - `/api/logout`
- [ ] Implement request management endpoints:
  - `POST /api/requests`
  - `GET /api/requests`
- [ ] Set up basic session management using Flask session.

## Phase 3: Base Layout & Common Styles
- [ ] Create `templates/base.html` containing:
  - Header/Navigation bar (responsive, glassmorphism design).
  - Main contents injection block (`{% block content %}`).
  - Footer with social links, contacts, and navigation.
  - Imports for Google Fonts (Outfit, Inter), GSAP, and Three.js.
- [ ] Create `static/css/style.css` with core utility classes, layout variables, and basic transitions.

## Phase 4: Landing Page & Custom Form
- [ ] Create `templates/index.html` structure:
  - **Hero Section**: Container for Three.js canvas, bold typography, search-like field selector, and live status numbers.
  - **Pilihan Bidang Section**: Cards detailing Electrical, IoT, MATLAB, AI, Web Dev packages.
  - **Fitur Unggulan**: Key selling points.
  - **Cara Kerja**: Roadmap steps.
  - **Paket & Harga**: Side-by-side product cards with highlight features.
  - **Custom Class Form**: Input fields to send custom requests directly (registers interest or inserts request if logged in).
  - **Testimonials Section**: Carousel of client comments.
- [ ] Implement smooth CSS layouts and scroll animations.

## Phase 5: Authentication Pages & Dashboard
- [ ] Design Auth flow (Integrated Login & Register forms or modal overlays inside landing page).
- [ ] Create `templates/dashboard.html` for client center:
  - Welcome banner with user profile stats.
  - Service descriptions: detailed look at what bimbingan options look like.
  - "My Bimbingan Requests" list displaying status indicators (Pending, Approved, Ongoing, Completed) with progress bars.
  - Form to submit new requests.
- [ ] Setup JS handlers in `static/js/main.js` to process login/registration/logout AJAX calls dynamically without page reloads.

## Phase 6: 3D Elements & Animations
- [ ] Create `static/js/three-canvas.js` for the hero section:
  - Set up Three.js Scene, Camera, and WebGLRenderer inside the `#three-container`.
  - Build a responsive particle constellation or digital globe mesh.
  - Add gentle mouse interaction (particles slightly hover towards or warp away from cursor).
- [ ] Configure `static/js/main.js` GSAP animations:
  - ScrollTrigger animations to slide/fade sections into view smoothly.
  - Interactive hover actions (card tilt, glow shadows, buttons pulse).

## Phase 7: Verification & Polishing
- [ ] Run backend unit tests or manually test register -> login -> request flow.
- [ ] Audit user experience for visual bugs, alignment issues, and loading speeds.
- [ ] Optimize Three.js canvas render loop to run efficiently without lagging the page.
- [ ] Finalize responsive UI/UX for mobile views.
