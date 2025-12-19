import streamlit as st
import requests
import json

# ======================
# CONFIG
# ======================


API_BASE_URL = st.secrets["API_URL"]
password_true= st.secrets["Pass"]

def check_password():
    """Returns True if the user entered the correct password."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    # Add title and emoji
    st.markdown("## 🔒 Secure Access")
    st.markdown("Welcome! Please enter the password to access the app. 🗝️")
    st.write("---")  # Divider for nicer design

    # Centering the input box
    password = st.text_input("Password", type="password", placeholder="Enter your secret password 🔑")

    # Add some vertical space
    st.write("\n")

    if st.button("Login 🔓"):
        if password_true == password:
            st.session_state.authenticated = True
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Incorrect password. Try again!")

    return False

# Usage
if not check_password():
    st.stop()


# Page config
st.set_page_config(
    page_title="API Manager",
    page_icon="🛠️",
    layout="centered"
)

# Custom CSS for larger, centered title
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
        color: #2c3e50;
    }
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #34495e;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Main title and subtitle
st.markdown('<div class="main-title">🛠️ API Manager</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Manage files, uploads, downloads, and all in one place.</div>', unsafe_allow_html=True)

# Optional divider for cleaner separation
st.write("---")

# ======================
# UPLOAD JSON FILE
# ======================
st.header("📤 Upload JSON File")

json_file = st.file_uploader("Select a JSON file", type=["json"])

if st.button("Upload JSON"):
    if not json_file:
        st.warning("Please select a JSON file")
    else:
        files = {
            "file": (json_file.name, json_file, "application/json")
        }

        response = requests.post(
            f"{API_BASE_URL}/upload-json-file",
            files=files
        )

        if response.status_code == 200:
            st.success(response.json().get("message", "Uploaded successfully"))
        else:
            st.error(response.text)

st.divider()

# ======================
# UPLOAD TXT PROMPT
# ======================
st.header("📝 Upload TXT Prompt")

txt_file = st.file_uploader("Select a TXT file", type=["txt"])
prompt_name = st.text_input("Prompt name (optional)")

if st.button("Upload TXT"):
    if not txt_file:
        st.warning("Please select a TXT file")
    else:
        files = {
            "file": (txt_file.name, txt_file, "text/plain")
        }

        data = {}
        if prompt_name:
            data["name"] = prompt_name

        response = requests.post(
            f"{API_BASE_URL}/prompts/upload-file",
            files=files,
            data=data
        )

        if response.status_code == 200:
            st.success("Prompt uploaded successfully")
        else:
            st.error(response.text)


st.divider()

# ======================
# UPLOAD System TXT PROMPT
# ======================
st.header("📝 Upload System TXT Prompt")

txt_file_system = st.file_uploader("Select messagetype.txt", type=["txt"])

if st.button("Upload System TXT"):
    if not txt_file_system:
        st.warning("Please select a TXT file")
    elif txt_file_system.name != "messagetype.txt":
        st.error("File must be named exactly 'messagetype.txt'")
    else:
        files = {
            "file": (
                txt_file_system.name,
                txt_file_system.getvalue(),
                "text/plain"
            )
        }

        try:
            response = requests.post(
                f"{API_BASE_URL}/prompts/upload-system-file",
                files=files,
                timeout=15
            )

            if response.status_code == 200:
                st.success("Prompt uploaded successfully")
            else:
                st.error(response.text)

        except Exception as e:
            st.error(f"Upload failed: {e}")



st.divider()



# ======================
# JSON FILES
# ======================
st.header("📂 JSON Files")

response = requests.get(f"{API_BASE_URL}/list-jsons")

if response.status_code == 200:
    files = response.json().get("files", [])
    st.info(f"Total JSON files: {len(files)}")

    for filename in files:
        col1, col2, col3 = st.columns([4, 2, 1])

        with col1:
            st.write(filename)

        # ⬇️ Download
        with col2:
            download_url = f"{API_BASE_URL}/download-json/{filename}"
            st.download_button(
                label="⬇️ Download",
                data=requests.get(download_url).content,
                file_name=filename,
                mime="application/json",
                key=f"dl_json_{filename}"
            )

        # ❌ Delete
        with col3:
            if st.button("❌", key=f"del_json_{filename}"):
                filename_no_ext = filename.replace(".json", "")
                del_resp = requests.delete(
                    f"{API_BASE_URL}/delete-json/{filename_no_ext}"
                )

                if del_resp.status_code == 200:
                    st.success(f"{filename} deleted")
                    st.rerun()
                else:
                    st.error(del_resp.text)
else:
    st.error(response.text)



# ======================
# TXT PROMPTS
# ======================
st.header("📂 TXT Prompts")

response = requests.get(f"{API_BASE_URL}/prompts")

if response.status_code == 200:
    prompts = response.json().get("prompts", [])
    prompts = [p for p in prompts if p != "messagetype"]
    st.info(f"Total prompts: {len(prompts)}")

    for prompt in prompts:
        col1, col2, col3 = st.columns([4, 2, 1])

        with col1:
            st.write(prompt)

        # ⬇️ Download
        with col2:
            download_url = f"{API_BASE_URL}/prompts/download/{prompt}.txt"
            st.download_button(
                label="⬇️ Download",
                data=requests.get(download_url).content,
                file_name=f"{prompt}.txt",
                mime="text/plain",
                key=f"dl_prompt_{prompt}"
            )

        # ❌ Delete
        with col3:
            if st.button("❌", key=f"del_prompt_{prompt}"):
                del_resp = requests.delete(
                    f"{API_BASE_URL}/prompts/delete/{prompt}.txt"
                )

                if del_resp.status_code == 200:
                    st.success(f"{prompt} deleted")
                    st.rerun()
                else:
                    st.error(del_resp.text)
else:
    st.error(response.text)


