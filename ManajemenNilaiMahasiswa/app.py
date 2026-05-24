import json
import os
import streamlit as st

DATA_FILE = "students.json"

CREDENTIALS = {
    "admin": "admin123",
    "user": "user123",
}

GRADE_RULES = [
    (85, "A", "Memuaskan"),
    (70, "B", "Baik"),
    (60, "C", "Cukup"),
    (50, "D", "Kurang"),
    (0, "E", "Gagal"),
]


def load_students():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return []
    return []


def save_students(students):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(students, file, indent=2, ensure_ascii=False)


def calculate_final_grade(tugas, uts, uas):
    return round(tugas * 0.2 + uts * 0.35 + uas * 0.45, 2)


def grade_description(final_score):
    for threshold, grade, desc in GRADE_RULES:
        if final_score >= threshold:
            return grade, desc
    return "E", "Gagal"


def status_label(final_score):
    return "Lulus" if final_score >= 60 else "Tidak Lulus"


def authenticate(username, password):
    return CREDENTIALS.get(username) == password


def ensure_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "students" not in st.session_state:
        st.session_state.students = load_students()
    if "show_edit" not in st.session_state:
        st.session_state.show_edit = False
    if "edit_index" not in st.session_state:
        st.session_state.edit_index = None


def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.show_edit = False
    st.session_state.edit_index = None


def main_page():
    st.title("Sistem Nilai Mahasiswa")
    st.write("Aplikasi sederhana untuk menentukan nilai akhir, keterangan, dan CRUD data mahasiswa.")

    st.sidebar.header("Menu")
    menu = st.sidebar.radio("Pilih fitur", ["Dashboard", "Input Nilai", "Daftar Mahasiswa"])

    if menu == "Dashboard":
        st.subheader("Ringkasan")
        total = len(st.session_state.students)
        lulus = sum(1 for item in st.session_state.students if item["status"] == "Lulus")
        tidak_lulus = total - lulus

        st.metric("Total Mahasiswa", total)
        st.metric("Jumlah Lulus", lulus)
        st.metric("Jumlah Tidak Lulus", tidak_lulus)

        st.markdown("---")
        if total:
            st.dataframe(st.session_state.students)
        else:
            st.info("Belum ada data mahasiswa. Silakan tambahkan nilai.")

    if menu == "Input Nilai":
        st.subheader("Tambah atau Ubah Nilai Mahasiswa")
        with st.form("nilai_form"):
            nim = st.text_input("NIM")
            nama = st.text_input("Nama")
            tugas = st.number_input("Nilai Tugas", min_value=0.0, max_value=100.0, value=0.0)
            uts = st.number_input("Nilai UTS", min_value=0.0, max_value=100.0, value=0.0)
            uas = st.number_input("Nilai UAS", min_value=0.0, max_value=100.0, value=0.0)
            submitted = st.form_submit_button("Simpan")

        final_score = calculate_final_grade(tugas, uts, uas)
        grade, desc = grade_description(final_score)
        status = status_label(final_score)

        st.markdown("### Pratinjau Nilai")
        preview_cols = st.columns(4)
        preview_cols[0].metric("Nilai Akhir", final_score)
        preview_cols[1].metric("Grade", grade)
        preview_cols[2].metric("Keterangan", desc)
        preview_cols[3].metric("Status", status)

        if submitted:
            if not nim or not nama:
                st.error("NIM dan Nama harus diisi.")
            else:
                new_student = {
                    "nim": nim,
                    "nama": nama,
                    "tugas": tugas,
                    "uts": uts,
                    "uas": uas,
                    "nilai_akhir": final_score,
                    "grade": grade,
                    "keterangan": desc,
                    "status": status,
                }

                existing_index = next((i for i, item in enumerate(st.session_state.students) if item["nim"] == nim), None)
                if existing_index is not None:
                    st.session_state.students[existing_index] = new_student
                    st.success(f"Data mahasiswa dengan NIM {nim} berhasil diperbarui.")
                else:
                    st.session_state.students.append(new_student)
                    st.success(f"Data mahasiswa dengan NIM {nim} berhasil disimpan.")

                save_students(st.session_state.students)

    if menu == "Daftar Mahasiswa":
        st.subheader("Kelola Data Mahasiswa")
        if st.session_state.students:
            for idx, student in enumerate(st.session_state.students):
                with st.expander(f"{student['nim']} - {student['nama']}"):
                    st.write(f"**Nilai Tugas:** {student['tugas']}")
                    st.write(f"**Nilai UTS:** {student['uts']}")
                    st.write(f"**Nilai UAS:** {student['uas']}")
                    st.write(f"**Nilai Akhir:** {student['nilai_akhir']}")
                    st.write(f"**Grade:** {student['grade']} ({student['keterangan']})")
                    st.write(f"**Status:** {student['status']}")

                    cols = st.columns(2)
                    if cols[0].button("Edit", key=f"edit_{idx}"):
                        st.session_state.show_edit = True
                        st.session_state.edit_index = idx
                    if cols[1].button("Hapus", key=f"delete_{idx}"):
                        st.session_state.students.pop(idx)
                        save_students(st.session_state.students)
                        st.success("Data mahasiswa berhasil dihapus.")
                        st.rerun()

            if st.session_state.show_edit and st.session_state.edit_index is not None:
                student = st.session_state.students[st.session_state.edit_index]
                st.markdown("---")
                st.subheader("Edit Mahasiswa")
                with st.form("edit_form"):
                    nim_edit = st.text_input("NIM", value=student["nim"])
                    nama_edit = st.text_input("Nama", value=student["nama"])
                    tugas_edit = st.number_input("Nilai Tugas", min_value=0.0, max_value=100.0, value=student["tugas"])
                    uts_edit = st.number_input("Nilai UTS", min_value=0.0, max_value=100.0, value=student["uts"])
                    uas_edit = st.number_input("Nilai UAS", min_value=0.0, max_value=100.0, value=student["uas"])
                    submitted_edit = st.form_submit_button("Perbarui")

                if submitted_edit:
                    if not nim_edit or not nama_edit:
                        st.error("NIM dan Nama harus diisi.")
                    else:
                        final_score = calculate_final_grade(tugas_edit, uts_edit, uas_edit)
                        grade, desc = grade_description(final_score)
                        status = status_label(final_score)
                        st.session_state.students[st.session_state.edit_index] = {
                            "nim": nim_edit,
                            "nama": nama_edit,
                            "tugas": tugas_edit,
                            "uts": uts_edit,
                            "uas": uas_edit,
                            "nilai_akhir": final_score,
                            "grade": grade,
                            "keterangan": desc,
                            "status": status,
                        }
                        save_students(st.session_state.students)
                        st.success("Data mahasiswa berhasil diperbarui.")
                        st.session_state.show_edit = False
                        st.session_state.edit_index = None
                        st.rerun()
        else:
            st.info("Belum ada data mahasiswa. Silakan tambahkan di menu Input Nilai.")

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        logout()
        st.success("Berhasil logout.")
        st.rerun()


def login_page():
    st.title("Login Sistem Nilai Mahasiswa")
    st.write("Silakan login untuk mengakses aplikasi nilai mahasiswa.")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Masuk")

    if login_button:
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login berhasil, selamat datang {}!".format(username))
            st.rerun()
        else:
            st.error("Username atau password salah.")

    st.info("Gunakan username 'admin' dengan password 'admin123' atau username 'user' dengan password 'user123'.")


def main():
    ensure_session_state()
    if st.session_state.logged_in:
        main_page()
    else:
        login_page()


if __name__ == "__main__":
    main()
