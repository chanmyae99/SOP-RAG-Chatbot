import streamlit as st
import uuid
import requests
import os
from dotenv import load_dotenv

load_dotenv()
# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="SOP QUERY AI Chatbot",
    layout="wide"
)



BLOB_BASE_URL = "https://wshragsopstorage.blob.core.windows.net/wsh-documents"
BLOB_SAS_TOKEN = os.getenv("BLOB_SAS_TOKEN")


RAG_API_URL = "https://f07b-42-61-142-232.ngrok-free.app/ask"

USE_RAG = True


def get_answer(query: str):
    try:
        resp = requests.get(
            RAG_API_URL,
            params={"q": query, "top_k": 5},
            timeout=60
        )
        resp.raise_for_status()
        data = resp.json()

        return {
            "answer": data.get("answer", ""),
            "sources": data.get("sources", []),
            "images": data.get("images", [])
        }

    except Exception as e:
        return {
            "answer": f"⚠️ Backend error:\n\n{e}",
            "sources": [],
            "images": []
        }



def format_title(text, max_len=4):
    text = text.replace("\n", " ")
    return text[:max_len] + "…" if len(text) > max_len else text

def render_text_source(src):
    document = src.get("source_file", "Unknown document")
    page = src.get("page_number", "N/A")

    st.markdown(
        f"""
**{document}**  
Page {page}
"""
    )

def format_source_citation(src):
    """
    Build a clean, human-readable citation string
    depending on document type and available metadata.
    """
    parts = []

    # Source ID + file name (always show)
    source_id = src.get("source_id", "T?")
    source_file = src.get("source_file", "Unknown document")

    parts.append(f"[{source_id}] {source_file}")

    # PDF
    if src.get("page_number") is not None:
        parts.append(f"page {src['page_number']}")

    # DOCX
    if src.get("section"):
        parts.append(f'section "{src["section"]}"')
        if src.get("paragraph_number") is not None:
            parts.append(f"paragraph {src['paragraph_number']}")

    # XLSX
    if src.get("sheet_name"):
        parts.append(f'sheet "{src["sheet_name"]}"')
        if src.get("row_number") is not None:
            parts.append(f"row {src['row_number']}")

    return ", ".join(parts)

def render_assistant_message(msg):
    # Answer text
    st.markdown(msg["content"])

    sources = msg.get("sources", [])

    if not sources:
        return

    image_sources = [s for s in sources if "image_path" in s]
    text_sources = [s for s in sources if "image_path" not in s]

    # Inline images
    for img in image_sources:
        image_url = (
            f"{BLOB_BASE_URL}/{img['image_path']}?"
            f"{BLOB_SAS_TOKEN}"
        )

        caption = img.get("caption")
        st.image(image_url, caption=caption, use_container_width=True)

    # Sources dropdown
    with st.expander("Retrieved SOP Sources"):
        if text_sources:
            st.markdown("### Text Sources")
            for src in text_sources:
                st.markdown(f"**{format_source_citation(src)}**")

        if image_sources:
            st.markdown("### Image Sources")
            for img in image_sources:
                st.markdown(f"**{format_source_citation(img)}**")


# ======================================================
# SESSION STATE INITIALISATION
# ======================================================
if "conversations" not in st.session_state:
    st.session_state.conversations = {}

if "current_conv" not in st.session_state:
    conv_id = str(uuid.uuid4())
    st.session_state.conversations[conv_id] = []
    st.session_state.current_conv = conv_id

if "delete_target" not in st.session_state:
    st.session_state.delete_target = None

# ======================================================
# SIDEBAR - CONVERSATION MANAGER
# ======================================================
st.sidebar.title("💬 Conversations")

# New conversation
if st.sidebar.button("➕ New Conversation"):
    new_id = str(uuid.uuid4())
    st.session_state.conversations[new_id] = []
    st.session_state.current_conv = new_id
    st.session_state.delete_target = None
    st.rerun()

st.sidebar.markdown("---")

# List conversations
for conv_id, messages in list(st.session_state.conversations.items()):
    label = (
        messages[0]["content"][:15] + "..."
        if messages else "New Conversation"
    )

    col1, col2 = st.sidebar.columns([6, 1])

    # Load conversation
    if col1.button(label, key=f"load_{conv_id}", use_container_width=True):
        st.session_state.current_conv = conv_id
        st.session_state.delete_target = None
        st.rerun()

    # Three-dot menu
    if col2.button("⋮", key=f"menu_{conv_id}", help="Conversation actions"):
        if st.session_state.delete_target == conv_id:
            st.session_state.delete_target = None
        else:
            st.session_state.delete_target = conv_id
        st.rerun()

    # Delete confirmation
    if st.session_state.delete_target == conv_id:
        st.sidebar.markdown("⚠️ **Delete this conversation?**")

        if st.sidebar.button(
            "🗑️ Delete conversation",
            key=f"confirm_delete_{conv_id}"
        ):
            del st.session_state.conversations[conv_id]

            # If deleting active conversation, create new one
            if st.session_state.current_conv == conv_id:
                new_id = str(uuid.uuid4())
                st.session_state.conversations[new_id] = []
                st.session_state.current_conv = new_id

            st.session_state.delete_target = None
            st.rerun()

        st.sidebar.markdown("---")

# ======================================================
# MAIN UI
# ======================================================
st.title("🦺 SOP Query AI Chatbot")
st.caption("Workplace Safety & Health SOP Question Answering System")
st.divider()


# ==============================
# Render chat history
# ==============================
for msg in st.session_state.conversations[
    st.session_state.current_conv
]:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            render_assistant_message(msg)
        else:
            st.markdown(msg["content"])


# ======================================================
# CHAT INPUT (BOTTOM)
# ======================================================
query = st.chat_input("Ask a safety-related question")

if query:
    # ==============================
    # Save user message
    # ==============================
    st.session_state.conversations[
        st.session_state.current_conv
    ].append({
        "role": "user",
        "content": query
    })

    # SHOW user message immediately
    with st.chat_message("user"):
        st.markdown(query)

    # ==============================
    # Global loading indicator
    # (NO chat_message here!)
    # ==============================
    placeholder = st.empty()

    with st.spinner("Analyzing SOP documents..."):
            placeholder.markdown("⏳ **Thinking...**")
            result = get_answer(query)

    placeholder.empty()

    # ==============================
    # Save assistant message
    # ==============================
    st.session_state.conversations[
        st.session_state.current_conv
    ].append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result.get("sources", [])
    })

    # ==============================
    # Rerun → history renders ONCE
    # ==============================
    st.rerun()



# if query:
#     # Save user message
#     st.session_state.conversations[
#         st.session_state.current_conv
#     ].append({
#         "role": "user",
#         "content": query
#     })

#     with st.chat_message("user"):
#         st.markdown(query)

#     with st.chat_message("assistant"):
#         placeholder = st.empty()

#         with st.spinner("Analyzing SOP documents..."):
#             placeholder.markdown("⏳ **Thinking...**")
#             result = get_answer(query)

#         placeholder.empty()

#         render_assistant_message({
#             "content": result["answer"],
#             "sources": result.get("sources", [])
#         })

#     # Save assistant message
#     st.session_state.conversations[
#         st.session_state.current_conv
#     ].append({
#         "role": "assistant",
#         "content": result["answer"],
#         "sources": result.get("sources", [])
#     })
