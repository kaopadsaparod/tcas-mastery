# TCAS Mastery Prep System 🎯
> **ระบบฝึกทำข้อสอบ TCAS ประจำวัน (ฟิสิกส์, คณิตประยุกต์ 1, TPAT3, TGAT2)**
> สถาปัตยกรรม Local-First ทำงานบนเครื่อง 100% แม้ไม่มีอินเทอร์เน็ต ตรวจคำตอบแบบ Deterministic พร้อมระบบวินิจฉัยจุดอ่อน เจาะลึกสูตร-ทักษะคำนวณ Spaced Repetition และ Confidence Calibration

---

## 🌟 จุดเด่นและปรัชญาของระบบ (Core Highlights)

1. **Local-First & 100% Offline Reliable:**
   - ข้อมูลและฐานข้อมูล SQLite อยู่บนเครื่องของคุณ (`127.0.0.1:8000`) ปลอดภัย เป็นส่วนตัว 100%
   - ไม่ต้องต่อเน็ตก็ทำโจทย์ ดูเฉลย และฝึกคิดเลขได้ครบวงจร
2. **Deterministic Grading (ตรวจถูก/ผิดแน่นอน ไม่ง้อ AI):**
   - การตรวจคะแนนใช้ตรรกะคณิตศาสตร์ที่แน่นอน รองรับเครื่องหมายลบแบบยูนิโค้ด (`−`), จุลภาคคั่นหลักพัน (`1,000`), เศษส่วน (`3/4`), และสัญกรณ์วิทยาศาสตร์ (`2e3`, `2*10^3`)
   - ระบบจับคู่หน่วยฟิสิกส์ (`m/s`, `km/h`, `kg/m³`) อย่างแม่นยำ หากแปลงหน่วยผิดจะติดแท็ก `no_unit_conversion` ทันที
3. **การประเมินผลอย่างตรงไปตรงมา (Honest Mastery Metrics):**
   - แยกสถิติชัดเจนระหว่าง "ทำได้เองตั้งแต่แรก (Honest Mastery)" กับ "ถูกหลังเปิดคำใบ้ (Assisted)"
   - แยก "เดาถูก (Lucky Guesses)" ออกจากสถิติความเชี่ยวชาญแท้จริง
4. **การประเมินความสัมพันธ์ความมั่นใจ (Confidence Calibration):**
   - วิเคราะห์ความแม่นยำจริงเทียบกับความมั่นใจ: มั่นใจ (Sure), ลังเล (Unsure), และเดา (Guessed)
   - ตรวจจับจุดเข้าใจผิดรุนแรง (Severe Misconceptions / Overconfidence Rate)
5. **เกณฑ์เวลาทำข้อสอบจริง (A-Level / TPAT3 Pace Benchmark):**
   - วัดเวลาต่อข้อเทียบกับเกณฑ์สอบจริง (ฟิสิกส์/คณิต: 180s, TPAT3: 150s)
   - แสดง Badge วินิจฉัยความเร็ว: ⚡ เร็วกว่าเกณฑ์, 🎯 อยู่ในเกณฑ์, ⏳ ช้ากว่าเกณฑ์
6. **โหมดฝึกสลับหัวข้อ (Interleaved Practice):**
   - สลับโจทย์ข้ามบทและข้ามวิชาแบบ Round-Robin พร้อมแทรกคิวทบทวน Spaced Repetition ป้องกันการติดกับดักความจำแบบบล็อก (Blocked Practice)
7. **เจาะลึก 3 กลไกความผิดพลาด (Root-Cause Diagnosis):**
   - **Plan Step:** บังคับเลือกสูตร/หลักการก่อนแทนค่า ป้องกันปัญหา "เลือกสูตรไม่เป็น"
   - **Checkpoints:** จุดตรวจตัวเลขระหว่างทาง (เช่น แปลงหน่วย, คำนวณค่าตัวแปรเบื้องต้น)
   - **Error-Tagged Distractors:** แต่ละช้อยส์ลวงผูกกับแท็กความผิดพลาด เช่น ลืมแปลงหน่วย (`no_unit_conversion`), เครื่องหมายผิด (`sign_error`)
8. **แบบฝึกคำนวณสุ่มตัวเลขไม่จำกัด (Procedural Drills):**
   - ฝึกคิดเลขในใจไม่อั้น: แปลงหน่วยความเร็ว ($km/h \leftrightarrow m/s$), พื้นที่/ปริมาตร, 5 สูตรการเคลื่อนที่แนวตรง, สัดส่วนเลขยกกำลัง
   - ตรวจคำตอบเข้มงวดตามมาตรฐานการคิดเลขในใจ ($\le 0.1\%$)
9. **สตูดิโอนำเข้าข้อสอบ PDF & รูปภาพจากโซเชียล (`/import`):**
   - อัปโหลดชีตข้อสอบจาก PDF หรือภาพโซเชียล พร้อมระบบป้องกันความปลอดภัย Magic Bytes, Anti-PDF Bomb, และ UUID Filenames
10. **แผนการอ่านและจัดลำดับความสำคัญของบทเรียน (`/roadmap`):**
    - จัดกลุ่มความสำคัญรายบท (ระดับ 1: ⭐️ ต้องเก็บก่อน, ระดับ 2: 📌 ทยอยเก็บ, ระดับ 3: ⏳ อ่านเสริม) พร้อมตัวนับถอยหลังวันสอบ TCAS TGAT/TPAT และ A-Level

---

## 🚀 วิธีการเริ่มต้นใช้งาน (Quick Start)

### 1. เปิดใช้งานผ่าน Windows Batch Script:
ดับเบิลคลิกไฟล์:
```
run.bat
```
ระบบจะเปิดเซิร์ฟเวอร์ที่ `http://127.0.0.1:8000`

### 2. หรือเปิดใช้งานผ่าน Command Line:
```powershell
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
จากนั้นเปิดเบราว์เซอร์ไปที่: **`http://127.0.0.1:8000`**

---

## 📁 โครงสร้างโปรเจกต์ (Project Structure)

```
tcas/
├── app/
│   ├── main.py                 # FastAPI Application & Security Middleware (CSRF, DNS Rebinding, LAN PIN)
│   ├── config.py               # การตั้งค่า, พาธข้อมูล (รองรับ TCAS_DATA_DIR), และความปลอดภัย
│   ├── database.py             # SQLite WAL Connection (busy_timeout=5000, synchronous=NORMAL)
│   ├── models/                 # Pydantic Schemas (Content & API Schemas)
│   ├── services/
│   │   ├── content_loader.py   # โหลดและ Validate เนื้อหา YAML พร้อม Atomic Pointer Swap
│   │   ├── grader.py           # ตัวตรวจคำตอบ (หน่วยฟิสิกส์, MCQ, Tolerance, Error Tags)
│   │   ├── procedural_gen.py   # ตัวสร้างโจทย์คิดเลขสุ่มตัวเลขไม่จำกัด
│   │   ├── review_engine.py    # Spaced Repetition, Honest Mastery, Calibration & Pace
│   │   ├── answer_sheet.py     # ตัวประมวลผลกระดาษคำตอบข้อสอบจำลอง
│   │   ├── backup_service.py   # SQLite VACUUM INTO Backup (Isolated autocommit connection)
│   │   ├── pdf_importer.py     # นำเข้าข้อสอบ PDF/รูปภาพ (Atomic YAML lock & Safe uploads)
│   │   ├── roadmap_service.py  # บริการแผนการอ่านและนับถอยหลังสอบ
│   │   └── ai_helper.py        # ตัวสร้าง Prompt บริบทสำหรับ AI Tutor
│   ├── routers/                # หน้าเว็บและ API endpoints
│   ├── templates/              # หน้าเว็บ Jinja2 Templates (Dashboard, Practice, Drills, Stats, Roadmap)
│   └── static/                 # CSS, JavaScript, Math rendering (KaTeX offline)
├── content/                    # คลังโจทย์และเนื้อหา YAML
│   ├── physics/                # ฟิสิกส์การเคลื่อนที่แนวตรงและแรง
│   ├── math/                   # คณิตประยุกต์ 1
│   ├── tpat3/                  # TPAT3 เชิงกลและวิศวกรรม
│   ├── formulas/               # บัตรสูตรฟิสิกส์
│   └── past_papers/            # ชุดข้อสอบจำลอง A-Level
├── data/                       # ฐานข้อมูล SQLite (tcas.db) และโฟลเดอร์ backups/
├── tests/                      # ชุดทดสอบอัตโนมัติ pytest (70 ข้อ ผ่านครบ 100%)
├── run.bat                     # สคริปต์รันระบบ 1 คลิกบน Windows
└── requirements.txt            # รายการ Dependencies
```

---

## 🧪 การรันชุดทดสอบอัตโนมัติ (Automated Testing)

เพื่อตรวจสอบความสมบูรณ์ของระบบและการคำนวณโจทย์ทุกข้อ:
```powershell
python -m pytest
```
ชุดทดสอบครอบคลุม **70 ข้อ (Pass 100%, Test Coverage 90%)**:
- `test_claude_review_hardening.py`: ตรวจสอบการตรวจหน่วย, ความปลอดภัย CSRF/DNS Rebinding/LAN PIN, Magic Bytes, Honest Mastery, Calibration, และ Interleaving
- `test_content_schema.py`: ตรวจสอบความถูกต้องของโครงสร้างไฟล์ YAML ทุกไฟล์
- `test_physics_answers.py`: คำนวณและ Assert ผลลัพธ์ตัวเลขโจทย์ฟิสิกส์และคณิตทุกข้อ (Level B Verification)
- `test_grader.py`: ตรวจสอบการแปลง Unicode Minus, จุลภาค, เศษส่วน, และ Error Tags
- `test_procedural_gen.py`: ตรวจสอบตัวสร้างโจทย์สุ่มคิดในใจทั้ง 4 หมวด
- `test_review_engine.py`: ตรวจสอบคิว Spaced Repetition และสถิติจุดอ่อน
- `test_backup.py`: ตรวจสอบ SQLite Integrity Check และการสร้างไฟล์สำรองผ่าน `VACUUM INTO`
- `test_routes.py`: ทดสอบ Endpoints และหน้าเว็บทั้งหมด

---

## 🛡️ ความปลอดภัยและการสำรองข้อมูล (Security & Backup)
- **CSRF & DNS Rebinding Protection:** กรอง Host, Origin และ Referer Headers บนทุกคำขอที่เปลี่ยนแปลงข้อมูล
- **LAN Protection:** รองรับ `TCAS_ACCESS_PIN` สำหรับการใช้งานบนแท็บเล็ตผ่าน Wi-Fi ภายในบ้าน
- **Safe Backup:** สามารถกดปุ่ม **"สำรองข้อมูลทันที"** ได้ที่เมนู **"ระบบและการสำรองข้อมูล"** (`/system`) ระบบจะใช้คำสั่ง `VACUUM INTO` ผ่าน Autocommit connection ปลอดภัย 100% แม้ระบบกำลังทำงาน
