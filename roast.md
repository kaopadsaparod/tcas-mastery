# 🔥 Brutal Roast & Technical Audit 2026: TCAS Mastery Codebase

> **เอกสารประเมินและชำแหละโปรเจกต์:** การตรวจสอบสถาปัตยกรรม โค้ด ความปลอดภัย ประสิทธิภาพ และหลักวิชาการของระบบ TCAS Mastery ทั้งระบบ  
> **วันเวลาประเมิน:** 12 ตุลาคม 2026  
> **เป้าหมาย:** สับแหลก ชี้จุดบกพร่องที่ซ่อนอยู่ ความย้อนแย้ง การหลอกตัวเองของระบบ และวางแผนผ่าตัดแก้ไขให้ระบบสมบูรณ์แบบพร้อมใช้งานจริง 100%

---

## 1. บทสรุปภาพรวม (The Brutal Roast Summary)

ถ้ามองแค่ผิวเผิน โปรเจกต์นี้ดู "ทรงดีมาก":
- 102 pytest tests ผ่านฉลุย 100%
- มีระบบป้องกัน DNS Rebinding, CSRF, Path Traversal, Magic Bytes
- มี Mock Exam Snapshot, Spaced Repetition, 5-Step Adaptive Tutor, Dynamic Study Planner, Progress Diagnostic Report

**แต่ถ้า "ขุดดูใต้พรม" จะพบความจริงที่น่าตกใจและความย้อนแย้งที่รุนแรงหลายจุด:**

### 🔥 1. ข้อสอบ 75 ข้อ "ติดคุก" อยู่ใน Past Papers โดยที่ระบบหลักมองไม่เห็นเลย!
ระบบเคลมว่ามีคลังข้อสอบและ Blueprint แต่ในความเป็นจริง `content_loader.py` โหลดข้อสอบเข้าคลังเฉพาะโฟลเดอร์ `physics/`, `math/`, `tpat3/`, `imported/` รวมแล้วมีแค่ **12 ข้อ!**
ส่วนข้อสอบฟิสิกส์ A-Level 30 ข้อใน `alevel_phy_blueprint_30.yaml`, ข้อสอบตัวอย่าง 20 ข้อใน `alevel_phy_sample.yaml`, และ TPAT3 25 ข้อใน `tpat3_practice_25.yaml` รวม **75 ข้อ** ถูกขังไว้เฉพาะในโหมดกระดาษคำตอบ/จำลองสอบ!
- ในหน้า `/practice` ผู้เรียนเห็นโจทย์แค่ 12 ข้อ ทำแป๊บเดียวก็หมด!
- ค้นหาด้วย `get_question_by_id("bp30-q01")` ได้ `None`!
- จะกดดู Tutor Breakdown, ขอ AI Prompt, ทำโจทย์ซ่อมจุดอ่อน (Skill Variant) หรือติดดาว (Bookmark) ข้อสอบ Blueprint ไม่ได้เลยแม้แต่ข้อเดียว!

### 🔥 2. กับดักความรู้พื้นฐานผี (The Ghost Prerequisite Trap / Catch-22 DAG)
ใน `learning_path.py` เขียนเงื่อนไขความรู้พื้นฐาน (DAG) ไว้อย่างโก้หรู:
- `physics.kinematics.1d` ต้องผ่าน `physics.vectors` ก่อน
- `math.functions_algebra` ต้องผ่าน `math.algebra.basics` ก่อน
**แต่ในระบบไม่มีหัวข้อ `physics.vectors` และ `math.algebra.basics` อยู่ในฐานข้อมูล และไม่มีโจทย์แม้แต่ข้อเดียว!**
ผลคือ: เมื่อผู้เรียนเปิดตารางติว (`/planner`) หรือเช็คความพร้อม ระบบจะเตือนว่า *"คุณยังไม่พร้อมเรียน Kinematics ต้องไปเก็บ physics.vectors ให้ได้ 60% ก่อน"* แต่พอกดเข้าไปเรียน กลับเจอหน้าว่าง 0 ข้อ! ผู้เรียนติดลูปตายอยู่ในระบบตลอดกาล!

### 🔥 3. จำลองสอบ 70 ข้อ "ทิพย์" (Fake TPAT3 70-Question Mock Exam)
ในหน้า `/mock-exam` มีการ์ดขึ้นโชว์หราว่า **"TPAT3 Official Blueprint (70 ข้อ) 180 นาที"** แต่ไฟล์ `tpat3-blueprint-70.yaml` **ไม่มีอยู่จริงในเครื่อง!**
พอนักเรียนกดเริ่มสอบ ระบบแอบ fallback ไปดึงชุดฝึกซ้อม 25 ข้อมาเปิดแทน แต่หน้าจอยังจั่วหัวว่า 70 ข้อ! นี่คือการหลอกผู้ใช้แบบซึ่งๆ หน้า!

### 🔥 4. สอบจำลองแล้ว "สมองเสื่อม" (Mock Exam Amnesia)
นักเรียนอุตส่าห์นั่งสอบจำลองจับเวลาจริง 90 นาที ทำข้อสอบ 30 ข้อ แล้วตอบผิดไป 10 ข้อ...
แต่ `submit_mock_exam` บันทึกผลแค่ในตาราง `mock_exam_sessions` เท่านั้น! **ไม่เคยส่งข้อที่ผิดเข้าตาราง `attempts` หรือ `review_queue` (Spaced Repetition) เลยแม้แต่ข้อเดียว!**
ผลลัพธ์คือ: ข้อที่นักเรียนทำผิดตอนสอบจำลอง จะไม่มีวันโผล่มาใน "คิวทบทวนวันนี้" หรือ "โจทย์ซ่อมจุดอ่อน" ใน Study Planner เลยแม้แต่น้อย! ระบบตัดขาดการสอบจำลองออกจากวงจรการเรียนรู้ประจำวันโดยสิ้นเชิง!

### 🔥 5. แถบเมนู 13 ลิงก์ที่ "เบียดกันจนพัง" (The Mega-Crowded Navbar)
บน `base.html` ยัดลิงก์ใส่ Navbar ไปถึง 13 รายการเรียงแถวยาวเหยียด พอเปิดบน iPad หรือมือถือ แถบเมนูล้นจอ แตกออกเป็น 3-4 บรรทัด ทับส่วนเนื้อหาและทำลาย User Experience ทันที

### 🔥 6. เคลมว่า Local-First 100% แต่แอบแฝงโหลด Google Fonts ข้ามโลก!
ใน Footer เขียนว่า *"Local-First Deterministic Learning Platform • ปลอดภัย 100% ทำงานได้แม้ไม่มีเน็ต"*
แต่ใน `<head>` ของ `base.html` บรรทัดที่ 8-10 ดึง `https://fonts.googleapis.com` และ `https://fonts.gstatic.com` ทุกครั้งที่เปิดหน้าเว็บ! ถ้าปิด Wi-Fi หรือเน็ตหลุด หน้าเว็บจะเกิด DNS timeout หน่วงไปหลายวินาทีกว่าจะเรนเดอร์! ทั้งที่ในเครื่องคอมพิวเตอร์และแท็บเล็ตมีฟอนต์ไทยมาตรฐาน (Leelawadee UI, Sarabun, Thonburi) อยู่แล้ว

### 🔥 7. บั๊กคำว่า `'guessing'` vs `'guessed'`
ใน `tutor_engine.py` บรรทัด 251 ตอนส่งบันทึก attempt ดันส่ง `confidence="guessing"` ในขณะที่ฐานข้อมูลและ `review_engine.py` ยึดคำว่า `'guessed'` ส่งผลให้เงื่อนไขการคำนวณ Spaced Repetition ตกไปเข้ากิ่ง `else: sure` โดยไม่ตั้งใจ!

### 🔥 8. บั๊กปุ่มเลื่อนอันดับ Roadmap สลับค่าไม่ไปไหน (Reorder Topic Deadlock)
ใน `roadmap_service.py` ฟังก์ชัน `reorder_topic_priority` ทำการสลับค่า `order_index` ระหว่าง 2 บทเรียน แต่ถ้า 2 บทนั้นมี `order_index` เท่ากัน (เช่น ค่าเริ่มต้นเป็น 0 เหมือนกัน) การสลับค่าจะไม่เปลี่ยนอะไรเลย กดปุ่มเลื่อนขึ้น-ลง 100 ครั้ง บทเรียนก็อยู่ที่เดิม!

### 🔥 9. หน้า Dashboard ทอดทิ้งฟีเจอร์สำคัญใหม่ๆ
หน้าแรก (`/`) มี Quick Actions แค่ 4 เมนูเดิม (Practice, Drills, Formulas, Answer Sheet) แต่ไม่มีทางลัดเข้าสู่ **ตารางติวรายวัน (`/planner`)**, **จำลองสอบจริง (`/mock-exam`)**, หรือ **ประเมินความพร้อมสอบ (`/progress`)** เลยแม้แต่ปุ่มเดียว!

---

## 2. ตารางสรุปจุดบกพร่องและแนวทางแก้ไข (Defect & Remediation Matrix)

| รหัส | ความรุนแรง | ประเด็นที่ตรวจพบ | ผลกระทบ | แผนการแก้ไข |
| :---: | :---: | :--- | :--- | :--- |
| **ROAST-01** | **CRITICAL** | ข้อสอบ Past Papers 75 ข้อไม่ถูกเชื่อมเข้าสู่ Question Bank หลัก | ผู้เรียนฝึกโจทย์ได้แค่ 12 ข้อ ไม่สามารถค้นหา ติดดาว หรือทำ Skill Variant บนข้อสอบจริงได้ | ทำ Adapter ใน `content_loader` นำเข้าข้อสอบทุกข้อจาก Past Papers เข้าสู่ `_questions` ให้มีข้อสอบพร้อมใช้งานกว่า 87 ข้อทันที |
| **ROAST-02** | **CRITICAL** | กับดัก Prerequisite ผี (`physics.vectors` และ `math.algebra.basics`) ขัดขวางการเรียน | ผู้เรียนถูกบล็อกไม่ให้เรียน Kinematics และ Algebra เพราะไม่มีโจทย์บทพื้นฐานให้ทำ | สร้างเนื้อหาและโจทย์พื้นฐานสำหรับ Vectors & Algebra Basics พร้อม seed ลงใน Roadmap ให้ปลดล็อกได้จริง |
| **ROAST-03** | **HIGH** | `tpat3_mock_70` ไม่มีชุดข้อสอบจริง 70 ข้อ แอบ fallback ดึง 25 ข้อมาหลอกผู้ใช้ | โครงสร้างสอบ TPAT3 70 ข้อไม่สมบูรณ์ หลอกตาผู้เรียน | สร้างชุดข้อสอบ `tpat3_blueprint_70.yaml` ฉบับสมบูรณ์ 70 ข้อ ครบทั้ง 5 ด้านตามพิมพ์เขียวจริง |
| **ROAST-04** | **HIGH** | Mock Exam สอบเสร็จแล้วไม่ส่งผลข้อที่ผิดเข้า Spaced Repetition | จุดอ่อนจากการสอบจำลองไม่ถูกนำมาทบทวนในวงจรติวรายวัน | ปรับ `submit_mock_exam` ให้บันทึก attempts และป้อนข้อที่ตอบผิดเข้า `review_queue` อัตโนมัติ |
| **ROAST-05** | **MEDIUM** | Navbar เบียดเสียด 13 รายการ แตกแถวล้นจอในแท็บเล็ตและมือถือ | หน้าเว็บพัง เมนูเกะกะ navigation แย่ | จัดกลุ่มเมนูเป็น 4 หมวดหลัก (ติวประจำวัน, ทำโจทย์, วิเคราะห์ผล, จัดการระบบ) พร้อมเมนู Dropdown / Responsive Grid |
| **ROAST-06** | **MEDIUM** | โหลด Google Fonts ภายนอก ทำลายสัญญา Local-First 100% Offline | เน็ตช้าหรือออฟไลน์ หน้าเว็บจะค้างรอฟอนต์จากภายนอก | ตัด Google Fonts ออก และใช้ System Thai Font Stack (Leelawadee UI, Sarabun Local, Thonburi, Segoe UI) |
| **ROAST-07** | **MEDIUM** | คำว่า `confidence="guessing"` ใน `tutor_engine.py` ไม่ตรงกับ schema `'guessed'` | Spaced repetition ตีความความมั่นใจผิดพลาด | แก้ไขเป็น `'guessed'` ให้สอดคล้องกับ schema ทุกจุด |
| **ROAST-08** | **MEDIUM** | `reorder_topic_priority` ติดเดดล็อกเมื่อ `order_index` เท่ากัน | กดปุ่มเลื่อนขึ้น-ลงใน Roadmap แล้วลำดับไม่ขยับ | ปรับตรรกะให้ normalize `order_index` ใหม่ (1, 2, 3...) ก่อนทำ swap เมื่อตรวจพบค่าซ้ำ |
| **ROAST-09** | **LOW** | หน้า Dashboard ไม่เชื่อมโยงไปยัง Planner, Mock Exam, Progress | ผู้ใช้ไม่เห็นฟีเจอร์สำคัญในหน้าแรก | เพิ่ม Quick Action Cards และสถิติ Mock Exam ล่าสุดลงใน `dashboard.html` |
| **ROAST-10** | **LOW** | `formula_reviews` เก็บข้อมูลแต่ไม่เคยคำนวณ `next_review_at` หรือนำมานับใน Planner | บัตรสูตรกลายเป็นระบบโดดเดี่ยว | ปรับการบันทึกสูตรให้คำนวณวันทบทวน และเชื่อมข้อมูลความจำสูตรเข้ากับ Dashboard |

---

## 3. แผนการลงมือแก้ไข (Action Plan)

1. **Fix 1 (Content Integration):** ปรับปรุง `content_loader.py` ให้แปลง `PastPaperQuestion` เป็น `Question` ในคลังโจทย์หลักอัตโนมัติ ทำให้ผู้เรียนมีโจทย์พร้อมฝึกทันที 87+ ข้อ
2. **Fix 2 (Prerequisites Resolution):** เพิ่มไฟล์เนื้อหาโจทย์ `physics/vectors.yaml` และ `math/algebra_basics.yaml` และ seed เข้าสู่ `topic_priorities` ปลดล็อกวงจรการเรียน Kinematics และ Algebra อย่างสมบูรณ์
3. **Fix 3 (Authentic 70-Item TPAT3 Blueprint):** สร้าง `content/past_papers/tpat3_blueprint_70.yaml` ให้มีข้อสอบครบ 70 ข้อ 5 พาร์ท 100 คะแนนเต็ม
4. **Fix 4 (Mock Exam & Spaced Repetition Link):** เชื่อมโยงข้อสอบที่ทำผิดใน Mock Exam เข้าสู่ `attempts` และ `review_queue` อัตโนมัติ
5. **Fix 5 (Responsive Clutter-Free Navbar):** จัดระเบียบ Navbar ใน `base.html` ให้เป็นกลุ่มหมวดหมู่สวยงาม ไม่แตกแถวบนแท็บเล็ตและมือถือ
6. **Fix 6 (True Offline Fonts):** นำ Google Fonts CDN ออกจาก `base.html` ใช้ Native System Fonts 100%
7. **Fix 7 (Bugfix Confidence & Reorder):** แก้ไข `'guessing'` -> `'guessed'` และปลดล็อก Deadlock ใน `reorder_topic_priority`
8. **Fix 8 (Dashboard Upgrade):** เพิ่มวิดเจ็ตตารางติว, จำลองสอบ, และประเมินความพร้อมสอบใน `dashboard.html`
9. **Fix 9 (Testing & Verification):** เขียนชุดทดสอบใหม่ใน `tests/test_roast_remediation.py` และรัน pytest ครบทุกข้อ 100%
