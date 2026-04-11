CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE user_role AS ENUM ('student', 'faculty', 'admin');
CREATE TYPE approval_status AS ENUM ('PENDING', 'APPROVED', 'REJECTED');
CREATE TYPE attendance_status AS ENUM ('PRESENT', 'ABSENT', 'LATE');
CREATE TYPE booking_status AS ENUM ('PENDING', 'APPROVED', 'REJECTED', 'RETURNED');
CREATE TYPE item_type AS ENUM ('LOST', 'FOUND');
CREATE TYPE item_status AS ENUM ('OPEN', 'CLAIMED', 'RESOLVED');
CREATE TYPE claim_status AS ENUM ('PENDING', 'APPROVED', 'REJECTED');
CREATE TYPE payment_status AS ENUM ('PENDING', 'SUCCESS', 'FAILED', 'REFUNDED');
CREATE TYPE room_type AS ENUM ('classroom', 'computer_lab', 'science_lab', 'lecture_hall', 'library');
CREATE TYPE occupancy_status AS ENUM ('available', 'almost_full', 'occupied');
CREATE TYPE day_of_week AS ENUM ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday');
CREATE TYPE lecture_type AS ENUM ('LECTURE', 'LAB', 'PRACTICAL', 'TUTORIAL');
CREATE TYPE notification_type AS ENUM ('ANNOUNCEMENT', 'ALERT', 'MESSAGE', 'REMINDER');
CREATE TYPE submission_status AS ENUM ('PENDING', 'SUBMITTED', 'LATE', 'GRADED');
CREATE TYPE fee_type AS ENUM ('TUITION', 'HOSTEL', 'LIBRARY', 'EXAM', 'SPORTS', 'LAB', 'OTHER');
CREATE TYPE grade_value AS ENUM ('O', 'A+', 'A', 'B+', 'B', 'C', 'D', 'F', 'AB');

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE departments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(200) NOT NULL UNIQUE,
  code VARCHAR(20) NOT NULL UNIQUE,
  hod_name VARCHAR(200),
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_departments_updated_at BEFORE UPDATE ON departments FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  role user_role NOT NULL DEFAULT 'student',
  full_name VARCHAR(200) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  phone VARCHAR(20),
  avatar_url TEXT,
  department_id UUID REFERENCES departments(id) ON DELETE SET NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_profiles_updated_at BEFORE UPDATE ON profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE students (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  profile_id UUID NOT NULL UNIQUE REFERENCES profiles(id) ON DELETE CASCADE,
  roll_number VARCHAR(50) NOT NULL UNIQUE,
  student_id VARCHAR(50) NOT NULL UNIQUE,
  department_id UUID NOT NULL REFERENCES departments(id) ON DELETE RESTRICT,
  year INT NOT NULL CHECK (year BETWEEN 1 AND 4),
  semester INT NOT NULL CHECK (semester BETWEEN 1 AND 8),
  batch VARCHAR(20),
  admission_date DATE,
  cgpa DECIMAL(4,2) DEFAULT 0.00 CHECK (cgpa >= 0 AND cgpa <= 10),
  class_rank INT,
  address TEXT,
  guardian_name VARCHAR(200),
  guardian_phone VARCHAR(20),
  guardian_relation VARCHAR(50),
  fees_status VARCHAR(50) DEFAULT 'PENDING',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_students_updated_at BEFORE UPDATE ON students FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE faculty (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  profile_id UUID NOT NULL UNIQUE REFERENCES profiles(id) ON DELETE CASCADE,
  faculty_id VARCHAR(50) NOT NULL UNIQUE,
  department_id UUID NOT NULL REFERENCES departments(id) ON DELETE RESTRICT,
  designation VARCHAR(100),
  qualification VARCHAR(200),
  specialization VARCHAR(200),
  join_date DATE,
  salary DECIMAL(12,2),
  experience_years INT DEFAULT 0,
  rating VARCHAR(10),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_faculty_updated_at BEFORE UPDATE ON faculty FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE subjects (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(200) NOT NULL,
  code VARCHAR(20) NOT NULL UNIQUE,
  department_id UUID NOT NULL REFERENCES departments(id) ON DELETE RESTRICT,
  semester INT NOT NULL CHECK (semester BETWEEN 1 AND 8),
  credits INT NOT NULL DEFAULT 3,
  subject_type lecture_type DEFAULT 'LECTURE',
  max_marks INT DEFAULT 100,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_subjects_updated_at BEFORE UPDATE ON subjects FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE faculty_subjects (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  faculty_id UUID NOT NULL REFERENCES faculty(id) ON DELETE CASCADE,
  subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
  academic_year VARCHAR(20),
  is_primary BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(faculty_id, subject_id, academic_year)
);

CREATE TRIGGER trg_faculty_subjects_updated_at BEFORE UPDATE ON faculty_subjects FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE classrooms (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(200) NOT NULL,
  room_type room_type NOT NULL DEFAULT 'classroom',
  building VARCHAR(200) NOT NULL,
  floor INT NOT NULL DEFAULT 0,
  total_seats INT NOT NULL DEFAULT 60,
  available_seats INT NOT NULL DEFAULT 60,
  status occupancy_status DEFAULT 'available',
  current_faculty_id UUID REFERENCES faculty(id) ON DELETE SET NULL,
  current_subject VARCHAR(200),
  current_time_slot VARCHAR(100),
  equipment TEXT[] DEFAULT '{}',
  upcoming_info VARCHAR(300),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_classrooms_updated_at BEFORE UPDATE ON classrooms FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE classroom_bookings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  classroom_id UUID NOT NULL REFERENCES classrooms(id) ON DELETE CASCADE,
  booked_by UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  purpose VARCHAR(300),
  booking_date DATE NOT NULL,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  status approval_status DEFAULT 'PENDING',
  approved_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_classroom_bookings_updated_at BEFORE UPDATE ON classroom_bookings FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE timetable_slots (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  department_id UUID NOT NULL REFERENCES departments(id) ON DELETE CASCADE,
  subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
  faculty_id UUID NOT NULL REFERENCES faculty(id) ON DELETE CASCADE,
  classroom_id UUID REFERENCES classrooms(id) ON DELETE SET NULL,
  day day_of_week NOT NULL,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  lecture_type lecture_type DEFAULT 'LECTURE',
  semester INT NOT NULL,
  year INT NOT NULL,
  academic_year VARCHAR(20),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_timetable_slots_updated_at BEFORE UPDATE ON timetable_slots FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE qr_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  timetable_slot_id UUID NOT NULL REFERENCES timetable_slots(id) ON DELETE CASCADE,
  faculty_id UUID NOT NULL REFERENCES faculty(id) ON DELETE CASCADE,
  subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
  qr_code_data TEXT NOT NULL UNIQUE,
  qr_image_url TEXT,
  session_date DATE NOT NULL,
  valid_from TIMESTAMPTZ NOT NULL,
  valid_until TIMESTAMPTZ NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_qr_sessions_updated_at BEFORE UPDATE ON qr_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE attendance (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  faculty_id UUID NOT NULL REFERENCES faculty(id) ON DELETE CASCADE,
  subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
  timetable_slot_id UUID REFERENCES timetable_slots(id) ON DELETE SET NULL,
  qr_session_id UUID REFERENCES qr_sessions(id) ON DELETE SET NULL,
  attendance_date DATE NOT NULL,
  attendance_time TIMESTAMPTZ DEFAULT NOW(),
  status attendance_status NOT NULL DEFAULT 'PRESENT',
  remarks TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(student_id, subject_id, attendance_date, timetable_slot_id)
);

CREATE TRIGGER trg_attendance_updated_at BEFORE UPDATE ON attendance FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE attendance_summary (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
  total_classes INT DEFAULT 0,
  present_count INT DEFAULT 0,
  absent_count INT DEFAULT 0,
  late_count INT DEFAULT 0,
  percentage DECIMAL(5,2) DEFAULT 0.00,
  month INT,
  year INT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(student_id, subject_id, month, year)
);

CREATE TRIGGER trg_attendance_summary_updated_at BEFORE UPDATE ON attendance_summary FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE sports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(200) NOT NULL,
  category VARCHAR(100),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_sports_updated_at BEFORE UPDATE ON sports FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE equipment (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  equipment_name VARCHAR(200) NOT NULL,
  category VARCHAR(100) NOT NULL,
  quantity INT NOT NULL DEFAULT 1,
  available_quantity INT NOT NULL DEFAULT 1,
  sport_id UUID REFERENCES sports(id) ON DELETE SET NULL,
  condition VARCHAR(50) DEFAULT 'GOOD',
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_equipment_updated_at BEFORE UPDATE ON equipment FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE equipment_bookings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  equipment_id UUID NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
  student_name VARCHAR(150) NOT NULL,
  roll_number VARCHAR(50) NOT NULL,
  department VARCHAR(100) NOT NULL,
  booking_date DATE NOT NULL,
  time_slot VARCHAR(100) NOT NULL,
  quantity INT NOT NULL DEFAULT 1,
  contact_number VARCHAR(20),
  status booking_status DEFAULT 'PENDING',
  approved_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
  return_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_equipment_bookings_updated_at BEFORE UPDATE ON equipment_bookings FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE turfs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  turf_name VARCHAR(200) NOT NULL,
  location VARCHAR(300),
  sport_id UUID REFERENCES sports(id) ON DELETE SET NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_turfs_updated_at BEFORE UPDATE ON turfs FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE turf_bookings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  turf_id UUID NOT NULL REFERENCES turfs(id) ON DELETE CASCADE,
  student_name VARCHAR(150) NOT NULL,
  roll_number VARCHAR(50) NOT NULL,
  department VARCHAR(100) NOT NULL,
  booking_date DATE NOT NULL,
  time_slot VARCHAR(100) NOT NULL,
  contact VARCHAR(20),
  status approval_status DEFAULT 'PENDING',
  approved_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_turf_bookings_updated_at BEFORE UPDATE ON turf_bookings FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE lost_found_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  item_type item_type NOT NULL,
  reporter_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  reporter_name VARCHAR(100) NOT NULL,
  roll_number VARCHAR(20),
  department VARCHAR(100),
  item_name VARCHAR(200) NOT NULL,
  description TEXT NOT NULL,
  location VARCHAR(200) NOT NULL,
  item_date DATE NOT NULL,
  contact VARCHAR(20),
  image_url TEXT,
  status item_status DEFAULT 'OPEN',
  admin_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_lost_found_items_updated_at BEFORE UPDATE ON lost_found_items FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE claims (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  item_id UUID NOT NULL REFERENCES lost_found_items(id) ON DELETE CASCADE,
  claimant_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  claimant_name VARCHAR(100) NOT NULL,
  roll_number VARCHAR(20),
  details TEXT NOT NULL,
  proof_image_url TEXT,
  status claim_status DEFAULT 'PENDING',
  reviewed_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_claims_updated_at BEFORE UPDATE ON claims FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE assignments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
  faculty_id UUID NOT NULL REFERENCES faculty(id) ON DELETE CASCADE,
  title VARCHAR(300) NOT NULL,
  description TEXT,
  file_url TEXT,
  max_marks INT DEFAULT 100,
  deadline TIMESTAMPTZ NOT NULL,
  semester INT NOT NULL,
  year INT NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_assignments_updated_at BEFORE UPDATE ON assignments FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE student_submissions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  assignment_id UUID NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
  student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  file_url TEXT,
  submitted_at TIMESTAMPTZ DEFAULT NOW(),
  marks_obtained DECIMAL(5,2),
  feedback TEXT,
  status submission_status DEFAULT 'PENDING',
  plagiarism_score DECIMAL(5,2),
  graded_by UUID REFERENCES faculty(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(assignment_id, student_id)
);

CREATE TRIGGER trg_student_submissions_updated_at BEFORE UPDATE ON student_submissions FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE notes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
  faculty_id UUID NOT NULL REFERENCES faculty(id) ON DELETE CASCADE,
  title VARCHAR(300) NOT NULL,
  description TEXT,
  file_url TEXT,
  file_type VARCHAR(20),
  file_size_bytes BIGINT,
  semester INT NOT NULL,
  year INT NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_notes_updated_at BEFORE UPDATE ON notes FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE marks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
  semester INT NOT NULL,
  internal_marks DECIMAL(5,2) DEFAULT 0,
  external_marks DECIMAL(5,2) DEFAULT 0,
  total_marks DECIMAL(5,2) DEFAULT 0,
  max_internal INT DEFAULT 40,
  max_external INT DEFAULT 60,
  max_total INT DEFAULT 100,
  grade grade_value,
  grade_points DECIMAL(4,2),
  credits INT DEFAULT 3,
  academic_year VARCHAR(20),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(student_id, subject_id, semester, academic_year)
);

CREATE TRIGGER trg_marks_updated_at BEFORE UPDATE ON marks FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE semester_results (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  semester INT NOT NULL,
  gpa DECIMAL(4,2) DEFAULT 0.00,
  cgpa DECIMAL(4,2) DEFAULT 0.00,
  total_credits INT DEFAULT 0,
  earned_credits INT DEFAULT 0,
  class_rank INT,
  academic_year VARCHAR(20),
  is_published BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(student_id, semester, academic_year)
);

CREATE TRIGGER trg_semester_results_updated_at BEFORE UPDATE ON semester_results FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE fees (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  fee_type fee_type NOT NULL,
  description VARCHAR(300),
  amount DECIMAL(12,2) NOT NULL,
  due_date DATE NOT NULL,
  academic_year VARCHAR(20) NOT NULL,
  semester INT,
  is_paid BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_fees_updated_at BEFORE UPDATE ON fees FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE payments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  fee_id UUID REFERENCES fees(id) ON DELETE SET NULL,
  amount DECIMAL(12,2) NOT NULL,
  razorpay_payment_id VARCHAR(100),
  razorpay_order_id VARCHAR(100),
  razorpay_signature VARCHAR(300),
  transaction_id VARCHAR(100) UNIQUE,
  payment_method VARCHAR(50),
  status payment_status DEFAULT 'PENDING',
  receipt_url TEXT,
  payment_date TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_payments_updated_at BEFORE UPDATE ON payments FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE payment_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  payment_id UUID NOT NULL REFERENCES payments(id) ON DELETE CASCADE,
  event VARCHAR(100) NOT NULL,
  details JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  sender_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
  title VARCHAR(300) NOT NULL,
  message TEXT NOT NULL,
  notification_type notification_type DEFAULT 'ANNOUNCEMENT',
  target_role user_role,
  target_department_id UUID REFERENCES departments(id) ON DELETE SET NULL,
  target_year INT,
  is_global BOOLEAN DEFAULT FALSE,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_notifications_updated_at BEFORE UPDATE ON notifications FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE user_notifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  notification_id UUID NOT NULL REFERENCES notifications(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  is_read BOOLEAN DEFAULT FALSE,
  read_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(notification_id, user_id)
);

CREATE TABLE system_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
  action VARCHAR(200) NOT NULL,
  entity_type VARCHAR(100),
  entity_id UUID,
  details JSONB,
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE activity_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  action VARCHAR(200) NOT NULL,
  module VARCHAR(100),
  description TEXT,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE admin_approvals (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  admin_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
  entity_type VARCHAR(100) NOT NULL,
  entity_id UUID NOT NULL,
  status approval_status DEFAULT 'PENDING',
  remarks TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER trg_admin_approvals_updated_at BEFORE UPDATE ON admin_approvals FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE INDEX idx_profiles_role ON profiles(role);
CREATE INDEX idx_profiles_department ON profiles(department_id);
CREATE INDEX idx_profiles_email ON profiles(email);

CREATE INDEX idx_students_profile ON students(profile_id);
CREATE INDEX idx_students_department ON students(department_id);
CREATE INDEX idx_students_roll ON students(roll_number);
CREATE INDEX idx_students_year_sem ON students(year, semester);

CREATE INDEX idx_faculty_profile ON faculty(profile_id);
CREATE INDEX idx_faculty_department ON faculty(department_id);

CREATE INDEX idx_subjects_department ON subjects(department_id);
CREATE INDEX idx_subjects_semester ON subjects(semester);
CREATE INDEX idx_subjects_code ON subjects(code);

CREATE INDEX idx_faculty_subjects_faculty ON faculty_subjects(faculty_id);
CREATE INDEX idx_faculty_subjects_subject ON faculty_subjects(subject_id);

CREATE INDEX idx_timetable_dept ON timetable_slots(department_id);
CREATE INDEX idx_timetable_faculty ON timetable_slots(faculty_id);
CREATE INDEX idx_timetable_day ON timetable_slots(day);
CREATE INDEX idx_timetable_semester_year ON timetable_slots(semester, year);

CREATE INDEX idx_qr_sessions_faculty ON qr_sessions(faculty_id);
CREATE INDEX idx_qr_sessions_date ON qr_sessions(session_date);
CREATE INDEX idx_qr_sessions_active ON qr_sessions(is_active);

CREATE INDEX idx_attendance_student ON attendance(student_id);
CREATE INDEX idx_attendance_faculty ON attendance(faculty_id);
CREATE INDEX idx_attendance_subject ON attendance(subject_id);
CREATE INDEX idx_attendance_date ON attendance(attendance_date);
CREATE INDEX idx_attendance_qr ON attendance(qr_session_id);

CREATE INDEX idx_attendance_summary_student ON attendance_summary(student_id);
CREATE INDEX idx_attendance_summary_subject ON attendance_summary(subject_id);

CREATE INDEX idx_equipment_bookings_student ON equipment_bookings(student_id);
CREATE INDEX idx_equipment_bookings_equipment ON equipment_bookings(equipment_id);
CREATE INDEX idx_equipment_bookings_date ON equipment_bookings(booking_date);
CREATE INDEX idx_equipment_bookings_status ON equipment_bookings(status);

CREATE INDEX idx_turf_bookings_student ON turf_bookings(student_id);
CREATE INDEX idx_turf_bookings_turf ON turf_bookings(turf_id);
CREATE INDEX idx_turf_bookings_date ON turf_bookings(booking_date);
CREATE INDEX idx_turf_bookings_status ON turf_bookings(status);

CREATE INDEX idx_lost_found_type ON lost_found_items(item_type);
CREATE INDEX idx_lost_found_status ON lost_found_items(status);
CREATE INDEX idx_lost_found_reporter ON lost_found_items(reporter_id);
CREATE INDEX idx_lost_found_date ON lost_found_items(item_date);

CREATE INDEX idx_claims_item ON claims(item_id);
CREATE INDEX idx_claims_claimant ON claims(claimant_id);
CREATE INDEX idx_claims_status ON claims(status);

CREATE INDEX idx_classrooms_type ON classrooms(room_type);
CREATE INDEX idx_classrooms_status ON classrooms(status);
CREATE INDEX idx_classrooms_building ON classrooms(building);

CREATE INDEX idx_classroom_bookings_room ON classroom_bookings(classroom_id);
CREATE INDEX idx_classroom_bookings_date ON classroom_bookings(booking_date);

CREATE INDEX idx_assignments_subject ON assignments(subject_id);
CREATE INDEX idx_assignments_faculty ON assignments(faculty_id);
CREATE INDEX idx_assignments_deadline ON assignments(deadline);

CREATE INDEX idx_submissions_assignment ON student_submissions(assignment_id);
CREATE INDEX idx_submissions_student ON student_submissions(student_id);
CREATE INDEX idx_submissions_status ON student_submissions(status);

CREATE INDEX idx_notes_subject ON notes(subject_id);
CREATE INDEX idx_notes_faculty ON notes(faculty_id);

CREATE INDEX idx_marks_student ON marks(student_id);
CREATE INDEX idx_marks_subject ON marks(subject_id);
CREATE INDEX idx_marks_semester ON marks(semester);

CREATE INDEX idx_semester_results_student ON semester_results(student_id);
CREATE INDEX idx_semester_results_semester ON semester_results(semester);

CREATE INDEX idx_fees_student ON fees(student_id);
CREATE INDEX idx_fees_due_date ON fees(due_date);
CREATE INDEX idx_fees_paid ON fees(is_paid);

CREATE INDEX idx_payments_student ON payments(student_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_razorpay ON payments(razorpay_payment_id);
CREATE INDEX idx_payments_transaction ON payments(transaction_id);

CREATE INDEX idx_notifications_type ON notifications(notification_type);
CREATE INDEX idx_notifications_target_role ON notifications(target_role);
CREATE INDEX idx_notifications_sender ON notifications(sender_id);

CREATE INDEX idx_user_notifications_user ON user_notifications(user_id);
CREATE INDEX idx_user_notifications_read ON user_notifications(is_read);

CREATE INDEX idx_system_logs_user ON system_logs(user_id);
CREATE INDEX idx_system_logs_action ON system_logs(action);
CREATE INDEX idx_system_logs_created ON system_logs(created_at);

CREATE INDEX idx_activity_logs_user ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_module ON activity_logs(module);

CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO profiles (id, role, full_name, email)
  VALUES (
    NEW.id,
    COALESCE((NEW.raw_user_meta_data->>'role')::user_role, 'student'),
    COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
    NEW.email
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();

CREATE OR REPLACE FUNCTION get_user_role(user_uuid UUID)
RETURNS user_role AS $$
  SELECT role FROM profiles WHERE id = user_uuid;
$$ LANGUAGE sql SECURITY DEFINER STABLE;

CREATE OR REPLACE FUNCTION is_admin(user_uuid UUID)
RETURNS BOOLEAN AS $$
  SELECT EXISTS(SELECT 1 FROM profiles WHERE id = user_uuid AND role = 'admin');
$$ LANGUAGE sql SECURITY DEFINER STABLE;

CREATE OR REPLACE FUNCTION is_faculty(user_uuid UUID)
RETURNS BOOLEAN AS $$
  SELECT EXISTS(SELECT 1 FROM profiles WHERE id = user_uuid AND role = 'faculty');
$$ LANGUAGE sql SECURITY DEFINER STABLE;

CREATE OR REPLACE FUNCTION is_student(user_uuid UUID)
RETURNS BOOLEAN AS $$
  SELECT EXISTS(SELECT 1 FROM profiles WHERE id = user_uuid AND role = 'student');
$$ LANGUAGE sql SECURITY DEFINER STABLE;

CREATE OR REPLACE FUNCTION calculate_attendance_percentage(p_student_id UUID, p_subject_id UUID)
RETURNS DECIMAL AS $$
DECLARE
  total INT;
  present INT;
BEGIN
  SELECT COUNT(*) INTO total FROM attendance WHERE student_id = p_student_id AND subject_id = p_subject_id;
  SELECT COUNT(*) INTO present FROM attendance WHERE student_id = p_student_id AND subject_id = p_subject_id AND status = 'PRESENT';
  IF total = 0 THEN RETURN 0; END IF;
  RETURN ROUND((present::DECIMAL / total::DECIMAL) * 100, 2);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

CREATE OR REPLACE FUNCTION log_activity()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO activity_logs (user_id, action, module, description, metadata)
  VALUES (
    auth.uid(),
    TG_ARGV[0],
    TG_ARGV[1],
    TG_ARGV[2],
    jsonb_build_object('table', TG_TABLE_NAME, 'operation', TG_OP, 'record_id', COALESCE(NEW.id::TEXT, OLD.id::TEXT))
  );
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

ALTER TABLE departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE faculty ENABLE ROW LEVEL SECURITY;
ALTER TABLE subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE faculty_subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE classrooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE classroom_bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE timetable_slots ENABLE ROW LEVEL SECURITY;
ALTER TABLE qr_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance_summary ENABLE ROW LEVEL SECURITY;
ALTER TABLE sports ENABLE ROW LEVEL SECURITY;
ALTER TABLE equipment ENABLE ROW LEVEL SECURITY;
ALTER TABLE equipment_bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE turfs ENABLE ROW LEVEL SECURITY;
ALTER TABLE turf_bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE lost_found_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE claims ENABLE ROW LEVEL SECURITY;
ALTER TABLE assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE marks ENABLE ROW LEVEL SECURITY;
ALTER TABLE semester_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE fees ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_approvals ENABLE ROW LEVEL SECURITY;

CREATE POLICY "departments_read_all" ON departments FOR SELECT USING (true);
CREATE POLICY "departments_admin_manage" ON departments FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "profiles_read_own" ON profiles FOR SELECT USING (id = auth.uid() OR is_admin(auth.uid()));
CREATE POLICY "profiles_update_own" ON profiles FOR UPDATE USING (id = auth.uid());
CREATE POLICY "profiles_admin_manage" ON profiles FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "students_read_own" ON students FOR SELECT USING (profile_id = auth.uid() OR is_admin(auth.uid()) OR is_faculty(auth.uid()));
CREATE POLICY "students_update_own" ON students FOR UPDATE USING (profile_id = auth.uid());
CREATE POLICY "students_admin_manage" ON students FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "faculty_read_all" ON faculty FOR SELECT USING (true);
CREATE POLICY "faculty_update_own" ON faculty FOR UPDATE USING (profile_id = auth.uid());
CREATE POLICY "faculty_admin_manage" ON faculty FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "subjects_read_all" ON subjects FOR SELECT USING (true);
CREATE POLICY "subjects_admin_manage" ON subjects FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "faculty_subjects_read_all" ON faculty_subjects FOR SELECT USING (true);
CREATE POLICY "faculty_subjects_admin_manage" ON faculty_subjects FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "classrooms_read_all" ON classrooms FOR SELECT USING (true);
CREATE POLICY "classrooms_admin_manage" ON classrooms FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "classroom_bookings_read" ON classroom_bookings FOR SELECT USING (booked_by = auth.uid() OR is_admin(auth.uid()) OR is_faculty(auth.uid()));
CREATE POLICY "classroom_bookings_insert" ON classroom_bookings FOR INSERT WITH CHECK (booked_by = auth.uid());
CREATE POLICY "classroom_bookings_admin_manage" ON classroom_bookings FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "timetable_read_all" ON timetable_slots FOR SELECT USING (true);
CREATE POLICY "timetable_admin_manage" ON timetable_slots FOR ALL USING (is_admin(auth.uid()));
CREATE POLICY "timetable_faculty_manage" ON timetable_slots FOR ALL USING (
  EXISTS(SELECT 1 FROM faculty WHERE faculty.id = timetable_slots.faculty_id AND faculty.profile_id = auth.uid())
);

CREATE POLICY "qr_sessions_read" ON qr_sessions FOR SELECT USING (true);
CREATE POLICY "qr_sessions_faculty_manage" ON qr_sessions FOR INSERT WITH CHECK (
  EXISTS(SELECT 1 FROM faculty WHERE faculty.id = qr_sessions.faculty_id AND faculty.profile_id = auth.uid())
);
CREATE POLICY "qr_sessions_faculty_update" ON qr_sessions FOR UPDATE USING (
  EXISTS(SELECT 1 FROM faculty WHERE faculty.id = qr_sessions.faculty_id AND faculty.profile_id = auth.uid())
);
CREATE POLICY "qr_sessions_admin_manage" ON qr_sessions FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "attendance_student_read_own" ON attendance FOR SELECT USING (
  EXISTS(SELECT 1 FROM students WHERE students.id = attendance.student_id AND students.profile_id = auth.uid())
  OR is_faculty(auth.uid())
  OR is_admin(auth.uid())
);
CREATE POLICY "attendance_student_insert" ON attendance FOR INSERT WITH CHECK (
  EXISTS(SELECT 1 FROM students WHERE students.id = attendance.student_id AND students.profile_id = auth.uid())
);
CREATE POLICY "attendance_faculty_manage" ON attendance FOR ALL USING (
  EXISTS(SELECT 1 FROM faculty WHERE faculty.id = attendance.faculty_id AND faculty.profile_id = auth.uid())
);
CREATE POLICY "attendance_admin_manage" ON attendance FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "attendance_summary_read" ON attendance_summary FOR SELECT USING (
  EXISTS(SELECT 1 FROM students WHERE students.id = attendance_summary.student_id AND students.profile_id = auth.uid())
  OR is_faculty(auth.uid())
  OR is_admin(auth.uid())
);
CREATE POLICY "attendance_summary_admin_manage" ON attendance_summary FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "sports_read_all" ON sports FOR SELECT USING (true);
CREATE POLICY "sports_admin_manage" ON sports FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "equipment_read_all" ON equipment FOR SELECT USING (true);
CREATE POLICY "equipment_admin_manage" ON equipment FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "equipment_bookings_read" ON equipment_bookings FOR SELECT USING (
  EXISTS(SELECT 1 FROM students WHERE students.id = equipment_bookings.student_id AND students.profile_id = auth.uid())
  OR is_admin(auth.uid())
);
CREATE POLICY "equipment_bookings_insert" ON equipment_bookings FOR INSERT WITH CHECK (
  EXISTS(SELECT 1 FROM students WHERE students.id = equipment_bookings.student_id AND students.profile_id = auth.uid())
);
CREATE POLICY "equipment_bookings_admin_manage" ON equipment_bookings FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "turfs_read_all" ON turfs FOR SELECT USING (true);
CREATE POLICY "turfs_admin_manage" ON turfs FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "turf_bookings_read" ON turf_bookings FOR SELECT USING (
  EXISTS(SELECT 1 FROM students WHERE students.id = turf_bookings.student_id AND students.profile_id = auth.uid())
  OR is_admin(auth.uid())
);
CREATE POLICY "turf_bookings_insert" ON turf_bookings FOR INSERT WITH CHECK (
  EXISTS(SELECT 1 FROM students WHERE students.id = turf_bookings.student_id AND students.profile_id = auth.uid())
);
CREATE POLICY "turf_bookings_admin_manage" ON turf_bookings FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "lost_found_read_all" ON lost_found_items FOR SELECT USING (true);
CREATE POLICY "lost_found_insert" ON lost_found_items FOR INSERT WITH CHECK (reporter_id = auth.uid());
CREATE POLICY "lost_found_update_own" ON lost_found_items FOR UPDATE USING (reporter_id = auth.uid());
CREATE POLICY "lost_found_admin_manage" ON lost_found_items FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "claims_read" ON claims FOR SELECT USING (claimant_id = auth.uid() OR is_admin(auth.uid()));
CREATE POLICY "claims_insert" ON claims FOR INSERT WITH CHECK (claimant_id = auth.uid());
CREATE POLICY "claims_admin_manage" ON claims FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "assignments_read_all" ON assignments FOR SELECT USING (true);
CREATE POLICY "assignments_faculty_manage" ON assignments FOR ALL USING (
  EXISTS(SELECT 1 FROM faculty WHERE faculty.id = assignments.faculty_id AND faculty.profile_id = auth.uid())
);
CREATE POLICY "assignments_admin_manage" ON assignments FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "submissions_student_read_own" ON student_submissions FOR SELECT USING (
  EXISTS(SELECT 1 FROM students WHERE students.id = student_submissions.student_id AND students.profile_id = auth.uid())
  OR is_faculty(auth.uid())
  OR is_admin(auth.uid())
);
CREATE POLICY "submissions_student_insert" ON student_submissions FOR INSERT WITH CHECK (
  EXISTS(SELECT 1 FROM students WHERE students.id = student_submissions.student_id AND students.profile_id = auth.uid())
);
CREATE POLICY "submissions_faculty_manage" ON student_submissions FOR UPDATE USING (is_faculty(auth.uid()));
CREATE POLICY "submissions_admin_manage" ON student_submissions FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "notes_read_all" ON notes FOR SELECT USING (true);
CREATE POLICY "notes_faculty_manage" ON notes FOR ALL USING (
  EXISTS(SELECT 1 FROM faculty WHERE faculty.id = notes.faculty_id AND faculty.profile_id = auth.uid())
);
CREATE POLICY "notes_admin_manage" ON notes FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "marks_student_read_own" ON marks FOR SELECT USING (
  EXISTS(SELECT 1 FROM students WHERE students.id = marks.student_id AND students.profile_id = auth.uid())
  OR is_faculty(auth.uid())
  OR is_admin(auth.uid())
);
CREATE POLICY "marks_faculty_manage" ON marks FOR ALL USING (is_faculty(auth.uid()));
CREATE POLICY "marks_admin_manage" ON marks FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "semester_results_read" ON semester_results FOR SELECT USING (
  EXISTS(SELECT 1 FROM students WHERE students.id = semester_results.student_id AND students.profile_id = auth.uid())
  OR is_faculty(auth.uid())
  OR is_admin(auth.uid())
);
CREATE POLICY "semester_results_admin_manage" ON semester_results FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "fees_student_read_own" ON fees FOR SELECT USING (
  EXISTS(SELECT 1 FROM students WHERE students.id = fees.student_id AND students.profile_id = auth.uid())
  OR is_admin(auth.uid())
);
CREATE POLICY "fees_admin_manage" ON fees FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "payments_student_read_own" ON payments FOR SELECT USING (
  EXISTS(SELECT 1 FROM students WHERE students.id = payments.student_id AND students.profile_id = auth.uid())
  OR is_admin(auth.uid())
);
CREATE POLICY "payments_student_insert" ON payments FOR INSERT WITH CHECK (
  EXISTS(SELECT 1 FROM students WHERE students.id = payments.student_id AND students.profile_id = auth.uid())
);
CREATE POLICY "payments_admin_manage" ON payments FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "payment_logs_read" ON payment_logs FOR SELECT USING (
  EXISTS(
    SELECT 1 FROM payments p
    JOIN students s ON s.id = p.student_id
    WHERE p.id = payment_logs.payment_id AND s.profile_id = auth.uid()
  )
  OR is_admin(auth.uid())
);
CREATE POLICY "payment_logs_admin_manage" ON payment_logs FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "notifications_read_all" ON notifications FOR SELECT USING (true);
CREATE POLICY "notifications_faculty_insert" ON notifications FOR INSERT WITH CHECK (is_faculty(auth.uid()) OR is_admin(auth.uid()));
CREATE POLICY "notifications_admin_manage" ON notifications FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "user_notifications_read_own" ON user_notifications FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "user_notifications_update_own" ON user_notifications FOR UPDATE USING (user_id = auth.uid());
CREATE POLICY "user_notifications_admin_manage" ON user_notifications FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "system_logs_admin_only" ON system_logs FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "activity_logs_read_own" ON activity_logs FOR SELECT USING (user_id = auth.uid() OR is_admin(auth.uid()));
CREATE POLICY "activity_logs_admin_manage" ON activity_logs FOR ALL USING (is_admin(auth.uid()));

CREATE POLICY "admin_approvals_admin_only" ON admin_approvals FOR ALL USING (is_admin(auth.uid()));

INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES
  ('student-documents', 'student-documents', false, 10485760, ARRAY['application/pdf','image/jpeg','image/png','image/webp']),
  ('assignments', 'assignments', false, 52428800, ARRAY['application/pdf','application/msword','application/vnd.openxmlformats-officedocument.wordprocessingml.document','application/zip','text/plain']),
  ('notes', 'notes', false, 52428800, ARRAY['application/pdf','application/vnd.ms-powerpoint','application/vnd.openxmlformats-officedocument.presentationml.presentation','application/msword','application/vnd.openxmlformats-officedocument.wordprocessingml.document']),
  ('lost-found-images', 'lost-found-images', true, 5242880, ARRAY['image/jpeg','image/png','image/webp','image/gif']),
  ('qr-codes', 'qr-codes', true, 1048576, ARRAY['image/png','image/svg+xml','image/webp']),
  ('payment-receipts', 'payment-receipts', false, 5242880, ARRAY['application/pdf','image/jpeg','image/png']),
  ('profile-images', 'profile-images', true, 5242880, ARRAY['image/jpeg','image/png','image/webp'])
ON CONFLICT (id) DO NOTHING;

CREATE POLICY "profile_images_read" ON storage.objects FOR SELECT USING (bucket_id = 'profile-images');
CREATE POLICY "profile_images_upload" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'profile-images' AND auth.uid() IS NOT NULL);
CREATE POLICY "profile_images_update" ON storage.objects FOR UPDATE USING (bucket_id = 'profile-images' AND auth.uid()::TEXT = (storage.foldername(name))[1]);
CREATE POLICY "profile_images_delete" ON storage.objects FOR DELETE USING (bucket_id = 'profile-images' AND (auth.uid()::TEXT = (storage.foldername(name))[1] OR is_admin(auth.uid())));

CREATE POLICY "student_docs_read" ON storage.objects FOR SELECT USING (bucket_id = 'student-documents' AND (auth.uid()::TEXT = (storage.foldername(name))[1] OR is_admin(auth.uid())));
CREATE POLICY "student_docs_upload" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'student-documents' AND auth.uid()::TEXT = (storage.foldername(name))[1]);
CREATE POLICY "student_docs_delete" ON storage.objects FOR DELETE USING (bucket_id = 'student-documents' AND (auth.uid()::TEXT = (storage.foldername(name))[1] OR is_admin(auth.uid())));

CREATE POLICY "assignments_read" ON storage.objects FOR SELECT USING (bucket_id = 'assignments' AND auth.uid() IS NOT NULL);
CREATE POLICY "assignments_upload_faculty" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'assignments' AND (is_faculty(auth.uid()) OR is_student(auth.uid())));
CREATE POLICY "assignments_delete" ON storage.objects FOR DELETE USING (bucket_id = 'assignments' AND (is_faculty(auth.uid()) OR is_admin(auth.uid())));

CREATE POLICY "notes_read" ON storage.objects FOR SELECT USING (bucket_id = 'notes' AND auth.uid() IS NOT NULL);
CREATE POLICY "notes_upload_faculty" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'notes' AND is_faculty(auth.uid()));
CREATE POLICY "notes_delete" ON storage.objects FOR DELETE USING (bucket_id = 'notes' AND (is_faculty(auth.uid()) OR is_admin(auth.uid())));

CREATE POLICY "lost_found_images_read" ON storage.objects FOR SELECT USING (bucket_id = 'lost-found-images');
CREATE POLICY "lost_found_images_upload" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'lost-found-images' AND auth.uid() IS NOT NULL);
CREATE POLICY "lost_found_images_delete" ON storage.objects FOR DELETE USING (bucket_id = 'lost-found-images' AND is_admin(auth.uid()));

CREATE POLICY "qr_codes_read" ON storage.objects FOR SELECT USING (bucket_id = 'qr-codes');
CREATE POLICY "qr_codes_upload" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'qr-codes' AND is_faculty(auth.uid()));
CREATE POLICY "qr_codes_delete" ON storage.objects FOR DELETE USING (bucket_id = 'qr-codes' AND (is_faculty(auth.uid()) OR is_admin(auth.uid())));

CREATE POLICY "payment_receipts_read" ON storage.objects FOR SELECT USING (bucket_id = 'payment-receipts' AND (auth.uid()::TEXT = (storage.foldername(name))[1] OR is_admin(auth.uid())));
CREATE POLICY "payment_receipts_upload" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'payment-receipts' AND auth.uid() IS NOT NULL);

INSERT INTO departments (name, code) VALUES
  ('Computer Science Engineering', 'CSE'),
  ('Information Technology', 'IT'),
  ('Electronics & Telecommunication', 'EXTC'),
  ('Mechanical Engineering', 'MECH'),
  ('Civil Engineering', 'CIVIL'),
  ('First Year Engineering', 'FE');
