# แผนแม่บทระบบฝึกทำข้อสอบ TCAS (Master Unified Implementation Plan)
> **เอกสารบูรณาการ:** สังเคราะห์จาก `astra_plan.md` (สถาปัตยกรรมและการเรียนรู้เชิงลึก) และ `claude_plan.md` (การปรับแผนปฏิบัติการจริงและการจัดการงบเวลา)
> **เป้าหมาย:** ระบบฝึกข้อสอบ TCAS (ฟิสิกส์, คณิตประยุกต์ 1, TPAT3, TGAT2) บนคอมพิวเตอร์ส่วนบุคคล แบบ Local-First ทำงานได้ 100% แม้ไม่มีอินเทอร์เน็ต ตรวจคำตอบแบบ Deterministic พร้อมระบบวิเคราะห์จุดอ่อน เจาะลึกสูตร-ทักษะคำนวณ และทบทวนแบบ Spaced Repetition

---

## 1. ปรัชญาและหลักการสำคัญ (Core Principles)

1. **Local-First & 100% Reliable Offline:**
   - ระบบทำงานในเครื่องคอมพิวเตอร์ส่วนบุคคล (`127.0.0.1:8000`) ใช้งานได้สมบูรณ์โดยไม่ต้องเชื่อมต่อภายนอก
   - ไม่ต้องมีโฮสติ้ง ไม่มีค่าใช้จ่ายแอบแฝง
2. **Deterministic Grading (ตรวจคำตอบโดยไม่อาศัย AI):**
   - การตรวจถูก/ผิดใช้ Logic ชัดเจน (ช้อยส์ตรง ID, ตัวเลขผ่าน Tolerance และ Normalization)
   - AI ทำหน้าที่เพียงผู้ช่วยอธิบาย (Tutor) ห้ามให้ AI เป็นผู้ตัดสินผลการให้คะแนน
3. **การแยกผลการทำอย่างตรงไปตรงมา (Honest Metrics):**
   - แยกชัดเจนระหว่าง "ทำได้เองตั้งแต่แรก" (Independent Mastery) กับ "ถูกหลังเปิดคำใบ้/ตัวช่วย" (Assisted)
   - ไม่นำผลที่จำคำตอบข้อเดิมมาเคลมว่าชำนาญแล้ว
4. **ความน่าเชื่อถือและการตรวจสอบที่มา (Verification Tiers A–E):**
   - ทุกข้อต้องระบุระดับการตรวจ:
     - **Level A:** ตรงกับเฉลยทางการ MyTCAS
     - **Level B:** ตรวจยืนยันด้วยโค้ดคำนวณอัตโนมัติ (Python assertion)
     - **Level C:** ครู/ติวเตอร์ตรวจยืนยัน
     - **Level D:** AI สองตัวตรงกัน + ผู้เรียนไล่ตรวจ (ติดป้ายเตือน)
     - **Level E:** ยังไม่ตรวจ (ห้ามนำมาคิดสถิติหลัก)
5. **เจาะลึกกลไกความผิดพลาด (Root-Cause Diagnosis):**
   - แทนที่จะให้ผู้เรียนเดาว่าผิดเพราะอะไร ระบบออกแบบ 3 กลไกสนับสนุน:
     1. **Plan Step (เลือกสูตรก่อนทำ):** ถามสมการ/หลักการก่อนแทนค่า
     2. **Checkpoints (จุดตรวจระหว่างทาง):** ตรวจการแปลงหน่วยหรือค่าตัวแปรเบื้องต้น
     3. **Error-Tagged Distractors (ช้อยส์ดักจุดผิด):** แต่ละช้อยส์ลวงผูกกับแท็กความผิดพลาด เช่น ลืมแปลงหน่วย, ลืมเลข 2, ย้ายข้างผิด, เครื่องหมายผิด
6. **Active Formula Recall (บัตรเรียกคืนสูตร):**
   - แบบฝึกทบทวนเงื่อนไขการใช้สูตร หน่วย และตัวแปร ป้องกันปัญหา "จำสูตรไม่ได้ / ใช้ผิดเงื่อนไข"
7. **Infinite Procedural Calculation Drills (ตัวสร้างแบบฝึกคำนวณสุ่มตัวเลข):**
   - แบบฝึกคิดเลขไม่อั้น ไม่ต้องพึ่ง AI: แปลงหน่วย (km/h ↔ m/s), เศษส่วน, เลขยกกำลัง, เครื่องหมายลบ
   - ตัวเลขคัดสรรให้คิดมือได้ลงตัวตามมาตรฐานสนามสอบที่ไม่อนุญาตให้ใช้เครื่องคิดเลข
8. **Pragmatic AI & Safe Data Storage:**
   - ฟีเจอร์หลักคือปุ่ม **"คัดลอกบริบทไปถาม AI" (One-Click AI Context Copy)** รวบรวมโจทย์ คำตอบที่ตรวจแล้ว และจุดที่ติด เพื่อให้ไปถามได้ทันทีโดยไม่เสียค่า API
   - รองรับการเชื่อมต่อ API ทางเลือก (Gemini / Local LLM) หากผู้ใช้ใส่ Key
   - จัดเก็บฐานข้อมูล SQLite โหมด WAL พร้อมระบบสำรองข้อมูลอัตโนมัติผ่าน `VACUUM INTO`

---

## 2. โครงสร้างระบบและสถาปัตยกรรม (System Architecture)

### 2.1 Technology Stack
- **Backend:** Python 3.13 + **FastAPI** + **Uvicorn**
- **Database:** **SQLite3** (WAL Mode + Foreign Keys On)
- **Data Modeling & Validation:** **Pydantic v2** + **PyYAML**
- **Testing & Content Verification:** **pytest**
- **Frontend:** HTML5 + CSS (Modern Responsive Tailwind-inspired clean aesthetic) + Vanilla JS
- **Math Rendering:** **KaTeX** (เรนเดอร์สมการคณิตศาสตร์และฟิสิกส์ LaTeX ได้รวดเร็วและรองรับออฟไลน์)

### 2.2 โครงสร้างไดเรกทอรีโปรเจกต์
```
C:\Users\pqx12\Desktop\tcas\
├── unified_tcas_plan.md        # แผนแม่บทฉบับบูรณาการนี้
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI Application & Lifespan
│   ├── config.py               # Settings (Paths, Port, DB settings)
│   ├── database.py             # SQLite Connection & Migration helpers
│   ├── models/
│   │   ├── content_schema.py   # Pydantic schemas สำหรับข้อสอบและบัตรสูตร
│   │   └── api_schema.py       # Request/Response schemas
│   ├── services/
│   │   ├── content_loader.py   # YAML Loader & Validator
│   │   ├── grader.py           # ตัวตรวจคำตอบ (MCQ, Numeric, Tolerance, Unicode minus)
│   │   ├── procedural_gen.py   # ตัวสร้างโจทย์คำนวณสุ่มตัวเลข (Procedural Drills)
│   │   ├── review_engine.py    # Spaced Repetition & Weakness Queue
│   │   ├── answer_sheet.py     # ตัวประมวลผลกระดาษคำตอบข้อสอบจำลอง
│   │   ├── backup_service.py   # SQLite VACUUM INTO Backup service
│   │   ├── ai_helper.py        # ตัวสร้าง Prompt บริบทสำหรับ AI Tutor
│   │   ├── pdf_importer.py     # ตัวประมวลผลนำเข้าข้อสอบจาก PDF/รูปภาพ
│   │   └── roadmap_service.py  # แผนการอ่านและจัดการลำดับความสำคัญบทเรียน
│   ├── routers/
│   │   ├── practice.py         # เส้นทางทำโจทย์หลัก
│   │   ├── drills.py           # เส้นทางแบบฝึกคำนวณสุ่มตัวเลข
│   │   ├── formulas.py         # เส้นทางบัตรสูตร
│   │   ├── answer_sheet.py     # เส้นทางโหมดกรอกกระดาษคำตอบ
│   │   ├── stats.py            # เส้นทางสถิติและคิวทบทวน
│   │   ├── system.py           # เส้นทางสำรองข้อมูล
│   │   ├── import_studio.py    # สตูดิโอนำเข้าข้อสอบ PDF/รูปภาพ
│   │   └── roadmap.py          # แผนการอ่าน & จัดลำดับบทเรียน
│   ├── templates/              # หน้าเว็บ UI (Jinja2 Templates)
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── practice.html
│   │   ├── procedural_drill.html
│   │   ├── formula_recall.html
│   │   ├── answer_sheet.html
│   │   ├── import_studio.html
│   │   ├── roadmap.html
│   │   ├── system.html
│   │   └── stats.html
│   └── static/                 # Static Assets (CSS, JS, KaTeX)
│       ├── css/style.css
│       ├── js/app.js
│       └── vendor/katex/
├── content/                    # คลังโจทย์และเนื้อหา (YAML Based)
│   ├── physics/
│   │   ├── kinematics_1d.yaml  # ฟิสิกส์: การเคลื่อนที่แนวตรง (โจทย์ลึก ละเอียดทุกทักษะ)
│   │   └── forces_energy.yaml  # ฟิสิกส์: กฎนิวตันและงานพลังงาน
│   ├── math/
│   │   └── functions_algebra.yaml # คณิตประยุกต์ 1
│   ├── tpat3/
│   │   └── quantitative.yaml   # TPAT3 ความถนัดด้านวิทยาศาสตร์และวิศวกรรม
│   ├── formulas/
│   │   └── physics_formulas.yaml # บัตรสูตรฟิสิกส์และการทดสอบเงื่อนไข
│   └── past_papers/
│       └── alevel_phy_sample.yaml # ข้อสอบเก่าสำหรับโหมดกระดาษคำตอบ
├── data/                       # ข้อมูล runtime และฐานข้อมูล
│   ├── tcas.db                 # SQLite DB
│   └── backups/                # จุดเก็บไฟล์ Backup จาก VACUUM INTO
├── tests/                      # ชุดทดสอบอัตโนมัติ (pytest)
│   ├── test_content_schema.py  # ตรวจความถูกต้องของไฟล์ YAML
│   ├── test_physics_answers.py # Level B Verification Tests (Assert ตัวเลขจริง)
│   ├── test_grader.py          # ตรวจ logic การตรวจคำตอบและ Normalize
│   ├── test_procedural_gen.py  # ตรวจสอบตัวสร้างโจทย์สุ่มตัวเลข
│   ├── test_review_engine.py   # ตรวจสอบคิวทบทวนและ Spaced Repetition
│   └── test_backup.py          # ตรวจสอบการทำ Backup
├── run.bat                     # สคริปต์รันแอปพลิเคชัน 1 คลิก
├── requirements.txt            # รายการ Dependencies
└── README.md                   # คู่มือการใช้งานระบบ
```

---

## 3. รายละเอียดสเปกของฟีเจอร์หลัก (Detailed Feature Specifications)

### 3.1 มาตรฐานไฟล์โจทย์ (YAML Content Schema & Verification)
โจทย์แต่ละข้อระบุข้อมูลครบถ้วนตามมาตรฐานที่บูรณาการ:
- `id`: รหัสเฉพาะ เช่น `phy-kin-0001`
- `source`: ที่มา (official MyTCAS / textbook / invented)
- `verification`: ระดับการตรวจ (`tier: A/B/C/D`, `verified_by: ...`)
- `topic` & `skills`: ทักษะหลัก (`primary`) และทักษะรอง (`secondary`)
- `stem`: ข้อความโจทย์ (รองรับ LaTeX `$s = ut + \frac{1}{2}at^2$`)
- `plan_step`: คำถามเลือกสูตรก่อนทำ (Optional สำหรับโจทย์เชิงคำนวณ)
- `checkpoints`: คำถามตรวจจุดระหว่างทาง (เช่น แปลงหน่วย)
- `answer`:
  - `type`: `single_choice` หรือ `numeric`
  - ตัวเลือกพร้อม `error_tag` สำหรับข้อที่ผิด เพื่อวินิจฉัยจุดพลาดทันที
- `hints`: คำใบ้ 3 ระดับ (ระดับ 1: แกะสิ่งที่รู้และสิ่งที่ต้องหา, ระดับ 2: สูตรและเงื่อนไข, ระดับ 3: แนวทางลงมือทำ)
- `solution_steps`: ขั้นตอนเฉลยละเอียดแบบขยายได้ พร้อมสรุปสูตรและจุดระวัง

### 3.2 ระบบตรวจคำตอบตัวเลขที่ยืดหยุ่น (Numeric Grader & Normalization)
- รองรับ Unicode Minus: `−` (U+2212) แปลงเป็น `-` (ASCII) อัตโนมัติ
- รองรับการคั่นหลักพัน: `1,000` → `1000`
- รองรับเศษส่วน: `3/4` → `0.75`
- รองรับสัญกรณ์วิทยาศาสตร์: `2e3`, `2*10^3`, `2x10^3`
- กำหนดค่าความคลาดเคลื่อน (Tolerance): default ±1% สำหรับทศนิยม

### 3.3 ระบบสร้างโจทย์สุ่มคำนวณไม่จำกัด (Procedural Drill Engine)
ฝึกคิดเลขและคำนวณพื้นฐานโดยไม่ต้องพึ่งพา AI:
1. **การแปลงหน่วยความเร็ว:** $km/h \leftrightarrow m/s$ โดยสุ่มตัวเลขพหุคูณของ 18 หรือ 3.6 เพื่อให้คิดเลขในใจได้ลงตัว (เช่น 36, 54, 72, 90, 108 km/h)
2. **การแปลงหน่วยพื้นที่/ปริมาตร:** $cm^2 \leftrightarrow m^2$, $cm^3 \leftrightarrow m^3$
3. **การคำนวณ 5 สูตรการเคลื่อนที่แนวตรง:** สุ่มตัวแปร 3 ตัว หาตัวแปรที่ 4 ด้วยตัวเลขที่ถอดรากและหารลงตัว
4. **เศษส่วนและเลขยกกำลังในฟิสิกส์:** การเปรียบเทียบอัตราส่วน $v_1/v_2$, การคิดเลขสัญกรณ์วิทยาศาสตร์

### 3.4 โหมดกระดาษคำตอบ (Answer Sheet Mode)
- สำหรับการทำข้อสอบเก่าจริงบนกระดาษตามเวลาสนามจริง
- ผู้ใช้เลือกชุดข้อสอบ (เช่น A-Level ฟิสิกส์ 2566)
- หน้าจอกระดาษคำตอบให้คลิกตอบข้อ 1-30 อย่างรวดเร็ว
- กดยื่นส่ง: ระบบตรวจคะแนนรวม แยกคะแนนตามบท และระบุหัวข้อที่ต้องทบทวนทันที

### 3.5 Active Formula Recall (ระบบบัตรเรียกคืนสูตร)
- ทดสอบการดึงสูตรจากความจำ 3 ด้าน:
  1. *สถานะ/เงื่อนไข:* "สูตรนี้ใช้ได้เมื่อความเร่งเป็นอย่างไร? (a คงที่)"
  2. *การจับคู่ตัวแปร:* "ถ้าโจทย์ไม่บอกเวลา $t$ และไม่ถามเวลา $t$ ต้องใช้สูตรใด? ($v^2 = u^2 + 2as$)"
  3. *หน่วยของตัวแปร:* "ตัวแปร $a$ ใน SI Unit คือหน่วยใด?"

### 3.6 Spaced Repetition Review Queue & Diagnostics
- บันทึกการทำโจทย์ใน SQLite แยกเป็น:
  - `status`: `correct_first_try` (ทำถูกเองรอบแรก), `correct_assisted` (ถูกหลังเปิดคำใบ้), `wrong` (ผิด)
  - `confidence`: `sure` (มั่นใจ), `unsure` (ไม่แน่ใจ), `guessed` (เดา)
- จัดลำดับคิวทบทวนตามความเร่งด่วน:
  1. **High Priority:** ข้อที่ "มั่นใจแต่ตอบผิด" (Misconception รุนแรง)
  2. **Medium Priority:** ข้อที่ถูกหลังเปิดใบ้ หรือถูกแต่ไม่มั่นใจ
  3. **Scheduled:** Spaced Repetition (1 วัน, 3 วัน, 7 วัน, 14 วัน, 30 วัน)
- การวัดเวลา: แยกเวลาคิดโจทย์ (Thinking Time) ออกจากเวลาอ่านเฉลย (Review Time)

### 3.7 ผู้ช่วย AI Tutor แบบ One-Click
- ปุ่ม "คัดลอกบริบทไปถาม AI" (Copy Prompt for AI):
  - รวม: โจทย์, ตัวเลือกที่ผู้เรียนเลือก, ข้อผิดพลาดที่ตรวจพบ (`error_tag`), เฉลยทางการ, และขั้นตอนที่ติด
  - คัดลอกลง Clipboard ทันที พร้อมนำไปวางใน ChatGPT/Claude/Gemini นอกเบราว์เซอร์ได้เลย
- รองรับการตั้งค่า Gemini API Key ในเครื่อง เพื่อให้สามารถกดถามและแสดงคำตอบในแอปได้โดยตรงหากต้องการ

### 3.8 การสำรองข้อมูลที่ปลอดภัย (Database Safety & Backup)
- ใช้ `sqlite3` โหมด WAL
- มีปุ่มและคำสั่งสำรองข้อมูลผ่าน `VACUUM INTO 'data/backups/tcas_backup_<timestamp>.db'`
- ตรวจสอบความถูกต้องของ Foreign Keys และ Integrity ด้วย `PRAGMA integrity_check`

---

## 4. แผนงานการลงมือทำ (Implementation Checklist)

- [x] **Phase 1: Project Setup & Core Foundation** (เสร็จสมบูรณ์ 100%)
  - สร้างโครงสร้างโฟลเดอร์ `app/`, `content/`, `data/`, `tests/`
  - สร้าง `app/config.py`, `app/database.py` (SQLite schema & migrations)
  - สร้าง `app/models/content_schema.py` (Pydantic schema รองรับ Verification, Plan Step, Checkpoints, Error Tags)
  - สร้าง `requirements.txt` และตั้งค่า Environment
- [x] **Phase 2: Question Content & Level B Python Test Suite** (เสร็จสมบูรณ์ 100%)
  - สร้างเนื้อหา YAML ฟิสิกส์การเคลื่อนที่แนวตรง `content/physics/kinematics_1d.yaml` (มีโจทย์ครอบคลุมทุกทักษะ พร้อม Error Tags, Plan Steps, Hints 3 ระดับ)
  - สร้างเนื้อหา YAML แรงและงานพลังงาน `content/physics/forces_energy.yaml`
  - สร้างเนื้อหาคณิตศาสตร์ `content/math/functions_algebra.yaml`
  - สร้างเนื้อหา TPAT3 `content/tpat3/quantitative.yaml`
  - สร้างบัตรสูตร `content/formulas/physics_formulas.yaml`
  - สร้าง `tests/test_content_schema.py` ตรวจความถูกต้องของ YAML ทุกไฟล์
  - สร้าง `tests/test_physics_answers.py` เขียน Assertion คณิตศาสตร์ตรวจสอบความถูกต้องของคำตอบ (Level B Verification)
- [x] **Phase 3: Core Grading & Procedural Drill Engines** (เสร็จสมบูรณ์ 100%)
  - พัฒนา `app/services/grader.py` (รองรับ MCQ, Numeric with tolerance, Unicode minus, Fractions)
  - พัฒนา `app/services/procedural_gen.py` (สร้างโจทย์สุ่มตัวเลขคิดในใจได้: แปลงหน่วย, 5 สูตรการเคลื่อนที่, เศษส่วน/เลขยกกำลัง)
  - พัฒนา `tests/test_grader.py` และ `tests/test_procedural_gen.py`
- [x] **Phase 4: Spaced Repetition Engine, Answer Sheet & Backup** (เสร็จสมบูรณ์ 100%)
  - พัฒนา `app/services/review_engine.py` (คำนวณคิวทบทวน, แยกข้อทำเอง vs มีตัวช่วย, มั่นใจแต่ผิด)
  - พัฒนา `app/services/answer_sheet.py` (โหมดกรอกกระดาษคำตอบข้อสอบจำลอง)
  - พัฒนา `app/services/backup_service.py` (SQLite `VACUUM INTO` backup)
  - พัฒนา `app/services/ai_helper.py` (สร้าง Prompt สำหรับ AI Copy และต่อ Gemini API)
  - พัฒนา `tests/test_review_engine.py` และ `tests/test_backup.py`
- [x] **Phase 5: FastAPI Web Endpoints & Responsive UI** (เสร็จสมบูรณ์ 100%)
  - สร้าง Template HTML + CSS + JS สะอาด สวยงาม รองรับ KaTeX สำหรับเรนเดอร์สมการคณิตศาสตร์
  - หน้า Dashboard (ภาพรวม, คิวทบทวนวันนี้, สถิติจุดอ่อน)
  - หน้าทำโจทย์ปกติ (Practice Mode): มีปุ่มเลือกสูตร, Checkpoint, คำใบ้ 3 ระดับ, เฉลยละเอียด, ปุ่ม Copy AI
  - หน้าแบบฝึกคำนวณสุ่มตัวเลข (Procedural Drills): สุ่มโจทย์ใหม่เรื่อยๆ พร้อมเฉลยทันที
  - หน้าบัตรเรียกคืนสูตร (Formula Recall)
  - หน้ากรอกกระดาษคำตอบ (Answer Sheet Mode)
  - หน้ารายงานสถิติ (Analytics & Review Queue)
  - หน้าจัดการระบบและสำรองข้อมูล (Backup & Diagnostics)
- [x] **Phase 6: Quality Assurance, Verification & Automated Auditing** (เสร็จสมบูรณ์ 100%)
  - รัน `pytest` ตรวจสอบโค้ดและเนื้อหา 100% ผ่าน
  - ทดสอบ End-to-End API ด้วย `httpx` / FastAPI TestClient
  - ทดสอบการทำงานจริงของเว็บเซิร์ฟเวอร์บนพอร์ตภายในเครื่อง
  - สร้างไฟล์ `run.bat` เพื่อให้ผู้ใช้เปิดใช้งานได้ง่ายในคลิกเดียว
  - ตรวจสอบบั๊กและ Edge Cases ทั้งหมด
- [x] **Phase 7: Final Report & Wrap-up** (เสร็จสมบูรณ์ 100%)
  - จัดทำรายงานสรุปผลการพัฒนา วิธีการใช้งาน และการตรวจสอบความถูกต้อง
- [x] **Phase 8: Future-Proof Expansion (PDF Import & Custom Study Roadmap)** (เสร็จสมบูรณ์ 100%)
  - พัฒนา `app/services/pdf_importer.py` และหน้า `/import` แปลงไฟล์ PDF/รูปภาพเป็นข้อสอบเข้าคลังทันที
  - พัฒนา `app/services/roadmap_service.py` และหน้า `/roadmap` ปรับลำดับความสำคัญของบทเรียน (ระดับ 1, 2, 3) จัดเรียงขึ้น-ลง และนับถอยหลังวันสอบ
  - เพิ่มชุดทดสอบ `tests/test_pdf_and_roadmap.py` ผ่านการทดสอบทั้งหมด 45 ข้อ

---
*สถานะปัจจุบัน: ดำเนินการเสร็จสิ้นครบทุก Phase 100% พร้อมใช้งานจริง*
