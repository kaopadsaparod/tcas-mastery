# TCAS Mastery Prep System 🎯
> **Local-First Pedagogical Examination Engine & Diagnostic System for TCAS (TGAT1, TGAT3, TPAT3, A-Level Physics & Math)**  
> *เอกสารข้อมูลระบบฉบับสมบูรณ์สำหรับนักพัฒนาและโมเดลปัญญาประดิษฐ์ (Comprehensive System Architecture & AI Pair-Programming Specification)*

[![Tests](https://img.shields.io/badge/pytest-150%2F150%20passed%20(100%25)-success?style=flat-square&logo=pytest)](file:///C:/Users/pqx12/Desktop/tcas/TEST_READY.md)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-WAL%20Mode-003B57?style=flat-square&logo=sqlite)](https://www.sqlite.org/)
[![Status](https://img.shields.io/badge/catalog-327%20Questions%20%7C%206%20Blueprints-orange?style=flat-square)](#4-content-catalog--blueprint-inventory)
[![Offline](https://img.shields.io/badge/runtime-100%25%20Offline%20First-green?style=flat-square)](#1-executive-overview--core-philosophy)

---

## 📑 สารบัญ (Table of Contents)
1. [ภาพรวมและปรัชญาของระบบ (Executive Overview & Philosophy)](#1-executive-overview--core-philosophy)
2. [สถาปัตยกรรมและเทคโนโลยีที่ใช้ (Architecture & Tech Stack)](#2-architecture--technology-stack)
3. [โครงสร้างไดเรกทอรีและไฟล์ทั้งหมด (Project Structure & File Map)](#3-project-structure--file-map)
4. [คลังเนื้อหาและโครงสร้างข้อสอบ (Content Catalog & Blueprints)](#4-content-catalog--blueprint-inventory)
5. [โครงสร้างข้อมูลและ Pydantic Schemas (Data Models & YAML Specifications)](#5-data-models--yaml-schemas)
6. [ระบบตรวจคำตอบและการวินิจฉัย (Deterministic Grading & Error Tags)](#6-deterministic-grading--pedagogical-diagnosis)
7. [ระบบทบทวนแบบเว้นระยะและความมั่นใจ (Spaced Repetition & Calibration)](#7-spaced-repetition-honest-mastery--calibration)
8. [ระบบจำลองการสอบจริง (Mock Exam Engine & Blueprint Rules)](#8-mock-exam-engine--blueprint-rules)
9. [แบบฝึกคิดเลขและคลังสูตร (Procedural Math & Formula Recall)](#9-procedural-drills--formula-studio)
10. [ความปลอดภัย ฐานข้อมูล และ Dark Mode (Security, DB & UX)](#10-security-database--dark-mode)
11. [เอกสาร API Endpoints ครบทุกเส้น (Complete API Reference)](#11-complete-api-reference)
12. [การทดสอบระบบและคุณภาพข้อสอบ (Testing & Quality Verification)](#12-testing--verification-pyramid)
13. [คู่มือสำหรับนักพัฒนาและ AI Agent (Developer & AI Agent Manual)](#13-developer--ai-agent-pair-programming-manual)

---

## 1. Executive Overview & Core Philosophy

**TCAS Mastery** ถูกสร้างขึ้นเพื่อแก้ปัญหาพื้นฐานของการเตรียมสอบเข้ามหาวิทยาลัย (TCAS: TGAT, TPAT, A-Level):
> *"การทำข้อสอบได้เยอะ ไม่ได้แปลว่าเก่งขึ้น ถ้าไม่รู้ว่าจุดอ่อนที่แท้จริงคืออะไร และข้อสอบที่ทำถูกต้องตามหลักวิชาการหรือไม่"*

ระบบนี้ไม่ได้เป็นเพียงแค่ "เว็บควิซออนไลน์" แต่เป็น **Closed-Loop Mastery Platform** ที่ทำงานบนเครื่องแบบ **Local-First 100%** โดยมีหลักการออกแบบ 6 ประการ:

1. **Deterministic Grading (ตรวจแม่นยำ 100% ไม่ง้อ AI):** ตรวจคำตอบด้วยตรรกะคณิตศาสตร์และกฎเกณฑ์ทางวิทยาศาสตร์แน่นอน รองรับเครื่องหมายลบแบบยูนิโค้ด (`−`, `–`), เลขไทย, เศษส่วน, สัญกรณ์วิทยาศาสตร์ (`2e3`, `2*10^3`) และแปลงหน่วยฟิสิกส์อัตโนมัติ
2. **Pedagogical Root-Cause Diagnosis (เจาะลึก 3 ชั้นความผิดพลาด):**
   - **Plan Step:** ตรวจการเลือกสูตรและมโนทัศน์ตั้งต้นก่อนเริ่มแทนค่า
   - **Checkpoints:** ตรวจจุดคำนวณขั้นกลางระหว่างทำ
   - **Error-Tagged Distractors:** ทุกตัวเลือกผิด (Distractor) มีการระบุแท็กความผิดพลาดเฉพาะทาง (`error_tag`) พร้อมคำอธิบายความเข้าใจผิด
3. **Honest Mastery & Anti-Guessing:** แยกคะแนน "ทำได้เองตั้งแต่แรก (Honest Mastery)" ออกจาก "ทำได้เพราะเปิดคำใบ้ (Assisted)" หรือ "เดาถูก (Lucky Guess)"
4. **Confidence Calibration:** วัดระดับความมั่นใจ 3 ระดับ (*มั่นใจ / ลังเล / เดา*) เทียบกับความถูกต้องจริง เพื่อวินิจฉัยภาวะมั่นใจผิดจุด (*Overconfidence / Dunning-Kruger Effect*)
5. **Exam Pace Benchmarking:** จับเวลาทำข้อสอบจริงเทียบกับเกณฑ์มาตรฐาน MyTCAS พร้อมแสดงสถานะ *เร็วเกินไป (⚡)*, *อยู่ในเกณฑ์ (🎯)* หรือ *ช้าเกินไป (⏳)*
6. **Zero-Placeholder Guarantee & Offline Privacy:** ข้อสอบทุกข้อในคลังผ่านการตรวจสอบความถูกต้องทางวิชาการ ปราศจากข้อความร่างทดลอง และข้อมูลทั้งหมดถูกจัดเก็บในเครื่องผู้เรียน ไม่ส่งข้อมูลออกภายนอก

---

## 2. Architecture & Technology Stack

```
+-------------------------------------------------------------------------+
|                              Client Browser                             |
|    - HTML5 Server-Side Rendered (Jinja2)                                |
|    - Dark / Light Theme Engine (CSS Custom Properties & LocalStorage)   |
|    - Offline KaTeX Math Typesetting Engine                              |
|    - Vanilla ES6 JavaScript (No NPM build step required)                |
+------------------------------------+------------------------------------+
                                     | HTTP Requests (with CSRF / DNS Rebinding check)
                                     v
+-------------------------------------------------------------------------+
|                        FastAPI Web Server (ASGI)                        |
|  [Security Middleware] DNS Rebinding Filter | CSRF Guard | LAN PIN Auth |
+------------------------------------+------------------------------------+
                                     |
    +--------------------------------+--------------------------------+
    |                                |                                |
    v                                v                                v
+----------------------+  +---------------------+  +---------------------+
|    Router Layer      |  |   Services Layer    |  |    Storage Layer    |
| - /practice          |  | - ContentLoader     |  | - SQLite WAL Engine |
| - /mock-exam         |  |   (Atomic Swap)     |  |   (data/tcas.db)    |
| - /formulas          |  | - Grader            |  | - Online Backup     |
| - /drills            |  | - ReviewEngine(SRS) |  |   (VACUUM INTO)     |
| - /answer-sheet      |  | - MockExamEngine    |  | - Content YAMLs     |
| - /stats & /roadmap  |  | - ProceduralGen     |  |   (content/*)       |
| - /import & /system  |  | - PdfImporter       |  | - Static Assets     |
+----------------------+  +---------------------+  +---------------------+
```

### รายละเอียด Tech Stack:
- **Backend Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.13+) รองรับ Async Concurrency
- **Data Validation & Schemas:** [Pydantic v2](https://docs.pydantic.dev/) ตรวจสอบ Schema ของทั้ง API Payload และไฟล์เนื้อหา YAML อย่างเข้มงวด
- **Database:** SQLite 3 พร้อมเปิดโหมด `PRAGMA journal_mode = WAL;`, `synchronous = NORMAL;`, `busy_timeout = 5000;` และ `foreign_keys = ON;`
- **Backup Mechanism:** Zero-downtime Online Backup ผ่านคำสั่ง `VACUUM INTO` บนการเชื่อมต่อแบบ Autocommit
- **Template Engine:** Jinja2 SSR
- **Math Rendering:** [KaTeX](https://katex.org/) ฉบับ Bundled Offline 100% ไม่พึ่งพา External CDN
- **Testing & Verification:** Pytest 9+, AnyIO, Hypothesis (Property-based Testing)
- **YAML Engine:** PyYAML สำหรับการจัดเก็บคลังข้อสอบและพิมพ์เขียว

---

## 3. Project Structure & File Map

```
tcas/
├── app/
│   ├── main.py                     # จุดเริ่มต้นระบบ FastAPI, Security Middleware, Lifecycle
│   ├── config.py                   # การตั้งค่าระบบ, ค่าคงที่, พาธไดเรกทอรี, PIN
│   ├── database.py                 # SQLite WAL Connection Pool, Schema Tables, Migrations
│   │
│   ├── models/                     # โมเดลโครงสร้างข้อมูล (Pydantic Models)
│   │   ├── content_schema.py       # สคีมาข้อสอบ (Question, ChoiceOption, PastPaper, FormulaCard)
│   │   └── api_schema.py           # สคีมารับ-ส่งข้อมูลผ่าน API (Requests / Responses)
│   │
│   ├── services/                   # โมดูลตรรกะทางธุรกิจ (Business Logic Services)
│   │   ├── content_loader.py       # ค้นหา โหลด และ Validate ไฟล์ YAML ด้วย Atomic Pointer Swap
│   │   ├── grader.py               # ตัวตรวจคำตอบ Deterministic (แปลงหน่วย, ตรวจ MCQ/ตัวเลข, ผูก Error Tag)
│   │   ├── mock_exam.py            # ควบคุมระบบสอบจำลอง, พิมพ์เขียว, Autosave, ตัดเกรด
│   │   ├── review_engine.py        # Spaced Repetition (SRS), Honest Mastery, Calibration, Pace
│   │   ├── procedural_gen.py       # ตัวสร้างโจทย์คิดเลขในใจสุ่มตัวเลขไม่จำกัด
│   │   ├── tutor_engine.py         # ตัวแยกย่อยขั้นตอน 5-Step Pedagogical Explanation
│   │   ├── ai_helper.py            # ตัวสร้าง Prompt บริบทสำหรับส่งต่อให้ AI ภายนอก (Zero API Cost)
│   │   ├── pdf_importer.py         # ตัวนำเข้าไฟล์ PDF/รูปภาพ พร้อมการตรวจ Magic Bytes และความปลอดภัย
│   │   ├── backup_service.py       # ตัวจัดการสำรองข้อมูล SQLite VACUUM INTO
│   │   ├── roadmap_service.py      # ตัวคำนวณลำดับความสำคัญของบทเรียนและนับถอยหลังวันสอบ
│   │   ├── study_planner.py        # ตัวสร้างแผนการอ่านหนังสือประจำวันอัตโนมัติ
│   │   └── content_audit.py        # ตัวตรวจทานความสมบูรณ์และสถิติของคุณภาพคลังข้อสอบ
│   │
│   ├── routers/                    # เส้นทาง API และการ Render หน้าเว็บ
│   │   ├── practice.py             # หน้าคลังโจทย์, ฝึกทำข้อสอบเดี่ยว, ส่งคำตอบ, คิวทบทวน
│   │   ├── mock_exam.py            # หน้าเลือกสอบจำลอง, ห้องสอบจับเวลาจริง, ส่งข้อสอบ, รายงานผล
│   │   ├── formulas.py             # หน้ารวมสูตร (ฟิสิกส์ & คณิต) และควิซ Active Recall
│   │   ├── drills.py               # หน้าฝึกคิดเลขในใจสุ่มตัวเลข (Procedural Math Drills)
│   │   ├── answer_sheet.py         # หน้ากระดาษคำตอบสำหรับฝนข้อสอบจากหนังสือหรือข้อสอบเก่า
│   │   ├── stats.py                # หน้าสถิติ, กราฟ Calibration, จุดอ่อนรายวิชา
│   │   ├── roadmap.py              # หน้าผังความสำคัญของเนื้อหา และตัวนับถอยหลังวันสอบ
│   │   ├── planner.py              # หน้าจัดตารางการเรียนประจำวัน
│   │   ├── import_studio.py        # หน้าสกัดข้อสอบจากชีต PDF หรือภาพโซเชียล
│   │   ├── system.py               # หน้าระบบ, ตรวจสอบฐานข้อมูล, สำรองและกู้คืนข้อมูล
│   │   ├── content_audit.py        # หน้าตรวจสอบ Audit คุณภาพโจทย์และสถานะ Verification
│   │   └── progress.py             # หน้ารายงานความก้าวหน้ารายสาระการเรียนรู้
│   │
│   ├── static/                     # ไฟล์ส่วนหน้า (Assets)
│   │   ├── css/
│   │   │   ├── style.css           # CSS หลักของระบบ รองรับ Light & Dark Theme Variables
│   │   │   └── dark_mode.css       # โทนสีและสไตล์ปรับแต่งเฉพาะ Dark Mode
│   │   ├── js/
│   │   │   └── app.js              # ตรรกะสลับ Theme, KaTeX render, Navigation, Shortcuts
│   │   └── vendor/katex/           # โมดูล KaTeX และฟอนต์ทางคณิตศาสตร์แบบ Offline
│   │
│   └── templates/                  # หน้าเว็บ Jinja2 Templates (HTML)
│       ├── base.html               # โครงสร้างหลัก (Navbar, Dark Toggle, KaTeX Init, Footer)
│       ├── dashboard.html          # หน้าแรก สรุปสถิติ คิวทบทวนด่วน ลิงก์สอบจำลอง
│       ├── practice.html           # หน้าทำข้อสอบเดี่ยว พร้อม Step-by-Step และแท็กจุดผิด
│       ├── practice_list.html      # หน้าคลังโจทย์ กรองตามวิชา บทเรียน สถานะตรวจทาน
│       ├── mock_exam_landing.html  # หน้าเลือกชุดข้อสอบจำลองตามโครงสร้าง MyTCAS
│       ├── mock_exam_active.html   # ห้องสอบจับเวลาจริง แถบนำทางข้อสอบ และ Autosave
│       ├── mock_exam_report.html   # รายงานผลสอบจำลอง คะแนน วิเคราะห์จุดอ่อน ส่งเข้าคิว SRS
│       ├── formula_recall.html     # หน้าการท่องจำและทดสอบสูตร Active Recall
│       ├── procedural_drill.html   # หน้าฝึกคิดเลขสุ่มโจทย์จับเวลา
│       ├── answer_sheet.html       # หน้ากระดาษคำตอบตรวจอัตโนมัติ
│       ├── answer_sheet_list.html  # หน้ารายการชุดข้อสอบสำหรับกระดาษคำตอบ
│       ├── stats.html              # หน้ารายงานผลการเรียนรู้และ Honest Mastery
│       ├── roadmap.html            # หน้าแผนการเตรียมตัวสอบและกำหนดการ TCAS
│       ├── planner.html            # หน้าแผนการเรียนประจำวัน
│       ├── import_studio.html      # หน้าสตูดิโอนำเข้าข้อสอบ
│       ├── system.html             # หน้าระบบ สำรองข้อมูล ตรวจสอบสถานะ DB
│       └── content_audit.html      # หน้ารายงานตรวจสอบคุณภาพข้อสอบ
│
├── content/                        # คลังข้อมูลข้อสอบและสูตรในรูปแบบ YAML
│   ├── formulas/                   # บัตรสูตร (Formula Cards)
│   │   ├── physics_formulas.yaml   # สูตรฟิสิกส์ ม.ปลาย ครบทุกบท พร้อมโจทย์ Active Recall
│   │   └── math_formulas.yaml      # สูตรคณิตศาสตร์ประยุกต์ 1 พร้อมโจทย์ Active Recall
│   ├── physics/                    # คลังโจทย์ฟิสิกส์เดี่ยว (การเคลื่อนที่, แรง, เวกเตอร์)
│   ├── math/                       # คลังโจทย์คณิตศาสตร์ประยุกต์เดี่ยว (พีชคณิต, ฟังก์ชัน)
│   ├── tpat3/                      # คลังโจทย์ TPAT3 เชิงตัวเลขและกลศาสตร์คำนวณ
│   ├── tgat1/                      # คลังโจทย์ TGAT1 ทักษะการพูด (Speaking) และการอ่าน (Reading)
│   ├── tgat3/                      # คลังโจทย์ TGAT3 แยก 4 ด้านสมรรถนะ
│   ├── past_papers/                # ชุดข้อสอบจำลองเต็มรูปแบบและแบบฝึกซ้อมจับเวลา
│   │   ├── tgat1_blueprint_60.yaml # TGAT1 60 ข้อ (พิมพ์เขียว MyTCAS 91)
│   │   ├── tgat3_blueprint_60.yaml # TGAT3 60 ข้อ (พิมพ์เขียว MyTCAS 93)
│   │   ├── tpat3_blueprint_70.yaml # TPAT3 70 ข้อ (พิมพ์เขียว MyTCAS 30)
│   │   ├── tpat3_practice_25.yaml  # TPAT3 25 ข้อ (ชุดฝึกซ้อม)
│   │   ├── alevel_phy_blueprint_30.yaml # A-Level ฟิสิกส์ 30 ข้อ (พิมพ์เขียวทางการ)
│   │   └── alevel_phy_sample.yaml  # A-Level ฟิสิกส์ 20 ข้อ (ชุดตัวอย่าง)
│   └── imported/                   # โจทย์ที่นำเข้าจากชีต PDF หรือรูปภาพ
│
├── data/                           # ที่เก็บฐานข้อมูล SQLite รันไทม์
│   ├── tcas.db                     # ไฟล์ฐานข้อมูล SQLite จริง (อยู่นอก Git)
│   ├── backups/                    # โฟลเดอร์สำรองข้อมูล VACUUM INTO
│   └── assets/                     # โฟลเดอร์เก็บภาพหน้าที่ตัดจาก PDF
│
├── tests/                          # ชุดทดสอบอัตโนมัติ Pytest (150 ข้อ ผ่าน 100%)
├── run.bat                         # สคริปต์เปิดระบบ 1 คลิกบน Windows
├── requirements.txt                # รายการโมดูล Python ที่ต้องใช้
└── TEST_READY.md                   # เอกสารรับรองผลการทดสอบและความพร้อมของระบบ
```

---

## 4. Content Catalog & Blueprint Inventory

ระบบมีคลังโจทย์ที่ผ่านการตรวจสอบทางวิชาการและพร้อมใช้งานรวมทั้งสิ้น **327 ข้อ** และ **22 บัตรสูตร** ดังนี้:

### 4.1 สรุปจำนวนข้อสอบตามรายวิชา (Subject Breakdown)

| รหัสวิชา | ชื่อวิชา | ข้อสอบรวม | รูปแบบข้อสอบในระบบ |
|---|---|:---:|---|
| **tpat3** | ความถนัดด้านวิทยาศาสตร์ เทคโนโลยี และวิศวกรรมศาสตร์ | **105 ข้อ** | • Blueprint 70 ข้อเต็มรูปแบบ<br>• Practice Set 25 ข้อ<br>• Quantitative Drills 10 ข้อ |
| **tgat1** | การสื่อสารภาษาอังกฤษ (English Communication) | **80 ข้อ** | • Blueprint 60 ข้อเต็มรูปแบบ<br>• Speaking Drills 10 ข้อ<br>• Reading Drills 10 ข้อ |
| **tgat3** | สมรรถนะการทำงานในอนาคต (Future Workforce Competencies) | **76 ข้อ** | • Blueprint 60 ข้อเต็มรูปแบบ<br>• สมรรถนะ 4 ด้านย่อย 16 ข้อ (ด้านละ 4 ข้อ) |
| **physics** | ฟิสิกส์ประยุกต์ A-Level | **62 ข้อ** | • Blueprint 30 ข้อทางการ (ปรนัย 25 + ตัวเลข 5)<br>• Sample Set 20 ข้อ<br>• แบบฝึกหัดรายบท 12 ข้อ |
| **math** | คณิตศาสตร์ประยุกต์ 1 A-Level | **4 ข้อ** | • พีชคณิตพื้นฐานและฟังก์ชัน (เนื้อหารองรับ Prerequisite) |
| **รวมทั้งหมด** | | **327 ข้อ** | **1,024 ตัวเลือก, 788 ตัวลวงมี `error_tag` ครบ 100%** |

---

### 4.2 รายละเอียดชุดข้อสอบจำลอง 6 ชุด (Past Paper Blueprints)

#### 1. TGAT1 Blueprint 60 ข้อ (`tgat1-blueprint-60`)
- **เวลาสอบ:** 60 นาที | **คะแนนเต็ม:** 100.0 คะแนน | **เวลาเฉลี่ยเป้าหมาย:** 1.0 นาที/ข้อ
- **ส่วนที่ 1: ทักษะการพูด (Speaking Skills) 30 ข้อ (ข้อละ 1.6667 คะแนน = 50.0 คะแนน)**
  - ถาม-ตอบ (Question-Response): ข้อ 1–10
  - บทสนทนาสั้น (Short Conversations): ข้อ 11–20
  - บทสนทนายาว (Long Conversations): ข้อ 21–30
- **ส่วนที่ 2: ทักษะการอ่าน (Reading Skills) 30 ข้อ (ข้อละ 1.6667 คะแนน = 50.0 คะแนน)**
  - เติมข้อความในบทความ (Text Completion): ข้อ 31–45
  - อ่านจับใจความ (Reading Comprehension): ข้อ 46–60

#### 2. TGAT3 Blueprint 60 ข้อ (`tgat3-blueprint-60`)
- **เวลาสอบ:** 60 นาที | **คะแนนเต็ม:** 100.0 คะแนน | **เวลาเฉลี่ยเป้าหมาย:** 1.0 นาที/ข้อ
- แบ่งออกเป็น 4 สมรรถนะเท่ากัน สมรรถนะละ 15 ข้อ (ข้อละ 1.6667 คะแนน = 25.0 คะแนน):
  - **ส่วนที่ 1:** การสร้างคุณค่าและนวัตกรรม (Value Creation & Innovation) ข้อ 1–15
  - **ส่วนที่ 2:** การแก้ไขปัญหาที่ซับซ้อน (Complex Problem Solving) ข้อ 16–30
  - **ส่วนที่ 3:** การบริหารจัดการอารมณ์ (Emotional Governance) ข้อ 31–45
  - **ส่วนที่ 4:** การเป็นพลเมืองที่มีส่วนร่วมของสังคม (Civic Engagement) ข้อ 46–60

#### 3. TPAT3 Blueprint 70 ข้อ (`tpat3-blueprint-70`)
- **เวลาสอบ:** 180 นาที (3 ชั่วโมง) | **คะแนนเต็ม:** 100.0 คะแนน | **เวลาเฉลี่ยเป้าหมาย:** 2.5 นาที/ข้อ
- **ส่วนที่ 1: การทดสอบความถนัด (Aptitude) 45 ข้อ (ข้อละ 1.3333 คะแนน = 60.0 คะแนน)**
  - ด้านตัวเลข (Numerical Reasoning): ข้อ 1–15
  - ด้านมิติสัมพันธ์ (Spatial Relations): ข้อ 16–30
  - ด้านเชิงกลและฟิสิกส์ (Mechanical & Physics): ข้อ 31–45
- **ส่วนที่ 2: การทดสอบความคิดและความสนใจทางวิทยาศาสตร์ เทคโนโลยี และวิศวกรรมศาสตร์ 25 ข้อ (ข้อละ 1.6 คะแนน = 40.0 คะแนน)**
  - ความคิดเชิงวิทยาศาสตร์ (Scientific Thinking): ข้อ 46–60 (15 ข้อ = 24.0 คะแนน)
  - ความสนใจและตรรกะทางเทคโนโลยี (Technology Awareness): ข้อ 61–70 (10 ข้อ = 16.0 คะแนน)

#### 4. A-Level ฟิสิกส์ Blueprint 30 ข้อ (`alevel-phy-blueprint-30`)
- **เวลาสอบ:** 90 นาที | **คะแนนเต็ม:** 100.0 คะแนน | **เวลาเฉลี่ยเป้าหมาย:** 3.0 นาที/ข้อ
- **ตอนที่ 1:** แบบปรนัย 5 ตัวเลือก 25 ข้อ (ข้อละ 3.0 คะแนน = 75.0 คะแนน)
- **ตอนที่ 2:** แบบอัตนัยระบายคำตอบเป็นตัวเลข 5 ข้อ (ข้อละ 5.0 คะแนน = 25.0 คะแนน)

#### 5. TPAT3 Practice 25 ข้อ (`tpat3-practice-25`)
- **เวลาสอบ:** 60 นาที | **คะแนนเต็ม:** 100.0 คะแนน | ชุดฝึกซ้อมมิติสัมพันธ์ การคิดเชิงตัวเลข และกลศาสตร์เบื้องต้น

#### 6. A-Level ฟิสิกส์ Sample 20 ข้อ (`alevel-phy-2566-mock`)
- **เวลาสอบ:** 60 นาที | **คะแนนเต็ม:** 64.0 คะแนน | ปรนัย 18 ข้อ (ข้อละ 3 คะแนน) + อัตนัย 2 ข้อ (ข้อละ 5 คะแนน)

---

## 5. Data Models & YAML Schemas

ไฟล์เนื้อหาทั้งหมดถูกจัดเก็บในรูปแบบ YAML และถูกตรวจสอบความถูกต้องผ่าน Pydantic models ใน `app/models/content_schema.py`

### 5.1 ตัวอย่างโครงสร้างโจทย์แบบปรนัย (Single Choice Question with Distractor Error Tags)

```yaml
- id: "phy-kin-0001"
  subject: "physics"
  topic: "physics.kinematics.1d"
  source:
    type: "official_blueprint"
    label: "A-Level ฟิสิกส์ Mock Exam"
    exam_year: 2566
  verification:
    tier: "A"
    status: "verified"
    verified_by: "expert_review"
  skills:
    primary: "kinematics_constant_acceleration"
    secondary: ["unit_conversion", "vector_signs"]
  stem: |
    รถยนต์คันหนึ่งแล่นด้วยความเร็วต้น $20\text{ m/s}$ ผู้ขับเหยียบเบรกให้รถชะลอความเร็วด้วยความเร่งคงตัว $4\text{ m/s}^2$ 
    จนกระทั่งรถหยุดสนิท จงหาระยะทางที่รถเคลื่อนที่ได้ตั้งแต่เริ่มเหยียบเบรกจนหยุด
  difficulty: 2
  estimated_seconds: 120
  plan_step:
    prompt: "ขั้นตอนแรกในการแก้โจทย์ข้อนี้คืออะไร?"
    options:
      a: "ใช้สมการ $v = u + at$ เพื่อหาระยะทางโดยตรง"
      b: "ใช้สมการ $v^2 = u^2 + 2as$ เพราะทราบความเร็วต้น ความเร็วปลาย และความเร่ง โดยไม่ต้องหาเวลา $t$"
    answer: "b"
    explanation: "โจทย์ให้ $u=20$, $v=0$, $a=-4$ และต้องการหา $s$ การใช้สมการที่ไม่ติดตัวแปรเวลาจะทำให้คำนวณได้เร็วที่สุด"
  answer:
    type: "single_choice"
    options:
      - id: "1"
        text: "25 m"
        correct: false
        error_tag: "arithmetic_error"
        explanation: "คำนวณเลขผิดในขั้นตอนหาร $400 / 8$"
      - id: "2"
        text: "50 m"
        correct: true
        error_tag: null
        explanation: "ถูกต้อง! จาก $v^2 = u^2 + 2as \implies 0^2 = 20^2 + 2(-4)s \implies 8s = 400 \implies s = 50\text{ m}$"
      - id: "3"
        text: "100 m"
        correct: false
        error_tag: "missing_factor_2"
        explanation: "ลืมตัวคูณ 2 ในเทอม $2as$ ทำให้ได้ $s = 400 / 4 = 100\text{ m}$"
      - id: "4"
        text: "200 m"
        correct: false
        error_tag: "formula_misapplication"
        explanation: "ใช้สูตร $s = vt$ โดยแทนค่า $t=10$ โดยไม่ได้นำความเร่งมาคิดร่วม"
  hints:
    - level: 1
      text: "ระบุตัวแปรที่โจทย์กำหนด: $u = 20$, $v = 0$, ความเร่งชะลอความเร็ว $a = -4\text{ m/s}^2$"
    - level: 2
      text: "เลือกสมการการเคลื่อนที่แนวตรงที่ไม่มีตัวแปรเวลา $t$: คือ $v^2 = u^2 + 2as$"
    - level: 3
      text: "แทนค่า: $0 = (20)^2 + 2(-4)s \implies 8s = 400 \implies s = 50\text{ m}$"
  solution:
    summary: "ระยะทางในการเบรกจนหยุดคือ 50 เมตร"
    common_mistakes: "ลืมใส่เครื่องหมายลบให้กับความเร่งชะลอความเร็ว หรือลืมตัวคูณ 2 ในสมการ"
    steps:
      - id: "s1"
        text: "กำหนดทิศทางการเคลื่อนที่ไปข้างหน้าเป็นบวก จะได้ $u = +20\text{ m/s}$, $v = 0$, ความเร่งเบรก $a = -4\text{ m/s}^2$"
      - id: "s2"
        text: "แทนค่าในสูตร $v^2 = u^2 + 2as$"
        math: "0^2 = (20)^2 + 2(-4)s"
      - id: "s3"
        text: "แก้สมการหาระยะทาง $s$"
        math: "8s = 400 \implies s = 50\\text{ m}"
```

---

### 5.2 ตัวอย่างโครงสร้างโจทย์แบบเติมตัวเลขและหน่วย (Numeric Question with Tolerance & Unit)

```yaml
- id: "phy-num-0002"
  subject: "physics"
  topic: "physics.mechanics.forces"
  source:
    type: "official_past_paper"
    label: "A-Level ฟิสิกส์ ข้อสอบจริง"
    exam_year: 2566
  verification:
    tier: "A"
    status: "verified"
  skills:
    primary: "newton_second_law"
    secondary: ["friction_coefficient"]
  stem: |
    มวล $5\text{ kg}$ วางอยู่บนพื้นราบที่มีสัมประสิทธิ์ความเสียดทานจลน์ $\mu_k = 0.2$ 
    ถูกแรงดึงในแนวราบ $F = 20\text{ N}$ จงหาความเร่งของวัตถุ (กำหนด $g = 10\text{ m/s}^2$)
  difficulty: 3
  answer:
    type: "numeric"
    correct_value: 2.0
    unit: "m/s^2"
    tolerance: 0.02
    require_unit: true
```

---

### 5.3 ตัวอย่างโครงสร้างบัตรสูตรและ Active Recall (FormulaCard)

```yaml
- id: "form-kin-01"
  subject: "physics"
  topic: "physics.kinematics.1d"
  title: "สมการการเคลื่อนที่แนวตรง (ไม่มีเวลา t)"
  latex: "v^2 = u^2 + 2as"
  conditions:
    - "ความเร่ง (a) ต้องคงตัวตลอดช่วงการเคลื่อนที่"
    - "การเคลื่อนที่เป็นแนวเส้นตรง 1 มิติ"
  variables:
    u: "ความเร็วต้น (m/s)"
    v: "ความเร็วปลาย (m/s)"
    a: "ความเร่ง (m/s^2)"
    s: "การกระจัด (m)"
  selection_cues:
    - "ใช้เมื่อโจทย์ไม่บอกเวลา (t) และไม่ต้องการหาเวลา (t)"
    - "โจทย์บอกระยะทาง ความเร็วต้น ความเร็วปลาย และถามหาความเร่ง"
  recall_questions:
    - prompt: "สมการ $v^2 = u^2 + 2as$ ใช้ได้ภายใต้เงื่อนไขใดเป็นสำคัญ?"
      options:
        a: "ความเร็วต้องคงตัว ($a = 0$)"
        b: "ความเร่งต้องมีค่าคงตัว ($a = \\text{const}$)"
        c: "วัตถุต้องตกอย่างอิสระเท่านั้น"
      answer: "b"
      explanation: "สมการ 5 สูตรการเคลื่อนที่แนวตรงประยุกต์ใช้ได้เฉพาะกรณีความเร่งคงตัวเท่านั้น"
```

---

## 6. Deterministic Grading & Pedagogical Diagnosis

ระบบตรวจคำตอบใน `app/services/grader.py` ไม่ใช้ LLM ในการตัดสิน แต่ใช้ **Deterministic Evaluation Engine**:

### 6.1 การทำความสะอาดข้อมูลตัวเลข (Input Normalization)
- **Unicode Replacement:** แปลงเครื่องหมายลบประเภทต่างๆ (`−`, `–`) กลับเป็น Regular ASCII `-`
- **Thai Numerals:** แปลงเลขไทย `๑๒๓๔๕๖๗๘๙๐` เป็นเลขอารบิก `1234567890`
- **Punctuation & Spaces:** ตัดจุลภาคคั่นหลักพัน (`1,500` $\implies$ `1500`), จัดการสัญลักษณ์เว้นวรรค
- **Fractions & Scientific Notation:** แปลงเศษส่วน (`3/4` $\implies$ `0.75`), สัญกรณ์วิทยาศาสตร์ (`2.5e-3`, `2.5*10^-3` $\implies$ `0.0025`)
- **Tolerance Checking:** ตรวจความคลาดเคลื่อนเทียบกับค่าสัมพัทธ์ `tolerance` (ปกติ $\pm 2\%$)

### 6.2 การตรวจสอบความสอดคล้องของหน่วยฟิสิกส์ (Physical Unit Matching)
ระบบรองรับตารางคำพ้องของหน่วย (`UNIT_SYNONYMS`) ครบถ้วน เช่น:
- ความเร็ว: `m/s`, `ms-1`, `m.s-1`, `m s^-1`, `เมตร/วินาที`, `เมตรต่อวินาที`
- ความเร่ง: `m/s^2`, `m/s2`, `ms-2`, `m.s-2`, `เมตร/วินาที²`
- ความหนาแน่น: `kg/m^3`, `kg/m3`, `กก./ลบ.ม.`
- กำลังและพลังงาน: `W`, `watt`, `วัตต์`, `J`, `joule`, `จูล`
*หากตัวเลขถูกแต่ลืมระบุหน่วย หรือแปลงหน่วยผิด ระบบจะให้คะแนนเป็น False พร้อมติดแท็ก `missing_unit` หรือ `no_unit_conversion` ทันที*

### 6.3 อนุกรมวิธานแท็กจุดผิด (Error Tag Taxonomy)

| แท็กความผิดพลาด (`error_tag`) | คำอธิบายความเข้าใจผิด (Pedagogical Misconception) |
|---|---|
| `no_unit_conversion` | ลืมแปลงหน่วย (เช่น ไม่ได้แปลง $km/h$ เป็น $m/s$ หรือ $cm$ เป็น $m$) |
| `missing_factor_2` | ลืมตัวคูณ 2 ในสมการ (เช่น เทอม $2as$) |
| `missing_factor_half` | ลืมตัวคูณ 1/2 ในสมการ (เช่น เทอม $\frac{1}{2}at^2$ หรือ $\frac{1}{2}mv^2$) |
| `sign_error` | เครื่องหมายเวกเตอร์ผิด (เช่น กำหนดให้ทิศลงเป็นบวกแต่แทนค่าความเร็วต้นติดลบ) |
| `sign_error_friction` | สับสนทิศทางของแรงเสียดทาน (แรงเสียดทานต้องต้านการเคลื่อนที่สัมพัทธ์เสมอ) |
| `forgot_friction` | ลืมคิดผลของแรงต้านหรือแรงเสียดทานในระบบ |
| `rearrange_error` | ย้ายข้างสมการพีชคณิตผิดพลาด |
| `only_to_peak` | คิดเฉพาะเวลาหรือระยะทางที่ลอยถึงจุดสูงสุด ยังไม่ได้คิดช่วงตกกลับลงมา |
| `return_to_cliff_level` | คิดเฉพาะเวลาที่ลอยกลับมาระดับเดิม ยังไม่ถึงก้นหน้าผา |
| `rectangle_only` | คิดพื้นที่ใต้กราฟเฉพาะสี่เหลี่ยมผืนผ้า ลืมว่าช่วงเร่ง/เบรกเป็นรูปสามเหลี่ยม |
| `velocity_match_only` | สับสนระหว่าง "ความเร็วเท่ากัน" กับ "แล่นทันกัน (การกระจัดเท่ากัน)" |
| `forgot_domain_restriction` | ลืมเงื่อนไขตัวส่วนห้ามเป็นศูนย์ในสมการ/อสมการเศษส่วน |
| `cross_multiplied_denominator` | คูณไขว้ตัวแปรที่มีโอกาสติดลบทิ้งไปโดยไม่สลับเครื่องหมายอสมการ |
| `intermediate_stage_only` | ตอบผลลัพธ์ของขั้นกลาง ลืมคำนวณต่อให้ถึงสิ่งที่โจทย์ถามจริง |
| `inverse_ratio_flipped` | สลับเศษเป็นส่วนในความสัมพันธ์แปรผกผัน |
| `wrong_unit` | ระบุหน่วยไม่ตรงกับที่โจทย์ต้องการ |
| `missing_unit` | ไม่ได้ใส่หน่วยกำกับ ทั้งที่โจทย์กำหนดให้ระบุหน่วย |
| `arithmetic_error` | คิดเลขหรือทดเลขผิดพลาด |

---

## 7. Spaced Repetition, Honest Mastery & Calibration

ระบบบริหารการเรียนรู้ใน `app/services/review_engine.py` จัดการข้อมูลการฝึกทำโจทย์ดังนี้:

### 7.1 Honest Mastery vs. Assisted Mastery
- **`correct_first_try`:** ตอบถูกตั้งแต่รอบแรกโดยไม่เปิดคำใบ้ $\implies$ ได้สถานะ **Honest Mastery** ได้คะแนนเต็ม
- **`correct_assisted`:** ตอบถูกหลังจากเปิดคำใบ้ (Hint Level 1–3) $\implies$ ระบบถือว่ายังไม่เชี่ยวชาญแท้จริง และจะถูกดึงเข้าคิวทบทวนซ้ำ
- **`wrong`:** ตอบผิด $\implies$ บันทึก `error_tag` และตั้งคิวทบทวนด่วน (Priority = `high`)

### 7.2 Spaced Repetition (SRS Adaptive Scheduling)
อิงหลักการ Leitner Box ร่วมกับการคำนวณช่วงเวลาแบบปรับเปลี่ยนตามผลการทำ:
- **ตอบถูกครั้งแรก (Honest Mastery, Sure):** เพิ่มช่วงเวลาทบทวน: $1 \to 3 \to 7 \to 14 \to 30$ วัน
- **ตอบถูกแต่ลังเล (Unsure / Guessed):** ลดอัตราการคูณช่วงเวลา (Multiplier = 1.2) เพื่อให้กลับมาทบทวนเร็วกว่าปกติ
- **ตอบถูกหลังเปิดคำใบ้:** กำหนดช่วงเวลาทบทวนไม่เกิน 2 วัน
- **ตอบผิด:** รีเซ็ตช่วงเวลากลับมาเป็น 1 วันทันที พร้อมติดแท็กความเข้าใจผิด

### 7.3 Confidence Calibration & Overconfidence Detection
ทุกครั้งที่ส่งคำตอบ ผู้เรียนต้องเลือกความมั่นใจ:
- `sure` (มั่นใจ)
- `unsure` (ลังเล)
- `guessed` (เดา)

ระบบวิเคราะห์ไขว้ระหว่างความมั่นใจและความถูกต้อง:
- **Overconfidence Rate (อันตรายสูงสุด):** ตอบ `sure` แต่ผลลัพธ์คือ **`wrong`** $\implies$ สะท้อนความเข้าใจผิดอย่างรุนแรง (Severe Misconception)
- **Underconfidence:** ตอบถูก แต่เลือก `guessed` หรือ `unsure`
- **True Mastery:** ตอบถูก และเลือก `sure`

### 7.4 Real-time Exam Pace Tracking
ประเมินความเร็วในการทำเทียบกับเวลาเฉลี่ยของข้อสอบทางการ:
- **ฟิสิกส์ / คณิตประยุกต์:** เกณฑ์เฉลี่ย **180 วินาที (3 นาที/ข้อ)**
- **TPAT3:** เกณฑ์เฉลี่ย **150 วินาที (2.5 นาที/ข้อ)**
- **TGAT1 / TGAT3:** เกณฑ์เฉลี่ย **60 วินาที (1 นาที/ข้อ)**

ระบบส่งคืน Badge วินิจฉัย:
- ⚡ **`fast`:** ใช้เวลาน้อยกว่าเกณฑ์เป้าหมายอย่างมีนัยสำคัญ
- 🎯 **`optimal`:** อยู่ในเกณฑ์ $\pm 15\%$ ของเวลามาตรฐาน
- ⏳ **`slow`:** ช้ากว่าเกณฑ์ แนะนำให้ทบทวนสูตรลัดหรือวิธีตัดช้อยส์

---

## 8. Mock Exam Engine & Blueprint Rules

ระบบจำลองการสอบใน `app/services/mock_exam.py` และ `app/routers/mock_exam.py`:

```
+-------------------------------------------------------------------------+
|                           Mock Exam Lifecycle                           |
+-------------------------------------------------------------------------+
  1. Start Exam  ──>  Create Session in DB (mock_exam_sessions)
                      Sanitize Questions (Strip correct answers/solutions)
                      Initialize Countdown Timer in Browser
  2. Active Exam ──>  AutoSave answers & flagged questions via /save (periodic)
                      Paging & Grid Navigation (Question palette)
  3. Submit Exam ──>  Submit payload via /submit (Idempotent)
                      Grade deterministically against official blueprints
                      Compute Topic Breakdown & Timing Stats
                      Inject wrong answers into Spaced Repetition queue
  4. Diagnostic  ──>  Render /mock-exam/{session_id}/report
     Report           Full Solutions + Distractor Error Tags Unlocked
                      Direct link to review individual questions
```

### มาตรการความปลอดภัยในการสอบ (Anti-Cheating Invariant)
ในระหว่างที่ผู้เรียนทำข้อสอบจำลอง (`status = in_progress`):
- API จะส่งเฉพาะ `stem`, `options` (เฉพาะ `id` และ `text`), `number`, `answer_type`
- **เฉลย (`correct_answer`), คำอธิบาย (`explanation`), สูตร (`solution`), และคำใบ้ (`hints`) จะถูกตัดทิ้งทั้งหมดจาก Payload**
- ข้อมูลเฉลยจะถูกนำมาประมวลผลบนเซิร์ฟเวอร์เมื่อผู้เรียนกดส่งข้อสอบเท่านั้น

---

## 9. Procedural Drills & Formula Studio

### 9.1 แบบฝึกคิดเลขในใจสุ่มตัวเลขไม่จำกัด (Procedural Math Drills)
อยู่ใน `app/services/procedural_gen.py` สร้างโจทย์คณิตศาสตร์และฟิสิกส์แบบสุ่มตัวเลขใหม่ทุกครั้ง:
1. **`speed_conversion`:** แปลงหน่วย $km/h \leftrightarrow m/s$
2. **`area_volume`:** แปลงหน่วยพื้นที่และปริมาตร ($cm^2 \leftrightarrow m^2$, $cm^3 \leftrightarrow m^3$, $L \leftrightarrow m^3$)
3. **`kinematics_5_formulas`:** แทนค่า 5 สูตรการเคลื่อนที่แนวตรงสุ่มตัวแปร
4. **`powers_and_scientific`:** สัดส่วนเลขยกกำลังและสัญกรณ์วิทยาศาสตร์

### 9.2 สตูดิโอบัตรสูตรและการระลึกสูตร (Formula Studio & Active Recall)
อยู่ใน `content/formulas/` และ `app/routers/formulas.py`:
- รวม 22 บัตรสูตรฟิสิกส์และคณิตศาสตร์ พร้อมข้อจำกัดการใช้งาน (`conditions`), คำอธิบายตัวแปร (`variables`), และสัญญาณเตือนการเลือกสูตร (`selection_cues`)
- โหมด **Active Recall Quiz:** ถาม-ตอบทดสอบความเข้าใจว่า "เมื่อไหร่ควรใช้สูตรนี้" และ "เงื่อนไขใดที่ห้ามใช้"
- ปุ่ม **Quick Navigation:** สลับกลับไปยังหน้าทำโจทย์ได้อย่างราบรื่น

---

## 10. Security, Database & Dark Mode

### 10.1 ความปลอดภัยระดับเครือข่ายและเบราว์เซอร์
- **DNS Rebinding & Host Filter:** กรอง `Host` header ป้องกันการโจมตีจากเว็บไซต์ภายนอก
- **CSRF & Origin Guard:** บล็อก HTTP Mutation (`POST`, `PUT`, `DELETE`) จาก Origin/Referer ที่ไม่ได้รับอนุญาต
- **Private LAN IP Range (RFC 1918):** รองรับการเปิดทำข้อสอบผ่านแท็บเล็ต/ไอแพดในวงแลนบ้าน (`192.168.x.x`, `10.x.x.x`)
- **LAN Protection PIN (`TCAS_ACCESS_PIN`):** กำหนด PIN ความปลอดภัยสำหรับการเรียกใช้ฟังก์ชันจัดการฐานข้อมูลหรืออัปโหลดไฟล์
- **Anti-PDF Bomb:** จำกัดขนาดไฟล์และจำนวนหน้าของไฟล์ PDF ที่นำเข้า ป้องกัน Memory Exhaustion

### 10.2 ฐานข้อมูล SQLite และระบบสำรองข้อมูล
- จัดเก็บที่ `data/tcas.db`
- ใช้โหมด **WAL (Write-Ahead Logging)** ป้องกันปัญหา Database Locked จากการอ่าน/เขียนพร้อมกัน
- ฟังก์ชันสำรองข้อมูลสดผ่าน **`VACUUM INTO 'data/backups/...'`** รับประกันความสมบูรณ์ของข้อมูล 100% โดยไม่ต้องหยุดการทำงานของเซิร์ฟเวอร์

### 10.3 ระบบ Dark Mode เต็มรูปแบบ
- ออกแบบผ่าน CSS Custom Properties (`--bg-page`, `--bg-card`, `--text-main`, `--border-color`)
- มี Anti-Flicker Script ใน `<head>` อ่านค่าจาก `localStorage.getItem('tcas_theme')` ก่อน Render ป้องกันแสงวาบขาว
- KaTeX ปรับสีตัวอักษรและสัญลักษณ์คณิตศาสตร์ให้สบายตาโดยอัตโนมัติในโหมดกลางคืน

---

## 11. Complete API Reference

| หมวดหมู่ | Method | Path | Request Body / Params | รายละเอียดการทำงาน |
|---|:---:|---|---|---|
| **หน้าหลัก** | `GET` | `/` | - | Dashboard สรุปสถิติ, คิวทบทวน, ข้อสอบจำลองล่าสุด |
| **การฝึกทำโจทย์** | `GET` | `/practice` | `?subject=`, `?topic=`, `?verified_only=` | หน้ารายการคลังโจทย์ กรองตามวิชาและหัวข้อ |
| | `GET` | `/practice/interleaved` | `?limit=15` | ชุดฝึกสลับหัวข้อและวิชาแบบ Round-Robin |
| | `GET` | `/practice/{question_id}` | - | หน้าทำโจทย์รายข้อ พร้อมระบบ Hint และ Plan Step |
| | `POST` | `/api/submit-attempt` | `SubmitAttemptRequest` (JSON) | ตรวจคำตอบแบบ Deterministic, คำนวณ SRS และ Pace |
| | `POST` | `/api/bookmark/toggle` | `{"question_id": "..."}` | บุ๊กมาร์กข้อสอบไว้ทบทวนภายหลัง |
| | `GET` | `/api/ai-prompt/presolve/{id}` | - | สร้าง Prompt ถามแนวคิด AI โดยไม่สปอยล์คำตอบ |
| **ข้อสอบจำลอง** | `GET` | `/mock-exam` | - | หน้ารวมพิมพ์เขียวข้อสอบจำลองและประวัติการสอบ |
| | `POST` | `/api/mock-exam/start` | `{"exam_type": "tgat1_mock_60"}` | เริ่มรอบสอบจำลองใหม่ และสร้าง Session ID |
| | `GET` | `/mock-exam/{session_id}` | - | ห้องสอบจับเวลาจริง (ส่งเฉพาะคำถามที่ Sanitize แล้ว) |
| | `POST` | `/api/mock-exam/{session_id}/save` | `{"answers": {...}, "flagged": [...]}` | Autosave คำตอบระหว่างสอบแบบ Idempotent |
| | `POST` | `/api/mock-exam/{session_id}/submit`| `{"answers": {...}, "time_spent_min": ...}` | ส่งข้อสอบ ตัดเกรดตามพิมพ์เขียว บันทึกรายงานผล |
| | `GET` | `/mock-exam/{session_id}/report` | - | หน้ารายงานผลสอบจำลองรายสาระ พร้อมเฉลยละเอียด |
| **คลังสูตร** | `GET` | `/formulas` | `?subject=physics` หรือ `?subject=math` | หน้ารวมบัตรสูตรฟิสิกส์และคณิตศาสตร์ |
| | `GET` | `/formulas/{id}/recall` | - | หน้าทดสอบความเข้าใจสูตร (Active Recall Quiz) |
| | `POST` | `/api/formulas/submit` | `FormulaRecallSubmitRequest` (JSON) | ตรวจคำตอบการทดสอบสูตร |
| **คิดเลขในใจ** | `GET` | `/drills` | - | หน้ารวมหมวดฝึกคิดเลขในใจสุ่มตัวเลข |
| | `GET` | `/drills/{drill_type}` | - | หน้าทำแบบฝึกคิดเลขในใจตามหมวดที่เลือก |
| | `GET` | `/api/drills/generate` | `?drill_type=...` | สุ่มตัวเลขและสร้างโจทย์คิดเลขข้อใหม่ |
| | `POST` | `/api/drills/submit` | `ProceduralSubmitRequest` (JSON) | ตรวจคำตอบคิดเลขในใจ (Tolerance $\le 0.1\%$) |
| **กระดาษคำตอบ** | `GET` | `/answer-sheet` | - | หน้ารวมชุดข้อสอบกระดาษคำตอบ |
| | `GET` | `/answer-sheet/{paper_id}` | - | หน้ากรอกกระดาษคำตอบสำหรับฝนข้อสอบจากหนังสือ |
| | `POST` | `/api/answer-sheet/submit` | `AnswerSheetSubmitRequest` (JSON) | ตรวจกระดาษคำตอบและวิเคราะห์ผล |
| **การวางแผน** | `GET` | `/roadmap` | - | หน้าผังความสำคัญบทเรียนและนับถอยหลังวันสอบ |
| | `GET` | `/planner` | - | หน้าตารางจัดแผนการอ่านหนังสือประจำวัน |
| | `GET` | `/stats` | - | หน้ารายงานสถิติ Honest Mastery และ Calibration |
| **การจัดการระบบ**| `GET` | `/system` | - | หน้าจัดการระบบและข้อมูลสำรอง |
| | `POST` | `/api/backup/create` | - | สร้างไฟล์สำรองฐานข้อมูลสดผ่าน `VACUUM INTO` |
| | `POST` | `/api/backup/restore` | `{"filename": "..."}` | กู้คืนฐานข้อมูลจากไฟล์สำรอง |
| | `GET` | `/api/system/integrity-check` | - | ตรวจสอบความสมบูรณ์ของฐานข้อมูล SQLite |
| | `GET` | `/audit` | - | หน้าตรวจสอบ Audit คุณภาพข้อสอบและแท็กตัวลวง |

---

## 12. Testing & Verification Pyramid

ระบบใช้การทดสอบแบบเข้มงวด 4 ระดับ (Pyramid Verification) ทั้งหมด **150 ข้อทดสอบ (100% Pass Rate)**:

```
                      / \
                     /   \
                    / T4  \    Tier 4: E2E Simulation & Blueprint Execution
                   /-------\   (18 tests in test_e2e_content.py + Mock Exam routes)
                  /   T3    \
                 /-----------\  Tier 3: Pedagogical Quality & Distractor Analysis
                /     T2      \ (Zero Placeholders, 100% Error Tags, Step-by-Step)
               /---------------\
              /       T1        \ Tier 1 & 2: Pydantic Schema Contracts & Ingestion
             /-------------------\ (Strict Model Validation, Tolerance, Grader)
```

### คำสั่งรันชุดทดสอบ:
```powershell
# 1. รันชุดทดสอบทั้งหมด 150 ข้อ
py -m pytest -v

# 2. รันเฉพาะชุดทดสอบ E2E และความถูกต้องทางวิชาการ
py -m pytest tests/test_e2e_content.py -v

# 3. รันเพื่อทดสอบการโหลดคลังข้อสอบแบบ In-Memory Atomic Swap
py -c "from app.services.content_loader import content_loader; content_loader.reload(); print('Loaded Questions:', len(content_loader._questions), 'Past Papers:', len(content_loader._past_papers))"
```

---

## 13. Developer & AI Agent Pair-Programming Manual

ส่วนนี้เขียนขึ้นเป็นข้อกำหนดและแนวทางปฏิบัติสำหรับ **AI Agent (เช่น Claude, ChatGPT, Gemini)** หรือนักพัฒนาที่มารับช่วงต่อโปรเจกต์:

### 13.1 กฎเหล็กที่ห้ามละเมิดเด็ดขาด (Invariant Rules)
1. **ห้ามใช้ Placeholder หลอกในข้อสอบ:** ห้ามใส่ตัวเลือกประเภท `"ตัวเลือก 1"`, `"ตัวเลือก 2"` หรือข้อความร่าง เช่น `"รอสักครู่"`, `"ไม่แน่ใจ"` ในไฟล์ข้อสอบ ทุกตัวเลือกต้องเป็นเนื้อหาจริงที่มีตัวลวงชัดเจน
2. **ตัวลวงต้องมี `error_tag` และเหตุผล:** สำหรับข้อสอบในชุด Blueprint ตัวเลือกที่ผิด (`correct: false`) ทุกตัวเลือกต้องระบุ `error_tag` และ `explanation` เพื่อให้ระบบวินิจฉัยจุดอ่อนได้
3. **ความถูกต้องทางคณิตศาสตร์และวิทยาศาสตร์:** เมื่อสร้างโจทย์คำนวณ ต้องตรวจสอบสมดุลหน่วย ตัวแปร และทิศทางเวกเตอร์ให้ถูกต้อง 100% ทุกข้อ
4. **ความเข้ากันได้กับ Pydantic Schema:** เมื่อเพิ่มข้อสอบใหม่ใน `content/` ต้องแน่ใจว่าโหลดผ่าน `content_loader.reload()` โดยไม่มี `ValidationError`
5. **ห้ามแก้ไฟล์ข้อสอบจำลองระหว่างการรันเทส:** ระวังการรันเทสบางตัวที่อาจเขียนไฟล์ชั่วคราวลงใน `content/imported/custom_questions.yaml` ให้ตรวจสอบ `git status` และ Restore กลับทุกครั้ง

### 13.2 ขั้นตอนการเพิ่มข้อสอบใหม่เข้าสู่ระบบ (How to Add Questions)
1. ระบุวิชาให้ถูกต้อง (`physics`, `math`, `tpat3`, `tgat1`, `tgat2`, `tgat3`)
2. สร้างหรือแก้ไขไฟล์ YAML ในโฟลเดอร์ `content/{subject}/` หรือ `content/past_papers/`
3. กำหนดโครงสร้างข้อสอบตามตัวอย่างใน [หัวข้อที่ 5](#5-data-models--yaml-schemas)
4. เลือกรหัสความผิดพลาด (`error_tag`) ให้สอดคล้องกับ [อนุกรมวิธานในหัวข้อที่ 6.3](#63-อนุกรมวิธานแท็กจุดผิด-error-tag-taxonomy)
5. รันคำสั่ง `py -m pytest` เพื่อรับรองว่าข้อสอบใหม่ไม่ทำให้การทดสอบระบบล้มเหลว

---

## 14. Quick Start & Execution

### วิธีเปิดใช้งานระบบบน Windows (Local Machine):
1. **ผ่าน Batch File:** ดับเบิลคลิกที่ไฟล์:
   ```cmd
   run.bat
   ```
2. **ผ่าน Terminal / PowerShell:**
   ```powershell
   # ติดตั้งโมดูลที่จำเป็น
   pip install -r requirements.txt

   # รันเซิร์ฟเวอร์
   py -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
3. เปิดเบราว์เซอร์ไปที่: **`http://127.0.0.1:8000`**

---
*เอกสารนี้ได้รับการปรับปรุงและตรวจสอบความสอดคล้องกับซอร์สโค้ดล่าสุด (`dd5814c`) เรียบร้อยแล้ว*
