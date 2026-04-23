import streamlit as st
import requests

# ── Configuration ──────────────────────────────────────────────────────────────
API_BASE = "https://assignment6new.onrender.com"   # ← update if needed
DEFAULT_TOKEN = "password"                                  # ← update to match API_TOKEN

# ── Page setup ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="📚 Bookstore",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=Source+Sans+3:wght@300;400;600&display=swap');

html, body, [class*="css"] { font-family: 'Source Sans 3', sans-serif; }

h1, h2, h3 { font-family: 'Playfair Display', serif !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #1a1a2e;
    border-right: 1px solid #2e2e4a;
}
[data-testid="stSidebar"] * { color: #e8e0d4 !important; }

/* Cards */
.book-card {
    background: linear-gradient(135deg, #fefcf9 0%, #f5f0e8 100%);
    border: 1px solid #ddd5c4;
    border-left: 4px solid #c9622f;
    border-radius: 6px;
    padding: 16px 20px;
    margin-bottom: 12px;
    box-shadow: 2px 3px 10px rgba(0,0,0,0.06);
    transition: transform .15s;
}
.book-card:hover { transform: translateX(3px); }
.book-title { font-family: 'Playfair Display', serif; font-size: 1.15rem; color: #1a1a2e; font-weight: 700; }
.book-meta  { font-size: .85rem; color: #6b6560; margin-top: 4px; }
.badge-available   { background:#d4edda; color:#155724; border-radius:12px; padding:2px 10px; font-size:.75rem; font-weight:600; }
.badge-unavailable { background:#f8d7da; color:#721c24; border-radius:12px; padding:2px 10px; font-size:.75rem; font-weight:600; }

/* Headings */
.section-title { font-family: 'Playfair Display', serif; font-size:1.6rem; color:#1a1a2e; border-bottom:2px solid #c9622f; padding-bottom:6px; margin-bottom:18px; }

/* Toasts via st.success/error already styled; keep buttons warm */
.stButton > button {
    background: #c9622f !important;
    color: white !important;
    border: none !important;
    border-radius: 4px !important;
    font-weight: 600 !important;
}
.stButton > button:hover { background: #a84d24 !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def get_books() -> list:
    try:
        r = requests.get(f"{API_BASE}/books", timeout=60)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Could not fetch books: {e}")
        return []


def render_book_card(book: dict):
    badge = (
        '<span class="badge-available">✓ Available</span>'
        if book.get("is_available")
        else '<span class="badge-unavailable">✗ Unavailable</span>'
    )
    st.markdown(f"""
    <div class="book-card">
      <div class="book-title">{book.get('title','—')}</div>
      <div class="book-meta">
        ✍️ {book.get('author','—')} &nbsp;|&nbsp;
        📅 {book.get('published_year','—')} &nbsp;|&nbsp;
        🔖 ISBN: {book.get('isbn','—')} &nbsp;|&nbsp;
        ID: <code>{book.get('id','?')}</code> &nbsp; {badge}
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 Bookstore Admin")
    st.markdown("---")
    token = st.text_input("🔑 Bearer Token", value=DEFAULT_TOKEN, type="password")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["🔍 Search & Browse", "➕ Add Book", "✏️ Update Book", "🩹 Patch Book", "🗑️ Delete Book"],
    )
    st.markdown("---")
    st.caption(f"API: `{API_BASE}`")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Search & Browse
# ══════════════════════════════════════════════════════════════════════════════
if page == "🔍 Search & Browse":
    st.markdown('<div class="section-title">Search & Browse Books</div>', unsafe_allow_html=True)

    books = get_books()

    # Search bar
    query = st.text_input("Search by title, author, or ISBN", placeholder="e.g. Tolkien")

    if query:
        q = query.lower()
        books = [
            b for b in books
            if q in b.get("title", "").lower()
            or q in b.get("author", "").lower()
            or q in b.get("isbn", "").lower()
        ]

    # Filter
    col1, col2 = st.columns([2, 1])
    with col2:
        avail_filter = st.selectbox("Availability", ["All", "Available", "Unavailable"])
    if avail_filter == "Available":
        books = [b for b in books if b.get("is_available")]
    elif avail_filter == "Unavailable":
        books = [b for b in books if not b.get("is_available")]

    st.caption(f"{len(books)} book(s) found")
    st.markdown("---")

    if books:
        for book in books:
            render_book_card(book)
    else:
        st.info("No books match your search.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Add Book
# ══════════════════════════════════════════════════════════════════════════════
elif page == "➕ Add Book":
    st.markdown('<div class="section-title">Add a New Book</div>', unsafe_allow_html=True)

    with st.form("add_book_form"):
        title   = st.text_input("Title *")
        author  = st.text_input("Author *")
        isbn    = st.text_input("ISBN *")
        year    = st.number_input("Published Year *", min_value=1000, max_value=2100, value=2024, step=1)
        avail   = st.checkbox("Available?", value=True)
        submit  = st.form_submit_button("➕ Create Book")

    if submit:
        if not all([title, author, isbn]):
            st.warning("Please fill in all required fields.")
        else:
            payload = {
                "title": title, "author": author, "isbn": isbn,
                "published_year": int(year), "is_available": avail,
            }
            try:
                r = requests.post(f"{API_BASE}/books", json=payload, headers=auth_headers(token), timeout=10)
                if r.status_code == 201:
                    st.success("✅ Book created successfully!")
                    st.json(r.json())
                else:
                    st.error(f"Error {r.status_code}: {r.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Full Update (PUT)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "✏️ Update Book":
    st.markdown('<div class="section-title">Full Update (PUT)</div>', unsafe_allow_html=True)
    st.caption("Replaces all fields for the specified book ID.")

    books = get_books()
    if books:
        options = {f"[{b['id']}] {b['title']}": b for b in books}
        chosen_label = st.selectbox("Select a book to update", list(options.keys()))
        chosen = options[chosen_label]
    else:
        chosen = None
        st.info("No books available.")

    with st.form("update_book_form"):
        book_id = st.number_input("Book ID *", min_value=1, step=1,
                                  value=int(chosen["id"]) if chosen else 1)
        title   = st.text_input("Title *",   value=chosen["title"]   if chosen else "")
        author  = st.text_input("Author *",  value=chosen["author"]  if chosen else "")
        isbn    = st.text_input("ISBN *",    value=chosen["isbn"]    if chosen else "")
        year    = st.number_input("Published Year *", min_value=1000, max_value=2100,
                                  value=int(chosen["published_year"]) if chosen else 2024, step=1)
        avail   = st.checkbox("Available?",  value=bool(chosen["is_available"]) if chosen else True)
        submit  = st.form_submit_button("✏️ Update Book")

    if submit:
        payload = {
            "title": title, "author": author, "isbn": isbn,
            "published_year": int(year), "is_available": avail,
        }
        try:
            r = requests.put(f"{API_BASE}/books/{int(book_id)}", json=payload,
                             headers=auth_headers(token), timeout=60)
            if r.status_code == 200:
                st.success("✅ Book updated!")
                st.json(r.json())
            elif r.status_code == 404:
                st.error("Book not found.")
            else:
                st.error(f"Error {r.status_code}: {r.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Partial Update (PATCH)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🩹 Patch Book":
    st.markdown('<div class="section-title">Partial Update (PATCH)</div>', unsafe_allow_html=True)
    st.caption("Only the fields you fill in will be updated.")

    books = get_books()
    if books:
        options = {f"[{b['id']}] {b['title']}": b for b in books}
        chosen_label = st.selectbox("Select a book to patch", list(options.keys()))
        chosen = options[chosen_label]
    else:
        chosen = None
        st.info("No books available.")

    with st.form("patch_book_form"):
        book_id = st.number_input("Book ID *", min_value=1, step=1,
                                  value=int(chosen["id"]) if chosen else 1)
        title   = st.text_input("New Title   (leave blank to skip)")
        author  = st.text_input("New Author  (leave blank to skip)")
        avail_opt = st.selectbox("Availability", ["— no change —", "Available", "Unavailable"])
        submit  = st.form_submit_button("🩹 Patch Book")

    if submit:
        payload: dict = {}
        if title:  payload["title"]  = title
        if author: payload["author"] = author
        if avail_opt != "— no change —":
            payload["is_available"] = (avail_opt == "Available")

        if not payload:
            st.warning("No fields to update.")
        else:
            try:
                r = requests.patch(f"{API_BASE}/books/{int(book_id)}", json=payload,
                                   headers=auth_headers(token), timeout=60)
                if r.status_code == 200:
                    st.success("✅ Book patched!")
                    st.json(r.json())
                else:
                    st.error(f"Error {r.status_code}: {r.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Delete Book
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🗑️ Delete Book":
    st.markdown('<div class="section-title">Delete a Book</div>', unsafe_allow_html=True)

    books = get_books()
    if books:
        options = {f"[{b['id']}] {b['title']}": b for b in books}
        chosen_label = st.selectbox("Select a book to delete", list(options.keys()))
        chosen = options[chosen_label]
        render_book_card(chosen)
    else:
        chosen = None
        st.info("No books available.")

    book_id = st.number_input("Confirm Book ID", min_value=1, step=1,
                               value=int(chosen["id"]) if chosen else 1)

    if st.button("🗑️ Delete Book", type="primary"):
        try:
            r = requests.delete(f"{API_BASE}/books/{int(book_id)}",
                                headers=auth_headers(token), timeout=60)
            if r.status_code == 200:
                st.success(f"✅ {r.json().get('message', 'Deleted.')}")
            else:
                st.error(f"Error {r.status_code}: {r.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")
