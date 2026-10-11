# 📚 เอกสารสรุปและวิเคราะห์สถาปัตยกรรมระบบโดยละเอียด (TCAS Mastery Prep System: Master Review Dossier)

> **เอกสารฉบับสมบูรณ์ (Comprehensive Technical Dossier):**  
> จัดทำขึ้นเพื่อให้ผู้ประเมินภายนอก (Claude / AI Technical Reviewer / Senior Software Engineer) สามารถอ่าน เข้าใจสถาปัตยกรรมทุกส่วนของระบบ ตรวจสอบความถูกต้องของตรรกะ (Logic Verification) ประเมินความมั่นคงปลอดภัย (Security) และแนะนำแนวทางการต่อยอดได้อย่างครบถ้วนและแม่นยำที่สุดโดยไม่ต้องเปิดโค้ดดูทีละไฟล์
>
> **เวอร์ชันระบบ:** 1.2.0 (Post-Audit Hardened Edition)  
> **สแต็กเทคโนโลยี:** Python 3.13 + FastAPI + SQLite (WAL Mode) + Pydantic v2 + PyYAML + PyMuPDF + Vanilla JS + Bundled Local KaTeX  
> **สถานะการทดสอบอัตโนมัติ:** ผ่านการรัน `pytest` ทั้งหมด **53/53 Tests (100% Pass)**  
> **วันที่จัดทำเอกสาร:** 11 ตุลาคม 2026

---

## สารบัญ (Table of Contents)

1. [ปรัชญาและวัตถุประสงค์หลักของระบบ (Core Philosophy & System Mission)](#1-ปรัชญาและวัตถุประสงค์หลักของระบบ-core-philosophy--system-mission)
2. [สถาปัตยกรรมระบบและโครงสร้างไฟล์ทั้งหมด (Complete Architecture & Directory Tree)](#2-สถาปัตยกรรมระบบและโครงสร้างไฟล์ทั้งหมด-complete-architecture--directory-tree)
3. [แบบจำลองข้อมูลและ Schema มาตรฐาน (Data Models & Validation Schemas)](#3-แบบจำลองข้อมูลและ-schema-มาตรฐาน-data-models--validation-schemas)
4. [โครงสร้างฐานข้อมูล SQLite และการจัดการความปลอดภัย (Database Architecture & DDL)](#4-โครงสร้างฐานข้อมูล-sqlite-และการจัดการความปลอดภัย-database-architecture--ddl)
5. [เจาะลึกตรรกะของเครื่องยนต์หลัก (Core Engines & Service Implementations)](#5-เจาะลึกตรรกะของเครื่องยนต์หลัก-core-engines--service-implementations)
   - 5.1 Grader Engine & Numeric Normalizer (`grader.py`)
   - 5.2 Infinite Procedural Mental Math Drill Engine (`procedural_gen.py`)
   - 5.3 Spaced Repetition & Misconception Review Engine (`review_engine.py`)
   - 5.4 Paper Mock Exam Grader (`answer_sheet.py`)
   - 5.5 PDF & Social Media Exam Import Studio (`pdf_importer.py`)
   - 5.6 Custom Study Roadmap & Priority Management (`roadmap_service.py`)
   - 5.7 Contextual AI Helper & Pre-solve Guidance (`ai_helper.py`)
   - 5.8 Database Safety, VACUUM INTO Backup & Integrity (`backup_service.py`)
   - 5.9 Content Repository Singleton & Validation (`content_loader.py`)
6. [เส้นทางเครือข่ายและ API Endpoints ทั้งหมด (Complete API & Route Catalog)](#6-เส้นทางเครือข่ายและ-api-endpoints-ทั้งหมด-complete-api--route-catalog)
7. [การออกแบบฝั่งผู้ใช้และประสบการณ์ผู้เรียน (Frontend UI, Offline KaTeX & Interactivity)](#7-การออกแบบฝั่งผู้ใช้และประสบการณ์ผู้เรียน-frontend-ui-offline-katex--interactivity)
8. [คลังเนื้อหาข้อสอบและการรับรองคุณภาพ (Question Bank & Verification Tiers)](#8-คลังเนื้อหาข้อสอบและการรับรองคุณภาพ-question-bank--verification-tiers)
9. [ชุดทดสอบอัตโนมัติและระดับการตรวจสอบทางคณิตศาสตร์ (Automated Test Suite & Math Assertions)](#9-ชุดทดสอบอัตโนมัติและระดับการตรวจสอบทางคณิตศาสตร์-automated-test-suite--math-assertions)
10. [ประวัติการชำแหละโค้ดเบสและการแก้ไขช่องโหว่ (Brutal Codebase Roast & Remediations)](#10-ประวัติการชำแหละโค้ดเบสและการแก้ไขช่องโหว่-brutal-codebase-roast--remediations)
11. [คู่มือการติดตั้งและรันระบบ (Setup & Execution Guide)](#11-คู่มือการติดตั้งและรันระบบ-setup--execution-guide)
12. [ประเด็นแนะนำสำหรับการรีวิวโดย Claude (Key Review Prompts & Questions for Claude)](#12-ประเด็นแนะนำสำหรับการรีวิวโดย-claude-key-review-prompts--questions-for-claude)

---

## 1. ปรัชญาและวัตถุประสงค์หลักของระบบ (Core Philosophy & System Mission)

ระบบฝึกทำข้อสอบ TCAS นี้ (เน้นวิชา **ฟิสิกส์ประยุกต์, คณิตประยุกต์ 1, TPAT3 ความถนัดด้านวิทยาศาสตร์และเทคโนโลยี/วิศวกรรม, และ TGAT2 การคิดอย่างมีเหตุผล**) ถูกสร้างขึ้นภายใต้หลักคิดทางวิศวกรรมการเรียนรู้ (Learning Engineering) ที่เข้มงวด 6 ประการ:

1. **Local-First & 100% Offline Resilience (ทำงานในเครื่อง 100% ไม่พึ่งอินเทอร์เน็ต):**
   - ผู้เรียนสามารถรันเซิร์ฟเวอร์บนเครื่องตนเอง (`127.0.0.1:8000`) ใช้งานได้ลื่นไหลบนคอมพิวเตอร์พกพาหรือแท็บเล็ตในวง LAN เดียวกัน
   - ทรัพยากรทั้งหมด เช่น KaTeX JavaScript, CSS, Font WOFF2 ถูกดาวน์โหลดและ Bundle ไว้ในเครื่อง ไม่มีการเรียก External CDN ใดๆ เมื่อไม่มีเน็ต ระบบยังเรนเดอร์สมการคณิตศาสตร์และทำงานได้ 100%
   - ข้อมูลการเรียน บันทึกคะแนน สถิติจุดอ่อนทั้งหมดถูกเก็บในเครื่องส่วนตัว (SQLite) ไม่มีการส่งข้อมูลส่วนบุคคลออกสู่ภายนอก
2. **Deterministic Grading (ตรวจคำตอบโดยไม่อาศัย AI):**
   - การตรวจถูก/ผิดใช้ตรรกะที่แน่นอน 100% (Mathematical Rules, Choice Matching, Normalization, Tolerance Bounds)
   - **ห้ามใช้ AI LLM มาตัดสินการให้คะแนน** เพื่อตัดปัญหา AI หลอน (Hallucination), การสุ่มตรวจไม่สม่ำเสมอ, หรือความล่าช้าของ Network Latency
   - AI ถูกจำกัดบทบาทเป็นเพียง "ผู้ช่วยอธิบายและให้คำใบ้ (Tutor/Explainer)" เท่านั้น
3. **Honest Mastery Separation (การวัดผลความเชี่ยวชาญอย่างตรงไปตรงมา):**
   - ระบบแยกสถานะการตอบข้อสอบเป็น 3 ระดับอย่างโปร่งใส:
     - `correct_first_try`: ทำถูกได้เองตั้งแต่รอบแรกโดยไม่เปิดคำใบ้ (ถือเป็น Honest Mastery แท้จริง)
     - `correct_assisted`: ตอบถูกแต่มีการเปิดคำใบ้ (1-3 ระดับ) ช่วยเหลือระหว่างทำ
     - `wrong`: ตอบผิด
   - ไม่อนุญาตให้นำข้อที่ทำถูกหลังเปิดเฉลยมาเคลมว่าเชี่ยวชาญแล้วในสถิติหลัก
4. **Root-Cause Diagnosis (เจาะลึกสมมติฐานความผิดพลาด ไม่ใช่แค่บอกว่าผิด):**
   - ไม่ปล่อยให้นักเรียนคาดเดาเอาเองว่าผิดเพราะอะไร โดยระบบนำร่อง 3 ขั้นตอน:
     - **Plan Step (เลือกสูตรก่อนทำ):** บังคับเลือกสมการ/หลักการที่ถูกต้องก่อนแทนค่า เพื่อตรวจจับอาการ "ใช้สูตรผิดเงื่อนไข"
     - **Checkpoints (จุดตรวจระหว่างทาง):** ตรวจการแปลงหน่วยและค่าตัวแปรในขั้นกลาง
     - **Error-Tagged Distractors (ช้อยส์ดักจุดพลาด):** ช้อยส์ลวงแต่ละข้อจะผูกกับแท็ก เช่น `no_unit_conversion` (ลืมแปลง km/h เป็น m/s), `missing_factor_2` (ลืมเลข 2 ในสูตร), `sign_error` (เครื่องหมายเวกเตอร์ผิด)
5. **Active Formula Recall & Infinite Procedural Drills:**
   - การทำโจทย์ TCAS มักสะดุดที่ 2 เรื่อง: จำสูตรไม่ได้/ใช้ผิดเงื่อนไข และคิดเลขช้า
   - ระบบจึงแยกโหมด **Active Formula Recall** (ทดสอบเงื่อนไขการใช้สูตร หน่วย SI และตัวแปร) และ **Infinite Procedural Calculation Drills** (สุ่มโจทย์ฝึกคิดเลขในใจไม่จำกัด ด้วยตัวเลขที่คำนวณมือลงตัว)
6. **Future-Proof Extensibility (รองรับการขยายเนื้อหาในอนาคต):**
   - มี **PDF & Image Import Studio** รองรับการนำเข้าข้อสอบจากไฟล์ PDF (เช่น ชีตแจกใน IG, Facebook) ตัดหน้าเป็นภาพความละเอียดสูง ดึงข้อความ และสร้างเป็นข้อสอบเข้าคลังได้ทันที
   - มี **Custom Study Roadmap Manager** ปรับเปลี่ยนลำดับบทที่ต้องการอ่านก่อน-หลัง (Priority 1, 2, 3), เพิ่มบทเรียนใหม่ได้เอง และคำนวณเวลานับถอยหลังสู่วันสอบ TCAS จริงแบบเรียลไทม์

---

## 2. สถาปัตยกรรมระบบและโครงสร้างไฟล์ทั้งหมด (Complete Architecture & Directory Tree)

### 2.1 แผนผังสถาปัตยกรรมระบบ (System Architecture Diagram)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Client Browser (Desktop / Mobile)                  │
│   Vanilla JS (app.js) • Local Bundled KaTeX (0.16.8) • Sarabun Fonts    │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ HTTP Requests / JSON APIs
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     FastAPI Web Application (Uvicorn)                   │
├─────────────────────────────────────────────────────────────────────────┤
│ Routers:                                                                │
│  ├─ practice.py      : ทำโจทย์หลัก, ส่งคำตอบ, ระบบ Bookmark, ขอ Prompt AI │
│  ├─ drills.py        : แบบฝึกคำนวณสุ่มตัวเลขคิดในใจ (Procedural Drills)  │
│  ├─ formulas.py      : บัตรเรียกคืนสูตรฟิสิกส์ (Active Recall)          │
│  ├─ answer_sheet.py  : โหมดกระดาษคำตอบข้อสอบจำลอง A-Level               │
│  ├─ stats.py         : หน้าวิเคราะห์จุดอ่อน สถิติความเชี่ยวชาญ คิวทบทวน  │
│  ├─ system.py        : ระบบสำรองฐานข้อมูล VACUUM INTO, ตรวจ Integrity   │
│  ├─ import_studio.py : สตูดิโอนำเข้าข้อสอบจาก PDF/รูปภาพโซเชียล         │
│  └─ roadmap.py       : แผนการอ่าน, จัดลำดับบทเรียน, นับถอยหลังวันสอบ    │
├─────────────────────────────────────────────────────────────────────────┤
│ Core Services & Engines:                                                │
│  ├─ grader.py        : ตัวตรวจ Deterministic (MCQ, Numeric, Tolerance)   │
│  ├─ procedural_gen.py: เครื่องยนต์สุ่มโจทย์คำนวณคิดในใจลงตัว           │
│  ├─ review_engine.py : Spaced Repetition (Leitner/SM) + Misconceptions │
│  ├─ answer_sheet.py  : ตัวประมวลผลกระดาษคำตอบและวิเคราะห์รายบท          │
│  ├─ backup_service.py: SQLite VACUUM INTO snapshotter + Integrity Check │
│  ├─ ai_helper.py     : ตัวสร้าง Prompt บริบทถาม AI (0-Cost Context)    │
│  ├─ pdf_importer.py  : PyMuPDF แปลง PDF สู่ภาพ PNG + Text Extraction    │
│  ├─ roadmap_service.py: ตรรกะ Roadmap, คำนวณวันสอบ, จัดลำดับบทเรียน     │
│  └─ content_loader.py: YAML Repository Singleton + Schema Validator     │
└───────────────────┬─────────────────────────────────┬───────────────────┘
                    │                                 │
                    ▼                                 ▼
┌───────────────────────────────────────┐ ┌───────────────────────────────┐
│          SQLite3 Database             │ │      File System Content      │
│   (WAL Mode + Foreign Keys ON)        │ │  (YAML Question & Paper Bank) │
│  - attempts                           │ │  - content/physics/*.yaml     │
│  - review_queue                       │ │  - content/math/*.yaml        │
│  - procedural_attempts                │ │  - content/tpat3/*.yaml       │
│  - formula_reviews                    │ │  - content/formulas/*.yaml    │
│  - answer_sheet_submissions           │ │  - content/past_papers/*.yaml │
│  - bookmarks                          │ │  - content/imported/*.yaml    │
│  - topic_priorities                   │ │  - data/assets/pages/*.png    │
│  - imported_files                     │ │  - data/backups/*.db          │
│  - app_settings                       │ └───────────────────────────────┘
└───────────────────────────────────────┘
```

### 2.2 โครงสร้างไฟล์ทั้งหมดของโปรเจกต์ (Full Codebase Directory Tree)

```
C:\Users\pqx12\Desktop\tcas\
├── run.bat                                # สคริปต์รันเซิร์ฟเวอร์แบบ 1 คลิกสำหรับ Windows
├── requirements.txt                       # รายการ Dependencies (FastAPI, PyMuPDF, etc.)
├── README.md                              # คู่มือภาษาไทยสำหรับผู้ใช้งานทั่วไป
├── unified_tcas_plan.md                   # แผนแม่บทฉบับบูรณาการที่เสร็จสมบูรณ์ 100%
├── codebase_roast_and_audit.md            # บันทึกการชำแหละโค้ดเบสและแก้ไขจุดบกพร่อง
├── tcas_master_review_dossier.md          # เอกสารสรุปเชิงสถาปัตยกรรมฉบับนี้
├── app/
│   ├── __init__.py
│   ├── main.py                            # FastAPI App, Lifespan Handler, Static Mounts
│   ├── config.py                          # พาธระบบ, พอร์ต, การตั้งค่าสภาพแวดล้อม
│   ├── database.py                        # SQLite Connection Manager, WAL Setup, DDL
│   ├── models/
│   │   ├── __init__.py
│   │   ├── content_schema.py              # Pydantic Schemas สำหรับข้อสอบ บัตรสูตร ข้อสอบเก่า
│   │   └── api_schema.py                  # Pydantic Schemas สำหรับ Request/Response API
│   ├── services/
│   │   ├── __init__.py
│   │   ├── grader.py                      # ตรวจคำตอบ (MCQ, Numeric, Units, Tolerance)
│   │   ├── procedural_gen.py              # ตัวสร้างโจทย์สุ่มตัวเลขคิดในใจได้
│   │   ├── review_engine.py               # Spaced Repetition, คิวทบทวน, วิเคราะห์จุดอ่อน
│   │   ├── answer_sheet.py                # ตรวจกระดาษคำตอบข้อสอบจำลอง
│   │   ├── backup_service.py              # SQLite VACUUM INTO, ตรวจ Integrity, ลบ Backup
│   │   ├── ai_helper.py                   # ตัวสร้าง AI Prompt บริบท และ Pre-solve Hint
│   │   ├── pdf_importer.py                # PyMuPDF ตัดหน้า PDF เป็นรูปภาพ ดึงข้อความ
│   │   ├── roadmap_service.py             # แผน Roadmap, ลำดับบท, วันสอบ TCAS
│   │   └── content_loader.py              # Singleton โหลดและตรวจสอบไฟล์ YAML ทั้งหมด
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── practice.py                    # /practice, /api/submit-attempt, /api/bookmark
│   │   ├── drills.py                      # /drills, /api/drills/new, /api/drills/submit
│   │   ├── formulas.py                    # /formulas, /api/formulas/submit
│   │   ├── answer_sheet.py                # /answer-sheet, /api/answer-sheet/submit
│   │   ├── stats.py                       # /stats, /api/stats
│   │   ├── system.py                      # /system, /api/backup/*, /api/system/integrity
│   │   ├── import_studio.py               # /import, /api/import/upload, /api/import/create-question
│   │   └── roadmap.py                     # /roadmap, /api/roadmap/*
│   ├── templates/                         # Jinja2 HTML Templates
│   │   ├── base.html                      # Layout หลัก, Local KaTeX, Navbar, Toast
│   │   ├── dashboard.html                 # หน้าแรก สรุปภาพรวม คิวทบทวน สถิติเร็ว
│   │   ├── practice_list.html             # หน้ารายการโจทย์ กรองรายวิชา และข้อติดดาว
│   │   ├── practice.html                  # หน้าทำโจทย์ (Plan Step, Checkpoints, Image, AI)
│   │   ├── procedural_drill.html          # หน้าฝึกคิดเลขสุ่มโจทย์ 4 หมวด
│   │   ├── formula_recall.html            # หน้าบัตรสูตรและทดสอบความจำ (Anti-spam)
│   │   ├── answer_sheet_list.html         # หน้ารายการชุดข้อสอบจำลอง
│   │   ├── answer_sheet.html              # หน้ากระดาษคำตอบจับเวลาพร้อมตรวจรายบท
│   │   ├── import_studio.html             # สตูดิโอนำเข้า PDF/รูปภาพสองหน้าต่าง
│   │   ├── roadmap.html                   # แผนการอ่าน จัดลำดับบท ตั้งค่าวันสอบ
│   │   ├── stats.html                     # หน้ารายงานสถิติจุดอ่อนและผลฝึกคิดเลข
│   │   └── system.html                    # หน้าสำรองข้อมูล ตรวจสอบสุขภาพ DB
│   └── static/
│       ├── css/
│       │   └── style.css                  # Custom Responsive CSS (ระบบสี, Layout, Typography)
│       ├── js/
│       │   └── app.js                     # Toast, Copy Clipboard, Timer, Accordion, Math Renderer
│       └── vendor/
│           └── katex/                     # Bundled Local KaTeX 0.16.8
│               ├── katex.min.css
│               ├── katex.min.js
│               ├── auto-render.min.js
│               └── fonts/                 # 20 KaTeX WOFF2 font files สำหรับออฟไลน์สมบูรณ์
├── content/                               # คลังโจทย์และเนื้อหาแบบ YAML
│   ├── physics/
│   │   ├── kinematics_1d.yaml             # ฟิสิกส์: การเคลื่อนที่แนวตรง (Level B Verified)
│   │   └── forces_energy.yaml             # ฟิสิกส์: กฎนิวตันและงานพลังงาน (Level B Verified)
│   ├── math/
│   │   └── functions_algebra.yaml         # คณิตประยุกต์ 1: อสมการและฟังก์ชันเอกซ์โพเนนเชียล
│   ├── tpat3/
│   │   └── quantitative.yaml              # TPAT3: อัตราทดเฟืองและความถนัดเชิงกล
│   ├── formulas/
│   │   └── physics_formulas.yaml          # บัตรสูตรฟิสิกส์และการทดสอบเงื่อนไข
│   ├── past_papers/
│   │   └── alevel_phy_sample.yaml         # ข้อสอบจำลอง A-Level ฟิสิกส์ 20 ข้อ
│   └── imported/
│       └── custom_questions.yaml          # ข้อสอบที่ผู้ใช้นำเข้าผ่าน Import Studio
├── data/                                  # จุดจัดเก็บข้อมูล Dynamic Runtime
│   ├── tcas.db                            # SQLite Database หลัก (WAL Mode)
│   ├── assets/pages/                      # รูปภาพหน้าข้อสอบที่แปลงจาก PDF (.png)
│   ├── sources/                           # ไฟล์ PDF ต้นฉบับที่อัปโหลด
│   └── backups/                           # ไฟล์ SQLite Snapshot (.db) จากคำสั่ง VACUUM INTO
└── tests/                                 # ชุดทดสอบอัตโนมัติ (pytest) 53 ข้อ
    ├── test_backup.py                     # ตรวจสอบการทำ Backup VACUUM INTO และ Integrity
    ├── test_content_schema.py             # ตรวจสอบความถูกต้องของโครงสร้าง YAML ทุกไฟล์
    ├── test_grader.py                     # ตรวจสอบ Normalizer, Unicode, Tolerance, Error Tags
    ├── test_physics_answers.py            # Level B Assertion: คำนวณคณิตศาสตร์ตรวจโจทย์ทุกข้อ
    ├── test_procedural_gen.py             # ตรวจสอบการสุ่มตัวเลขคิดในใจได้
    ├── test_review_engine.py              # ตรวจสอบ Spaced Repetition, Misconceptions, Analytics
    ├── test_routes.py                     # ตรวจสอบ Endpoints ทั้งหมดคืนค่า HTTP 200/ถูกต้อง
    ├── test_pdf_and_roadmap.py            # ตรวจสอบ PDF Importer และ Roadmap Priority
    └── test_audit_fixes.py                # ตรวจสอบจุดแก้ไขจากการ Roast (KaTeX, Units, Bookmarks, etc.)
```

---

## 3. แบบจำลองข้อมูลและ Schema มาตรฐาน (Data Models & Validation Schemas)

ทุกข้อมูลในระบบได้รับการควบคุมโครงสร้างอย่างเข้มงวดด้วย **Pydantic v2** ใน [app/models/content_schema.py](file:///C:/Users/pqx12/Desktop/tcas/app/models/content_schema.py):

### 3.1 โครงสร้างข้อสอบ (Question Schema)

```python
class Question(BaseModel):
    id: str                               # เช่น 'phy-kin-0001'
    subject: str                          # 'physics', 'math', 'tpat3', 'tgat2'
    topic: str                            # เช่น 'physics.kinematics.1d'
    source: SourceInfo                    # type (official/textbook/invented/exam_prep), label, exam_year
    verification: VerificationInfo        # tier ('A' | 'B' | 'C' | 'D' | 'E'), verified_by, notes
    skills: SkillInfo                     # primary skill, secondary skills list
    stem: str                             # ข้อความโจทย์ (รองรับ LaTeX $...$)
    image_url: str | None = None          # URL รูปภาพประกอบ (แสดงทั้งโจทย์ในคลังและโจทย์ที่นำเข้า)
    plan_step: PlanStep | None = None     # คำถามเลือกสูตร/หลักการก่อนคำนวณ
    checkpoints: list[Checkpoint] | None = None # จุดตรวจตัวแปร/แปลงหน่วยระหว่างทาง
    answer: AnswerConfig                  # ชนิดคำตอบ (single_choice หรือ numeric), ตัวเลือก, ค่าที่ถูกต้อง
    hints: list[Hint] = Field(default_factory=list) # คำใบ้ 3 ระดับ
    solution: FullSolution | None = None  # เฉลยละเอียดเป็นขั้นตอน, สรุป, จุดระวัง, Sanity check
```

#### ระดับการตรวจสอบคุณภาพโจทย์ (Verification Tiers A–E):
* **Tier A:** ตรงกับข้อสอบจริงและเฉลยทางการของ ทปอ. (MyTCAS)
* **Tier B:** ผ่านการตรวจสอบความถูกต้องด้วยโค้ดคำนวณอัตโนมัติ (Python assertion) โดยการแทนค่าตัวเลขจริง
* **Tier C:** ครูหรือติวเตอร์ผู้เชี่ยวชาญตรวจสอบความถูกต้อง
* **Tier D:** AI 2 ตัวประมวลผลตรงกัน + ผู้เรียนตรวจสอบด้วยตนเอง
* **Tier E:** ยังไม่ผ่านการตรวจสอบ (โจทย์ร่าง)

#### ตัวเลือกที่ผูกกับแท็กวินิจฉัยความผิดพลาด (ChoiceOption with Error Tags):
```python
class ChoiceOption(BaseModel):
    id: str                               # 'o1', 'o2', 'o3', 'o4', 'o5'
    text: str                             # ข้อความช้อยส์ (เช่น "$20\\text{ m}$")
    correct: bool = False                 # ข้อถูกหรือไม่
    error_tag: str | None = None          # แท็กความผิดพลาดหากเลือกข้อนี้
    explanation: str | None = None        # คำอธิบายเจาะจงว่าเหตุใดจึงผิด
```

### 3.2 โครงสร้างบัตรสูตรฟิสิกส์ (FormulaCard Schema)

```python
class FormulaCard(BaseModel):
    id: str                               # เช่น 'phy-form-kin-01'
    subject: str                          # 'physics'
    topic: str                            # 'physics.kinematics.1d'
    title: str                            # เช่น '5 สูตรการเคลื่อนที่แนวตรง (ความเร่งคงตัว)'
    latex: str                            # เช่น 'v = u + at'
    conditions: list[str]                 # เงื่อนไขสำคัญ เช่น 'วัตถุต้องมีความเร่งคงตัว (a = constant)'
    variables: dict[str, str]             # ความหมายและหน่วย SI เช่น {'v': 'ความเร็วปลาย (m/s)', ...}
    selection_cues: list[str]             # ข้อสังเกตในการหยิบสูตรมาใช้
    recall_questions: list[dict[str, Any]] # คำถาม Active Recall เช็คความเข้าใจและตัวแปร
```

### 3.3 โครงสร้างข้อสอบจำลอง (PastPaper Schema)

```python
class PastPaperQuestion(BaseModel):
    number: int
    correct_answer: str                   # '1', '2', '3', '4', '5' หรือค่าตัวเลข เช่น '12.5'
    topic: str
    skill: str
    score: float = 1.0

class PastPaper(BaseModel):
    id: str                               # เช่น 'alevel-phy-sample-01'
    title: str
    subject: str
    year: int
    time_limit_min: int = 90
    questions: list[PastPaperQuestion]
```

---

## 4. โครงสร้างฐานข้อมูล SQLite และการจัดการความปลอดภัย (Database Architecture & DDL)

ฐานข้อมูลทำงานผ่าน SQLite 3 ที่ไฟล์ `data/tcas.db` โดยเปิดใช้งาน **WAL Mode (Write-Ahead Logging)** เพื่อให้สามารถอ่านและเขียนพร้อมกันได้โดยไม่เกิดปัญหา Lock บน Windows:

```sql
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;
```

### ตารางทั้งหมดในระบบ (Database DDL):

```sql
-- 1. ประวัติการทำโจทย์แต่ละครั้ง พร้อมข้อมูลเวลา ความมั่นใจ และการใช้คำใบ้
CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT NOT NULL,
    subject TEXT,
    topic TEXT,
    user_answer TEXT,
    is_correct INTEGER NOT NULL,
    status TEXT NOT NULL,          -- 'correct_first_try', 'correct_assisted', 'wrong'
    confidence TEXT,               -- 'sure', 'unsure', 'guessed'
    hints_opened INTEGER DEFAULT 0,
    plan_step_answer TEXT,
    plan_step_correct INTEGER,
    error_tag TEXT,
    time_spent_sec REAL DEFAULT 0.0,
    review_time_sec REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. คิวการทบทวนแบบ Spaced Repetition และข้อที่เข้าใจผิดรุนแรง (Misconceptions)
CREATE TABLE IF NOT EXISTS review_queue (
    question_id TEXT PRIMARY KEY,
    subject TEXT,
    topic TEXT,
    next_review_at TIMESTAMP,
    interval_days INTEGER DEFAULT 1,
    repetition_count INTEGER DEFAULT 0,
    priority TEXT DEFAULT 'normal', -- 'high' (มั่นใจแต่ตอบผิด), 'normal', 'low'
    last_status TEXT,
    last_error_tag TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. สถิติการฝึกคิดเลขเร็วในใจ (Infinite Procedural Drills)
CREATE TABLE IF NOT EXISTS procedural_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drill_type TEXT NOT NULL,      -- 'unit_kmh_ms', 'kinematics_5eq', 'area_volume', 'fractions_powers'
    question_stem TEXT NOT NULL,
    user_answer TEXT,
    expected_answer TEXT,
    is_correct INTEGER NOT NULL,
    time_spent_sec REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. สถิติการทดสอบดึงความจำบัตรสูตรฟิสิกส์ (Formula Active Recall)
CREATE TABLE IF NOT EXISTS formula_reviews (
    formula_id TEXT PRIMARY KEY,
    subject TEXT,
    correct_count INTEGER DEFAULT 0,
    wrong_count INTEGER DEFAULT 0,
    next_review_at TIMESTAMP,
    last_reviewed_at TIMESTAMP
);

-- 5. ประวัติการส่งกระดาษคำตอบข้อสอบจำลองจับเวลา (Mock Answer Sheets)
CREATE TABLE IF NOT EXISTS answer_sheet_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id TEXT NOT NULL,
    paper_title TEXT NOT NULL,
    total_questions INTEGER NOT NULL,
    correct_count INTEGER NOT NULL,
    score_percent REAL NOT NULL,
    answers_json TEXT NOT NULL,
    details_json TEXT NOT NULL,
    time_taken_min REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. ระบบบันทึกข้อสอบที่ผู้เรียนติดดาวไว้ทบทวน (Bookmarks)
CREATE TABLE IF NOT EXISTS bookmarks (
    question_id TEXT PRIMARY KEY,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. การตั้งค่าระบบ (เช่น วันสอบ TCAS จริง)
CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- 8. แผนการอ่านและจัดลำดับความสำคัญของบทเรียน (Custom Study Roadmap)
CREATE TABLE IF NOT EXISTS topic_priorities (
    topic_id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    topic_name TEXT NOT NULL,
    priority_level INTEGER DEFAULT 1, -- 1: สำคัญอันดับแรก, 2: ลำดับถัดไป, 3: อ่านเสริม
    target_score_pct REAL DEFAULT 80.0,
    notes TEXT DEFAULT '',
    order_index INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. ประวัติไฟล์ PDF และรูปภาพข้อสอบที่ผู้เรียนนำเข้า
CREATE TABLE IF NOT EXISTS imported_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    original_name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    page_count INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes สำหรับประสิทธิภาพการสืบค้น
CREATE INDEX IF NOT EXISTS idx_attempts_qid ON attempts(question_id);
CREATE INDEX IF NOT EXISTS idx_attempts_status ON attempts(status);
CREATE INDEX IF NOT EXISTS idx_review_next ON review_queue(next_review_at, priority);
CREATE INDEX IF NOT EXISTS idx_topic_prio ON topic_priorities(priority_level, order_index);
```

---

## 5. เจาะลึกตรรกะของเครื่องยนต์หลัก (Core Engines & Service Implementations)

### 5.1 Grader Engine & Numeric Normalizer ([grader.py](file:///C:/Users/pqx12/Desktop/tcas/app/services/grader.py))

ตัวตรวจคำตอบแบบ Deterministic ที่มีความยืดหยุ่นสูง เพื่อป้องกันการตรวจผิดจากความแตกต่างในการพิมพ์ของมนุษย์:

1. **Thai Numerals Translation:** แปลงเลขไทย (`๑๒๓๔๕๖๗๘๙๐`) เป็นอารบิก (`1234567890`)
2. **Unicode Minus Normalization:** แปลงเครื่องหมายลบ Unicode `−` (U+2212) และ En-dash `–` (U+2013) เป็นเครื่องหมายลบ ASCII `-`
3. **Thousands Comma & Whitespace Stripping:** ตัดจุลภาคคั่นหลักพัน (`1,000` ➔ `1000`) และช่องว่างภายใน
4. **Physical Units Stripping:** ตัดหน่วยฟิสิกส์ที่ผู้เรียนอาจเผลอพิมพ์ต่อท้ายตัวเลข เช่น `20 m/s`, `5.0 N`, `100 J`, `15 km/h` ออกอัตโนมัติ โดยไม่ไปทำลายสัญกรณ์วิทยาศาสตร์ (`e3`, `e-2`)
5. **Scientific Notation Parsing:** แปลงสัญกรณ์หลากหลายรูปแบบ (`2e3`, `2*10^3`, `2x10^3`, `2×10^3`) สู่ค่า float
6. **Fractional Value Evaluation:** คำนวณเศษส่วน (`3/4` ➔ `0.75`, `-1/2` ➔ `-0.5`)
7. **Tolerance Grading:** กำหนด Relative Tolerance $\le 2\%$ หรือ Absolute Error $< 10^{-4}$ เพื่อรองรับความคลาดเคลื่อนจากการปัดเศษทศนิยม
8. **Root-Cause Error Diagnostics:** เมื่อตอบผิดในข้อปรนัย ระบบจะดึง `error_tag` และแปลความหมายเป็นภาษาไทยทันทีจาก `ERROR_TAG_DESCRIPTIONS` เช่น:
   - `no_unit_conversion`: *"ลืมแปลงหน่วย (เช่น ไม่ได้แปลง km/h เป็น m/s)"*
   - `missing_factor_2`: *"ลืมตัวคูณ 2 หรือ 1/2 ในสมการ"*
   - `sign_error`: *"เครื่องหมายเวกเตอร์หรือทิศทางผิด"*
   - `intermediate_stage_only`: *"ตอบเฉพาะผลลัพธ์ของขั้นกลาง ยังไม่ได้คิดต่อจนถึงขั้นสุดท้าย"*

### 5.2 Infinite Procedural Mental Math Drill Engine ([procedural_gen.py](file:///C:/Users/pqx12/Desktop/tcas/app/services/procedural_gen.py))

ระบบสร้างโจทย์คำนวณสุ่มตัวเลขแบบไม่จำกัด ไม่พึ่งพา AI แต่รับประกันว่าตัวเลขทุกข้อถูกออกแบบให้ **คิดเลขในใจหรือทดมือได้ลงตัว**:

* **Drill 1: แปลงหน่วยความเร็ว ($km/h \leftrightarrow m/s$):** สุ่มตัวเลขที่เป็นพหุคูณของ 18 หรือ 3.6 (เช่น $36, 54, 72, 90, 108\text{ km/h}$) เพื่อให้นักเรียนตัดทอนด้วย $\frac{5}{18}$ หรือ $\frac{18}{5}$ ได้อย่างรวดเร็ว
* **Drill 2: แปลงหน่วยพื้นที่ ปริมาตร ความหนาแน่น:** $cm^2 \leftrightarrow m^2$ ($10^{-4}$), $g/cm^3 \leftrightarrow kg/m^3$ ($\times 1000$), ลิตร $\leftrightarrow m^3$
* **Drill 3: 5 สูตรการเคลื่อนที่แนวตรง:** สุ่มตัวแปร 3 ตัว หาตัวที่ 4 ในสถานการณ์ออกตัว ($u=0$), ระยะเบรกจนหยุด ($v=0$), และการโยนดิ่งถึงจุดสูงสุด ($v=0, g=10$) ตัวเลขคำนวณแล้วถอดสแควร์รูทลงตัวเสมอ
* **Drill 4: สัดส่วนและเลขยกกำลังในฟิสิกส์:** การเปรียบเทียบอัตราส่วนพลังงานจลน์ ($E_k \propto mv^2$), อัตราส่วนความต้านทานลวดตัวนำ ($R \propto \frac{1}{r^2}$), และแรงดึงดูดระหว่างมวล ($F \propto \frac{1}{R^2}$)

### 5.3 Spaced Repetition & Misconception Review Engine ([review_engine.py](file:///C:/Users/pqx12/Desktop/tcas/app/services/review_engine.py))

ตรรกะจัดคิวทบทวนตามหลักการกระจายเวลา (Spaced Repetition: 1 วัน, 3 วัน, 7 วัน, 14 วัน, 30 วัน) ผสานกับการตรวจจับความเข้าใจผิด (Misconception Detection):

1. **กรณีตอบผิด หรือตอบถูกหลังเปิดคำใบ้ (`correct_assisted`):**
   - รีเซ็ตช่วงเวลาทบทวนกลับมาเป็น **1 วัน** เสมอ เพื่อประเมินซ้ำว่าทำได้เองจริงหรือไม่
2. **กรณีมั่นใจมากแต่ตอบผิด (`confidence == 'sure'` และ `is_correct == False`):**
   - จัดเป็น **Severe Misconception (ความเข้าใจผิดรุนแรง)** กำหนดลำดับความสำคัญในคิวเป็น **High Priority** และลอยขึ้นมาให้ทบทวนเป็นอันดับแรกในหน้า Dashboard
3. **กรณีตอบถูกเองตั้งแต่แรก (`correct_first_try`):**
   - ถ้าเดา (`guessed`): ทบทวนใน 1 วัน
   - ถ้าไม่แน่ใจ (`unsure`): คงช่วงเวลาเดิมไว้
   - ถ้ามั่นใจ (`sure`): เลื่อนระดับขั้นถัดไปตามลำดับ `[1, 3, 7, 14, 30]` วัน
4. **ความแม่นยำของเวลา:** ใช้รูปแบบวันที่ `YYYY-MM-DD HH:MM:SS` สอดคล้องกับ SQLite Native Timestamp ทำให้การเปรียบเทียบเงื่อนไข `next_review_at <= ?` เที่ยงตรง 100%

### 5.4 Paper Mock Exam Grader ([answer_sheet.py](file:///C:/Users/pqx12/Desktop/tcas/app/services/answer_sheet.py))

* จำลองการทำข้อสอบเก่าจริงบนกระดาษจับเวลา 90 นาที แล้วนำคำตอบมากรอกในเว็บ
* ตรวจคำตอบผสมผสานระหว่างตัวเลือกปรนัย (`1-5`) และตัวเลขอัตนัยเติมคำ
* ใช้ `grade_numeric` ร่วมด้วย ทำให้การกรอกตัวเลขที่มีทศนิยมเหลื่อมหลัก (เช่น `12.5` กับ `12.50`) หรือมีเครื่องหมายลบยูนิโค้ดได้รับการตรวจอย่างถูกต้อง
* คำนวณคะแนนรวม ร้อยละ และ **วิเคราะห์คะแนนแยกตามบทเรียน (Topic Breakdown)** เพื่อบอกทันทีว่าสอบครั้งนี้ตกบทไหนมากที่สุด

### 5.5 PDF & Social Media Exam Import Studio ([pdf_importer.py](file:///C:/Users/pqx12/Desktop/tcas/app/services/pdf_importer.py))

* ใช้ไลบรารี **PyMuPDF (`pymupdf`)** รับไฟล์ PDF ข้อสอบที่ผู้เรียนได้มาจาก Instagram / กลุ่มติว
* แปลงหน้า PDF แต่ละหน้าเป็นรูปภาพ PNG คมชัดความละเอียด 150 DPI บันทึกที่ `data/assets/pages/`
* ดึงข้อความ Text Streams จาก PDF (หากเป็นข้อสอบดิจิทัล) หรือระบุข้อความแนะนำผู้ใช้หากเป็นเอกสารสแกน
* หน้าเว็บมี Question Builder สองหน้าต่าง (ดูภาพต้นฉบับทางซ้าย กรอกช้อยส์และคำตอบทางขวา)
* เมื่อบันทึก ระบบจะแปลงเป็น `Question` Pydantic Model แล้ว Append ต่อท้ายไฟล์ `content/imported/custom_questions.yaml` และสั่ง `content_loader.reload()` ทันทีโดยไม่ต้องรีสตาร์ทเซิร์ฟเวอร์

### 5.6 Custom Study Roadmap & Priority Management ([roadmap_service.py](file:///C:/Users/pqx12/Desktop/tcas/app/services/roadmap_service.py))

* คำนวณเวลานับถอยหลังสู่วันสอบ TCAS จริง (แยก TGAT/TPAT3 ช่วงปลายปี/ม.ค. และ A-Level ช่วง มี.ค.)
* มีฟอร์มปรับเปลี่ยนวันสอบจริงของแต่ละปีการศึกษาได้จากหน้าเว็บ
* จัดหมวดหมู่บทเรียนตามระดับความสำคัญของผู้เรียน:
  - **ระดับ 1 (Priority 1):** สำคัญเร่งด่วน ต้องเก็บให้แม่นก่อนบทอื่น
  - **ระดับ 2 (Priority 2):** สำคัญปานกลาง ทยอยเก็บสะสม
  - **ระดับ 3 (Priority 3):** อ่านเสริมเพื่อเก็งคะแนนระดับสูง
* รองรับการกดเลื่อนสลับลำดับบทเรียนขึ้น-ลง (⬆️ / ⬇️) โดยระบบ **รักษาค่า `order_index` ไว้อย่างถูกต้อง** แม้จะมีการแก้ไขเป้าหมายคะแนน
* คำนวณ Honest Mastery เปรียบเทียบกับเป้าหมาย % ที่ผู้เรียนตั้งไว้ในแต่ละบท

### 5.7 Contextual AI Helper & Pre-solve Guidance ([ai_helper.py](file:///C:/Users/pqx12/Desktop/tcas/app/services/ai_helper.py))

* **One-Click Context Copy (ฟรี 100% ไม่เสียค่า API):**
  - รวม: ข้อความโจทย์, คำตอบที่ผู้เรียนเลือก, แท็กข้อผิดพลาดที่ตรวจพบ, เฉลยทางการ, และคำใบ้
  - จัดรูปแบบเป็น Prompt ภาษาไทยอย่างสุภาพสำหรับนำไปกดวางใน ChatGPT, Claude หรือ Gemini ได้ทันที
* **Pre-solve Hint Prompt (แนวคิดตั้งต้นโดยไม่สปอยล์คำตอบ):**
  - ออกแบบสำหรับนักเรียนที่อ่านโจทย์แล้วคิดไม่ออกตั้งแต่เริ่ม (Thinking Phase)
  - สร้าง Prompt ร้องขอให้ AI ช่วยสรุปสิ่งที่โจทย์ให้, สิ่งที่ต้องหา, และกรอบความคิดทางฟิสิกส์ **โดยสั่งห้าม AI เฉลยคำตอบสุดท้ายเด็ดขาด**
* **Direct Gemini Client (ทางเลือกเสริม):**
  - รองรับการยิง API ตรงไปยังโมเดล `gemini-2.5-flash` หากผู้ใช้ระบุ `GEMINI_API_KEY` ในเครื่อง

### 5.8 Database Safety, VACUUM INTO Backup & Integrity ([backup_service.py](file:///C:/Users/pqx12/Desktop/tcas/app/services/backup_service.py))

* สำรองข้อมูลแบบจุดเดียวจบด้วยเทคโนโลยี **SQLite `VACUUM INTO`**:
  - สร้างไฟล์ Snapshot ฐานข้อมูลที่สมบูรณ์ ณ เสี้ยววินาทีนั้น โดยไม่ล็อกตาราง และปลอดภัยแม้กำลังเขียนข้อมูลในโหมด WAL
  - ปลอดภัยจากการซิงก์ของ OneDrive หรือ Google Drive บนระบบปฏิบัติการ Windows
* ตรวจสอบความสมบูรณ์ของโครงสร้างด้วย `PRAGMA integrity_check` และ `PRAGMA foreign_key_check`
* มีระบบกำจัดไฟล์สำรองเก่าที่ไม่ต้องการ (`delete_backup`) พร้อมการตรวจสอบป้องกัน Path Traversal

### 5.9 Content Repository Singleton & Validation ([content_loader.py](file:///C:/Users/pqx12/Desktop/tcas/app/services/content_loader.py))

* Singleton ทำหน้าที่อ่านไฟล์ YAML ทั้งหมดใน `content/` (`physics/`, `math/`, `tpat3/`, `tgat2/`, `formulas/`, `past_papers/`, `imported/`)
* Parse ข้อมูลผ่าน Pydantic models หากมีฟิลด์ใดผิดประเภทหรือขาดหาย ระบบจะตรวจพบตั้งแต่ขั้นตอนบูตระบบ
* มีฟังก์ชัน `reload()` สำหรับโหลดไฟล์ใหม่เข้าหน่วยความจำทันทีหลังนำเข้าข้อสอบจาก PDF

---

## 6. เส้นทางเครือข่ายและ API Endpoints ทั้งหมด (Complete API & Route Catalog)

| Method | Endpoint Path | วัตถุประสงค์การทำงาน | Request Body / Params | Response Format |
| :---: | :--- | :--- | :--- | :--- |
| `GET` | `/` | หน้า Dashboard สรุปภาพรวมและคิวทบทวน | - | HTML (`dashboard.html`) |
| `GET` | `/practice` | คลังข้อสอบหลักพร้อมตัวกรอง | `subject`, `topic`, `bookmarked_only` | HTML (`practice_list.html`) |
| `GET` | `/practice/{question_id}` | หน้าทำโจทย์ข้อสอบแบบ Interactive | - | HTML (`practice.html`) |
| `POST` | `/api/submit-attempt` | ตรวจคำตอบโจทย์หลัก บันทึกสถิติ และจัดคิว | `SubmitAttemptRequest` (JSON) | JSON (`SubmitAttemptResponse` + `ai_prompt`) |
| `POST` | `/api/bookmark/toggle` | สลับสถานะติดดาวโจทย์ (Bookmark) | `{"question_id": str}` | `{"question_id": str, "bookmarked": bool}` |
| `GET` | `/api/ai-prompt/presolve/{id}` | ขอ Prompt แนวคิดเริ่มต้นจาก AI (ไม่เฉลย) | - | `{"prompt": str}` |
| `GET` | `/drills` | หน้าแบบฝึกคำนวณสุ่มตัวเลขคิดในใจ | `drill_type` | HTML (`procedural_drill.html`) |
| `GET` | `/api/drills/new` | สุ่มโจทย์คำนวณข้อใหม่ | `drill_type` | JSON (`stem`, `expected_answer`, `unit`, etc.) |
| `POST` | `/api/drills/submit` | ตรวจคำตอบคิดเลขเร็วและบันทึกลงตาราง | `ProceduralSubmitRequest` (JSON) | `{"is_correct": bool, "expected_answer": str}` |
| `GET` | `/formulas` | หน้าบัตรเรียกคืนสูตรฟิสิกส์ | - | HTML (`formula_recall.html`) |
| `POST` | `/api/formulas/submit` | ตรวจและบันทึกคะแนนบัตรสูตร (Anti-spam) | `FormulaRecallSubmitRequest` | `{"is_correct": bool, "correct_answer": str}` |
| `GET` | `/answer-sheet` | หน้ารายการชุดข้อสอบจำลอง | - | HTML (`answer_sheet_list.html`) |
| `GET` | `/answer-sheet/{paper_id}` | หน้ากระดาษคำตอบจับเวลา 90 นาที | - | HTML (`answer_sheet.html`) |
| `POST` | `/api/answer-sheet/submit` | ตรวจกระดาษคำตอบและวิเคราะห์รายบท | `AnswerSheetSubmitRequest` | JSON (`AnswerSheetSubmitResponse`) |
| `GET` | `/import` | สตูดิโอนำเข้าข้อสอบ PDF/รูปภาพ | - | HTML (`import_studio.html`) |
| `POST` | `/api/import/upload` | อัปโหลด PDF ตัดหน้าเป็น PNG ดึงข้อความ | `multipart/form-data` (`file`) | JSON (`file_id`, `pages`, `page_count`) |
| `POST` | `/api/import/create-question`| บันทึกข้อสอบที่ตัดเข้าสู่คลัง YAML | JSON (stem, options, image_url, etc.) | `{"success": true, "question_id": str}` |
| `GET` | `/roadmap` | แผนการอ่าน จัดลำดับบท นับถอยหลังวันสอบ | - | HTML (`roadmap.html`) |
| `POST` | `/api/roadmap/update-priority`| ปรับความสำคัญและเป้าหมายคะแนนรายบท | `UpdatePriorityRequest` | `{"success": true}` |
| `POST` | `/api/roadmap/add-topic` | เพิ่มบทเรียนใหม่เข้าสู่ Roadmap | `AddTopicRequest` | `{"success": true}` |
| `POST` | `/api/roadmap/reorder` | สลับลำดับบทเรียนขึ้นหรือลง (⬆️ / ⬇️) | `{"topic_id": str, "direction": "up"|"down"}` | `{"success": true}` |
| `POST` | `/api/roadmap/update-exam-dates`| ปรับตั้งค่าวันสอบ TGAT/TPAT และ A-Level | `{"tpat_date": str, "alevel_date": str}` | `{"success": true}` |
| `GET` | `/stats` | หน้าวิเคราะห์สถิติจุดอ่อนและผลการฝึก | - | HTML (`stats.html`) |
| `GET` | `/api/stats` | ดึงข้อมูลสถิติภาพรวมในรูปแบบ JSON | - | JSON (`get_learning_stats()`) |
| `GET` | `/system` | หน้าจัดการระบบและสำรองข้อมูล | - | HTML (`system.html`) |
| `POST` | `/api/backup/create` | สั่งสร้าง Snapshot DB ผ่าน `VACUUM INTO` | - | `{"success": true, "filename": str}` |
| `POST` | `/api/backup/delete` | ลบไฟล์สำรองข้อมูลที่ไม่ต้องการ | `{"filename": str}` | `{"success": bool}` |
| `GET` | `/api/backup/list` | ดูรายการไฟล์สำรองทั้งหมด | - | JSON (list of backups) |
| `GET` | `/api/system/integrity` | ตรวจสอบความสมบูรณ์ของฐานข้อมูล | - | `{"integrity_ok": bool, "foreign_keys_ok": bool}` |

---

## 7. การออกแบบฝั่งผู้ใช้และประสบการณ์ผู้เรียน (Frontend UI, Offline KaTeX & Interactivity)

1. **Local-First KaTeX Engine:**
   - ไฟล์ `katex.min.css`, `katex.min.js`, `auto-render.min.js` และไฟล์ฟอนต์ `KaTeX_*.woff2` ทั้งหมด 20 ไฟล์ถูกติดตั้งแบบ Standalone ใน `app/static/vendor/katex/`
   - ฟังก์ชัน `renderMathInDocument()` จะสแกนและเรนเดอร์สัญลักษณ์ `$...$` (inline) และ `$$...$$` (display) ทันทีที่โหลดหน้า หรือเมื่อมีการเปิดเนื้อหาใหม่แบบไดนามิก
2. **Typography & System Fallbacks:**
   - ใช้ฟอนต์หลัก `'Sarabun'` และตั้งค่า Fallback เป็นฟอนต์ระบบภาษาไทยของ Windows/macOS (`'Leelawadee UI'`, `'Thonburi'`, `'Tahoma'`) ทำให้อ่านสบายตาและไม่กระตุกแม้ไม่มีอินเทอร์เน็ต
3. **Interactive Components ใน [app/static/js/app.js](file:///C:/Users/pqx12/Desktop/tcas/app/static/js/app.js):**
   - **`PracticeTimer`:** ตัวจับเวลาการคิดโจทย์ระดับมิลลิวินาที แยกเวลาคิดโจทย์ (Thinking Time) ออกจากเวลาอ่านเฉลย
   - **`showToast` & `copyToClipboard`:** ระบบแจ้งเตือนแบบป๊อปอัป และการคัดลอก Prompt AI ลงคลิปบอร์ดแบบ 1 คลิก รองรับทั้ง Clipboard API มาตรฐานและ Fallback Textarea
   - **Accordion System:** คำใบ้แบบพับเก็บและขยายได้ 3 ระดับ
   - **Image Viewer & Lightbox:** รองรับรูปภาพข้อสอบที่ผู้เรียนนำเข้าจาก PDF สามารถคลิกเพื่อเปิดดูรูปขยายขนาดเต็มได้

---

## 8. คลังเนื้อหาข้อสอบและการรับรองคุณภาพ (Question Bank & Verification Tiers)

คลังข้อสอบตัวอย่างที่บรรจุอยู่ในระบบถูกสร้างขึ้นตามหลักสูตร สสวท. และแนวข้อสอบ A-Level จริง:

| ไฟล์คลังข้อสอบ | วิชา | จำนวนข้อ | จุดเด่นและเนื้อหา | ระดับการตรวจ |
| :--- | :--- | :---: | :--- | :---: |
| [kinematics_1d.yaml](file:///C:/Users/pqx12/Desktop/tcas/content/physics/kinematics_1d.yaml) | ฟิสิกส์ | 6 ข้อ | การเคลื่อนที่แนวตรง, ความเร็วสัมพัทธ์, วัตถุตกแนวดิ่งจากหน้าผา, กราฟ $v-t$ ที่มีจุดตัด มี Plan Steps ครบทุกข้อ | **Tier B** |
| [forces_energy.yaml](file:///C:/Users/pqx12/Desktop/tcas/content/physics/forces_energy.yaml) | ฟิสิกส์ | 4 ข้อ | กฎข้อ 2 นิวตัน, แรงเสียดทานสถิต/จลน์, กฎการอนุรักษ์พลังงานกลบนพื้นเอียง | **Tier B** |
| [functions_algebra.yaml](file:///C:/Users/pqx12/Desktop/tcas/content/math/functions_algebra.yaml) | คณิต 1 | 3 ข้อ | อสมการเศษส่วนพหุนาม (ดักจุดลืมเงื่อนไขส่วนห้ามศูนย์), สมการเอกซ์โพเนนเชียล | **Tier B** |
| [quantitative.yaml](file:///C:/Users/pqx12/Desktop/tcas/content/tpat3/quantitative.yaml) | TPAT3 | 2 ข้อ | อัตราทดเฟืองกลศาสตร์ (Gear Trains) และความสัมพันธ์เชิงกล | **Tier B** |
| [physics_formulas.yaml](file:///C:/Users/pqx12/Desktop/tcas/content/formulas/physics_formulas.yaml) | บัตรสูตร | 4 บัตร | 5 สูตรการเคลื่อนที่, กฎนิวตัน, พลังงานกล, งานและกำลัง พร้อมคำถาม Active Recall | **Tier A** |
| [alevel_phy_sample.yaml](file:///C:/Users/pqx12/Desktop/tcas/content/past_papers/alevel_phy_sample.yaml)| ข้อสอบเก่า | 20 ข้อ | ข้อสอบจำลอง A-Level ฟิสิกส์ 20 ข้อ สำหรับโหมดกรอกกระดาษคำตอบจับเวลา | **Tier B** |
| [custom_questions.yaml](file:///C:/Users/pqx12/Desktop/tcas/content/imported/custom_questions.yaml) | นำเข้า | พลวัต | ข้อสอบที่ผู้เรียนนำเข้าจากไฟล์ PDF หรือรูปภาพโซเชียล | **Tier D** |

---

## 9. ชุดทดสอบอัตโนมัติและระดับการตรวจสอบทางคณิตศาสตร์ (Automated Test Suite & Math Assertions)

ระบบมีชุดทดสอบอัตโนมัติ **53 การทดสอบ** รันผ่าน `pytest` แบ่งออกเป็น 9 หมวด:

```bash
python -m pytest
============================= 53 passed in 3.06s =============================
```

### สรุปรายละเอียดชุดทดสอบทั้ง 9 ไฟล์:

1. **[test_physics_answers.py](file:///C:/Users/pqx12/Desktop/tcas/tests/test_physics_answers.py) (11 tests - Level B Verification):**
   - เขียนโค้ดสูตรคำนวณทางฟิสิกส์จริงเพื่อ `assert` ตรวจสอบว่า คำตอบของโจทย์ทุกข้อและช้อยส์ลวงในไฟล์ YAML คำนวณออกมาถูกต้องตามหลักฟิสิกส์จริง 100%
   - ตัวอย่างเช่น: ตรวจการตกแนวดิ่ง $s = ut - \frac{1}{2}gt^2$ เมื่อโยนขึ้นจากหน้าผา $u=15, s=-50$, คำนวณเวลาตกถึงพื้นจริง $t=5.0\text{ s}$ ตรงกับช้อยส์ `o3` และช้อยส์ลวง `o1` ($t=1.5\text{ s}$) ตรงกับแท็ก `only_to_peak`
2. **[test_content_schema.py](file:///C:/Users/pqx12/Desktop/tcas/tests/test_content_schema.py) (3 tests):**
   - ตรวจสอบความสมบูรณ์ของโครงสร้าง Pydantic ในไฟล์ YAML ทุกไฟล์ ทั้งข้อสอบ บัตรสูตร และข้อสอบเก่า
3. **[test_grader.py](file:///C:/Users/pqx12/Desktop/tcas/tests/test_grader.py) (7 tests):**
   - ตรวจสอบตัวแปลงตัวเลข Normalizer, Unicode minus (`−`), จุลภาค, เศษส่วน (`3/4`), สัญกรณ์วิทยาศาสตร์, Tolerance, และการจับคู่ Error Tags
4. **[test_procedural_gen.py](file:///C:/Users/pqx12/Desktop/tcas/tests/test_procedural_gen.py) (5 tests):**
   - ตรวจสอบว่าโจทย์สุ่มคิดเลขเร็วทุกหมวดให้ผลลัพธ์เป็นตัวเลขที่ถูกต้องและคิดในใจได้
5. **[test_review_engine.py](file:///C:/Users/pqx12/Desktop/tcas/tests/test_review_engine.py) (3 tests):**
   - ตรวจสอบการเลื่อนขั้น Spaced Repetition, การคัดแยกข้อที่เข้าใจผิดรุนแรง (Misconceptions), และการคำนวณ Honest Mastery Rate
6. **[test_backup.py](file:///C:/Users/pqx12/Desktop/tcas/tests/test_backup.py) (2 tests):**
   - ตรวจสอบการทำงานของ `VACUUM INTO` และการรัน `PRAGMA integrity_check`
7. **[test_routes.py](file:///C:/Users/pqx12/Desktop/tcas/tests/test_routes.py) (11 tests):**
   - ตรวจสอบการตอบสนองของเส้นทาง HTTP ทั้งหมดผ่าน FastAPI TestClient ว่าคืนค่า HTTP 200 และคืนค่า JSON ที่ถูกต้อง
8. **[test_pdf_and_roadmap.py](file:///C:/Users/pqx12/Desktop/tcas/tests/test_pdf_and_roadmap.py) (3 tests):**
   - ตรวจสอบการประมวลผลไฟล์ PDF ผ่าน PyMuPDF และการจัดลำดับบทเรียน Roadmap
9. **[test_audit_fixes.py](file:///C:/Users/pqx12/Desktop/tcas/tests/test_audit_fixes.py) (8 tests):**
   - ตรวจสอบจุดแก้ไขจากการ Roast โค้ดเบส: ไฟล์ KaTeX Offline อยู่ครบ, การตัดหน่วยฟิสิกส์ (`20 m/s`), เลขไทย (`๑๒.๕`), การตรวจกระดาษคำตอบด้วย Tolerance, ระบบ Bookmark, Pre-solve AI prompt, การแก้วันสอบ, และการลบไฟล์ Backup

---

## 10. ประวัติการชำแหละโค้ดเบสและการแก้ไขช่องโหว่ (Brutal Codebase Roast & Remediations)

ในการตรวจสอบความสมบูรณ์ของระบบ ทีมพัฒนาได้ทำการ **Brutal Roast (ชำแหละจุดบกพร่องแบบไม่ไว้หน้า)** และแก้ไขปัญหาที่พบทั้ง 10 จุดอย่างสมบูรณ์:

| ลำดับ | จุดบกพร่องเดิมที่พบ (Defect) | ผลกระทบที่อาจเกิดขึ้น | วิธีการแก้ไขที่นำไปปฏิบัติจริง (Remediation) |
| :---: | :--- | :--- | :--- |
| **1** | KaTeX และ Fonts โหลดผ่าน CDN | เมื่อปิดอินเทอร์เน็ต สมการ LaTeX จะกลายเป็นโค้ดดิบ | ดาวน์โหลด KaTeX 0.16.8 และฟอนต์ 20 ไฟล์ฝังใน `app/static/vendor/katex/` 100% Offline |
| **2** | `practice.html` ลืมแสดงภาพโจทย์ | โจทย์ที่นำเข้าจาก PDF ไม่แสดงภาพประกอบ | เพิ่มบล็อกเรนเดอร์รูปภาพ `q.image_url` พร้อมระบบคลิกขยายภาพ |
| **3** | `answer_sheet.py` ใช้ `==` ตรวจตัวเลข | ตอบ `12.5` แทน `12.50` หรือใช้ลบยูนิโค้ดโดนปรับตก | เชื่อมโยง `grade_numeric` เข้ามาตรวจ ทำให้รองรับทศนิยมและ Tolerance 2% |
| **4** | `roadmap` อัปเดตแล้วรีเซ็ต `order_index` เป็น 0 | แก้ไขการตั้งค่าบทแล้วลำดับที่จัดไว้พังทลาย | ปรับ SQL ใน `update_topic_priority` ให้คงค่า `order_index` เดิมไว้ |
| **5** | มี API แก้วันสอบแต่ไม่มีหน้า UI | ผู้เรียนไม่สามารถแก้วันสอบ TCAS ของตนเองได้ | เพิ่มฟอร์มปรับเปลี่ยนวันสอบ TGAT/TPAT และ A-Level ในหน้า `/roadmap` |
| **6** | หน้า Formula Recall สแปมคะแนนได้ | คลิกช้อยส์ซ้ำๆ ปั๊มคะแนนใน DB ได้ไม่จำกัด | เพิ่ม State Locking ปิดการคลิกซ้ำหลังตอบ และเพิ่มปุ่มลองใหม่ |
| **7** | ข้อมูลการฝึกคิดเลขไม่แสดงในแดชบอร์ด | ผู้เรียนไม่เห็นสถิติความคล่องในการคำนวณ | ดึงข้อมูลจาก `procedural_attempts` มาแสดงใน Dashboard และ Stats |
| **8** | ตาราง `bookmarks` ถูกปล่อยทิ้ง | ผู้เรียนไม่มีที่เก็บข้อสอบยาก | เพิ่มปุ่ม ⭐ ติดดาวในหน้าโจทย์ และแท็บกรองดูเฉพาะข้อที่ติดดาว |
| **9** | ตัวตรวจตัวเลขไม่ตัดหน่วยฟิสิกส์ | ตอบ `20 m/s` โดนปรับผิดเพราะแถมหน่วย | อัปเกรด regex ใน `normalize_numeric_string` ให้ตัดหน่วยฟิสิกส์อัตโนมัติ |
| **10**| ขอคำใบ้ AI ได้เฉพาะหลังส่งคำตอบ | ติดขัดตั้งแต่เริ่มทำ ไม่สามารถขอคำใบ้ได้ | เพิ่มฟังก์ชัน Pre-solve AI Prompt ขอแนวคิดตั้งต้นโดยไม่สปอยล์คำตอบ |

---

## 11. คู่มือการติดตั้งและรันระบบ (Setup & Execution Guide)

### 11.1 ความต้องการของระบบ (Prerequisites)
- ระบบปฏิบัติการ: Windows 10/11, macOS หรือ Linux
- Python: เวอร์ชัน 3.11 หรือสูงกว่า (ทดสอบและรับรองบน Python 3.13)
- เบราว์เซอร์: Google Chrome, Microsoft Edge, Firefox, Safari

### 11.2 การติดตั้งและเปิดใช้งาน (1-Click Run)

1. **บนระบบปฏิบัติการ Windows:**
   - ดับเบิ้ลคลิกไฟล์ **`run.bat`**
   - หรือเปิด Terminal ที่โฟลเดอร์โปรเจกต์แล้วรันคำสั่ง:
     ```bash
     python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
     ```
2. **การเข้าใช้งาน:**
   - เปิดเว็บเบราว์เซอร์ไปที่: **`http://127.0.0.1:8000`**
3. **การรันชุดทดสอบอัตโนมัติ:**
   ```bash
   python -m pytest -v
   ```

---

## 12. ประเด็นแนะนำสำหรับการรีวิวโดย Claude (Key Review Prompts & Questions for Claude)

เพื่อให้คุณสามารถส่งเอกสารนี้ให้ Claude ช่วยรีวิวและวิเคราะห์ต่อได้อย่างมีประสิทธิภาพ นี่คือคำถามและหัวข้อที่แนะนำให้ถาม Claude:

### คำถามที่แนะนำให้ส่งให้ Claude ร่วมกับเอกสารนี้:

1. **การตรวจสอบสถาปัตยกรรม (Architectural & Code Health Review):**
   > *"จากสถาปัตยกรรม Local-First ของระบบ TCAS Mastery นี้ มีจุดคอขวด (Bottleneck) หรือความเสี่ยงด้านการเขียนไฟล์พร้อมกัน (Concurrency / Race Condition) ใน SQLite WAL mode จุดใดที่ควรระวังเพิ่มเติมอีกหรือไม่?"*
2. **การประเมินด้านจิตวิทยาการเรียนรู้ (Pedagogical Evaluation):**
   > *"กลไก 3 ขั้นตอน (Plan Step -> Checkpoints -> Error-Tagged Distractors) ร่วมกับ Spaced Repetition ในระบบนี้ มีจุดใดที่สามารถเพิ่มประสิทธิภาพเพื่อช่วยให้นักเรียนเตรียมสอบฟิสิกส์และคณิตประยุกต์ 1 จดจำและเข้าใจได้ดียิ่งขึ้นอีกหรือไม่?"*
3. **การขยายระบบในอนาคต (Extensibility & Future Features):**
   > *"หากต้องการเพิ่มความสามารถในการนำเข้าข้อสอบอัตโนมัติจาก PDF ด้วย Local OCR (เช่น Tesseract หรือ Surya OCR) โดยยังคงรักษาหลักการ 100% Offline ไว้อยู่ ควรออกแบบ Pipeline การทำงานอย่างไรให้เบาเครื่องที่สุด?"*
4. **การประเมินความปลอดภัย (Security & Data Integrity Audit):**
   > *"จาก API endpoints และกลไก SQLite VACUUM INTO รวมถึงการอัปโหลดไฟล์ในสตูดิโอนำเข้าข้อสอบ มีประเด็นด้าน File Traversal หรือ Input Sanitization จุดใดที่ควรเพิ่ม Guardrails อีกหรือไม่?"*

---
*เอกสารนี้จัดทำขึ้นอย่างละเอียดและครอบคลุมทุกส่วนของระบบ พร้อมสำหรับการส่งรีวิวในเชิงลึกทันที*
