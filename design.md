# Product Requirement Document (PRD) & System Design
**Project**: SkripsiEngineer - Bimbingan Skripsi Teknik & Teknologi

---

## 1. Product Requirements Document (PRD)

### 1.1 Product Overview
**SkripsiEngineer** is a premium online tutoring and engineering service platform designed specifically for engineering students (Electrical, IoT, MATLAB, Software Dev, AI/ML, Embedded Systems, etc.). The platform connects clients with expert mentors to guide them through final projects, thesis writing, simulation, and software coding.

### 1.2 Target Audience
- Final year engineering students looking for tutoring, code review, debugging, or simulation support.
- Students who need guidance in setting up hardware (IoT, Embedded) or theoretical modeling (MATLAB, Machine Learning).

### 1.3 Key Features
1. **Premium Landing Page**:
   - Modern, high-end design matching the dark/neon blue glassmorphic aesthetic.
   - Interactive 3D element (Three.js) in the hero section.
   - Smooth entrance and scroll-motion animations (GSAP).
   - Display of bimbingan fields, pricing packages, how it works, and student testimonials.
   - Interactive custom class/guidance booking form.
2. **User Authentication**:
   - Registration (name, email, password, phone, major).
   - Login (session-based authentication).
3. **User Dashboard / Service Catalog**:
   - Visual catalog of specific service descriptions (Jokian/Bimbingan details: Web Development, IoT Hardware, AI/ML models, MATLAB scripts, etc.).
   - List of student's submitted bimbingan requests with progress trackers (Pending, Approved, Ongoing, Completed).
   - Order history and details of assigned mentors.
4. **Service Request Portal**:
   - Form to submit requests (select field, select package, describe custom requirements, upload reference documents/syllabus).

---

## 2. System Architecture & Tech Stack

### 2.1 Tech Stack
- **Frontend**: HTML5, Vanilla CSS3 (Custom Variables, Flexbox/Grid, Backdrop-filters for Glassmorphism), Modern JavaScript (ES6+), GSAP (GreenSock Animation Platform) + ScrollTrigger, Three.js (for the hero 3D particle canvas).
- **Backend**: Python Flask framework.
- **Database**: SQLite3.
- **Libraries & CDNs**:
  - Fonts: Google Fonts (Outfit & Inter).
  - Icons: Lucide Icons or FontAwesome via CDN.
  - Three.js: `three.min.js` via CDN.
  - GSAP: `gsap.min.js` and `ScrollTrigger.min.js` via CDN.

### 2.2 Directory Structure
```text
bimbel_skripsi_web/
│
├── app.py                 # Core Flask Application & API Routes
├── db.py                  # Database connection, schemas, and helper functions
├── design.md              # Product Requirement Document (PRD) & System Design
├── plan.md                # Phase-by-phase implementation checklist
├── database.db            # SQLite Database (generated on launch)
│
├── static/
│   ├── css/
│   │   └── style.css      # Core Stylesheet (Dark mode, glassmorphism, responsive)
│   └── js/
│       ├── main.js        # GSAP animations, form validation, API integrations
│       └── three-canvas.js# Three.js 3D canvas animation script
│
└── templates/
    ├── base.html          # Shared navbar, footer, scripts, layout structure
    ├── index.html         # Landing page template
    ├── login.html         # Register/Login templates (or integrated modal)
    └── dashboard.html     # User Dashboard & Service catalog page
```

---

## 3. Database Schema (SQLite)

We will define three main tables: `users`, `requests`, and `fields`.

### 3.1 `users` Table
Stores user registration and authentication data.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| `username` | TEXT | UNIQUE, NOT NULL | User login handle |
| `email` | TEXT | UNIQUE, NOT NULL | User email address |
| `password_hash`| TEXT | NOT NULL | Hashed password |
| `phone` | TEXT | NOT NULL | Contact number |
| `major` | TEXT | NOT NULL | Academic major |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Date of registration |

### 3.2 `requests` Table
Tracks student requests for tutoring/project assistance.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Request ID |
| `user_id` | INTEGER | FOREIGN KEY (`users.id`) | Submitting user |
| `field` | TEXT | NOT NULL | Field (e.g. IoT, MATLAB, AI, etc.) |
| `package` | TEXT | NOT NULL | Package (Basic, Pro, Premium, Custom) |
| `description` | TEXT | NOT NULL | Client's project description or thesis topic |
| `status` | TEXT | DEFAULT 'Pending' | 'Pending', 'Approved', 'Ongoing', 'Completed' |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Submission timestamp |

---

## 4. API Endpoints

### 4.1 Authentication
- **`POST /api/register`**
  - Payload: `{ username, email, password, phone, major }`
  - Response: `{ status: "success", message: "User registered" }` or `{ status: "error", message: "Email already exists" }`
- **`POST /api/login`**
  - Payload: `{ email, password }`
  - Response: `{ status: "success", redirect: "/dashboard" }`
- **`POST /api/logout`**
  - Response: `{ status: "success", redirect: "/" }`

### 4.2 Class Requests
- **`POST /api/requests`** (Requires Auth)
  - Payload: `{ field, package, description }`
  - Response: `{ status: "success", request_id: X }`
- **`GET /api/requests`** (Requires Auth)
  - Response: `[{ id, field, package, description, status, created_at }, ...]`

---

## 5. UI/UX Specification

### 5.1 Colors
- **Background**: Deep Indigo/Blue Black (`#0a0f1d`)
- **Card Background**: Glassmorphism translucent dark blue (`rgba(16, 22, 41, 0.6)`) with `backdrop-filter: blur(12px)`
- **Border**: Thin translucent indigo border (`rgba(255, 255, 255, 0.08)`)
- **Accent 1**: Electric Cyan (`#00f0ff`)
- **Accent 2**: Royal Blue (`#2563eb`)
- **Text Primary**: White/Off-white (`#f8fafc`)
- **Text Secondary**: Soft blue-gray (`#94a3b8`)

### 5.2 Animations
- **Three.js Canvas**: Background simulation of connected constellation lines with floating neon blue nodes. Moves slowly, speeds up slightly on scroll, reacts to mouse hover.
- **GSAP ScrollTrigger**:
  - Fade-in-up on sections as they scroll into view.
  - Hover zoom and micro-glow animation on bidangs (tutoring fields) and pricing cards.
  - Custom tabs sliding transition.
