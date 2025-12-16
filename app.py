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

    password = st.text_input("🔐 Enter password", type="password")

    if st.button("Login"):
        if password_true == password:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")

    return False


if not check_password():
    st.stop()



st.set_page_config(page_title="Prompt Manager", layout="centered")

st.title("API Manager")

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


