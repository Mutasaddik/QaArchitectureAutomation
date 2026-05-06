# pages/5_Query_Repository.py
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.ui_theme import inject_theme
inject_theme()

from src.database.query_store import (
    add_query, get_all_queries, smart_search,
    keyword_search, delete_query, get_all_modules,
    index_queries_to_chromadb
)

st.set_page_config(page_title="Query Repository", page_icon="🔍", layout="wide")
st.title("🔍 SQL Query Repository")
st.markdown("Store and search your QA validation queries.")

tab1, tab2, tab3 = st.tabs(["🔎 Search Queries", "➕ Add New Query", "📂 Upload SQL File"])

# ── Tab 1: Search ─────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        search_input = st.text_input(
            "Search by keyword or sentence",
            placeholder="e.g. 'loan weekly repayment' or 'check borrower payment history'"
        )
    with col2:
        modules = ["All"] + get_all_modules()
        module_filter = st.selectbox("Filter by Module", modules)

    search_btn = st.button("🔍 Search", type="primary")

    if search_btn and search_input:
        module = None if module_filter == "All" else module_filter
        with st.spinner("Searching..."):
            results = smart_search(search_input, module=module)

        if results:
            st.success(f"Found {len(results)} matching queries")
            for r in results:
                with st.expander(f"[{r['module']}] {r['title']} — CR: {r.get('cr_id', 'N/A')}"):
                    st.code(r["sql"], language="sql")
                    st.markdown(f"**Purpose:** {r.get('purpose', '')}")
                    st.markdown(f"**Tables:** `{r.get('tables', '')}`")
                    st.markdown(f"**Tags:** {', '.join(r.get('tags', []))}")
                    if st.button("🗑️ Delete", key=f"del_{r['id']}"):
                        delete_query(r["id"])
                        st.success("Deleted!")
                        st.rerun()
        else:
            st.info("No matching queries found.")

    # Show all queries if no search
    if not search_input:
        all_q = get_all_queries()
        st.markdown(f"**Total queries in repository: {len(all_q)}**")
        for r in all_q:
            with st.expander(f"[{r['module']}] {r['title']}"):
                st.code(r["sql"], language="sql")
                st.markdown(f"**Purpose:** {r.get('purpose', '')}")
                st.markdown(f"**Tables:** `{r.get('tables', '')}`")
                st.markdown(f"**Tags:** {', '.join(r.get('tags', []))}")
                if st.button("🗑️ Delete", key=f"del_all_{r['id']}"):
                    delete_query(r["id"])
                    st.rerun()

# ── Tab 2: Add New Query Manually ─────────────────────────────
with tab2:
    st.subheader("➕ Add New Query")
    title = st.text_input("Title", placeholder="e.g. Check weekly repayment records")
    module = st.text_input("Module", placeholder="e.g. Loan, Notification, Report")
    cr_id = st.text_input("CR ID (optional)", placeholder="e.g. CR-2024-089")
    tables = st.text_input("Tables Used", placeholder="e.g. loan_repayments, installments")
    purpose = st.text_area("Purpose", placeholder="What does this query validate?", height=80)
    sql = st.text_area("SQL Query", height=150, placeholder="SELECT * FROM ...")
    tags = st.text_input("Tags (comma separated)", placeholder="weekly, loan, repayment")

    if st.button("💾 Save Query", type="primary"):
        if not title or not sql or not module:
            st.warning("Title, Module and SQL are required.")
        else:
            tag_list = [t.strip() for t in tags.split(",") if t.strip()]
            add_query(title, sql, module, cr_id, tables, purpose, tag_list)
            index_queries_to_chromadb()
            st.success(f"✅ Query '{title}' saved and indexed!")
            st.rerun()

# ── Tab 3: Upload SQL File ─────────────────────────────────────
with tab3:
    st.subheader("📂 Upload SQL File")
    st.markdown("""
    Upload a `.sql` file containing one or more queries.

    **Expected format in your SQL file:**
    ```sql
    -- title: Check weekly repayment records
    -- module: Loan
    -- cr_id: CR-2024-089
    -- tables: loan_repayments
    -- purpose: Validate weekly repayment records are created correctly
    -- tags: weekly, loan, repayment
    SELECT * FROM loan_repayments WHERE frequency = 'weekly' ORDER BY created_at DESC;

    -- title: Check SMS notifications for weekly payment
    -- module: Notification
    -- cr_id: CR-2024-089
    -- tables: notifications
    -- purpose: Verify SMS is sent for weekly payment due
    -- tags: sms, notification, weekly
    SELECT * FROM notifications WHERE type = 'SMS' AND trigger_event = 'weekly_payment_due';
    ```
    Each query block must start with `-- title:` comment.
    """)

    uploaded_sql = st.file_uploader("Choose a .sql file", type=["sql", "txt"])

    if uploaded_sql:
        content = uploaded_sql.read().decode("utf-8")
        st.code(content, language="sql")


        # Parse the SQL file into individual query blocks
        def parse_sql_file(content: str):
            """
            Parse SQL file into list of query dicts.
            Each block starts with -- title: comment.
            """
            blocks = []
            current = {}
            sql_lines = []
            in_sql = False

            for line in content.split("\n"):
                stripped = line.strip()

                if stripped.startswith("-- title:"):
                    # Save previous block if exists
                    if current and sql_lines:
                        current["sql"] = "\n".join(sql_lines).strip()
                        blocks.append(current)
                        current = {}
                        sql_lines = []
                        in_sql = False

                    current["title"] = stripped.replace("-- title:", "").strip()
                    in_sql = False

                elif stripped.startswith("-- module:"):
                    current["module"] = stripped.replace("-- module:", "").strip()

                elif stripped.startswith("-- cr_id:"):
                    current["cr_id"] = stripped.replace("-- cr_id:", "").strip()

                elif stripped.startswith("-- tables:"):
                    current["tables"] = stripped.replace("-- tables:", "").strip()

                elif stripped.startswith("-- purpose:"):
                    current["purpose"] = stripped.replace("-- purpose:", "").strip()

                elif stripped.startswith("-- tags:"):
                    current["tags"] = [
                        t.strip()
                        for t in stripped.replace("-- tags:", "").split(",")
                        if t.strip()
                    ]

                elif stripped and not stripped.startswith("--"):
                    # This is SQL content
                    in_sql = True
                    sql_lines.append(line)

                elif in_sql and not stripped:
                    # Empty line inside SQL block — keep it
                    sql_lines.append(line)

            # Save last block
            if current and sql_lines:
                current["sql"] = "\n".join(sql_lines).strip()
                blocks.append(current)

            return blocks


        parsed = parse_sql_file(content)

        if parsed:
            st.success(f"✅ Found {len(parsed)} queries in file")

            # Preview parsed queries
            st.subheader("Preview")
            for i, q in enumerate(parsed):
                with st.expander(f"Query {i + 1}: {q.get('title', 'Untitled')}"):
                    st.code(q.get("sql", ""), language="sql")
                    st.markdown(f"**Module:** {q.get('module', 'N/A')}")
                    st.markdown(f"**CR ID:** {q.get('cr_id', 'N/A')}")
                    st.markdown(f"**Tables:** {q.get('tables', 'N/A')}")
                    st.markdown(f"**Purpose:** {q.get('purpose', 'N/A')}")
                    st.markdown(f"**Tags:** {', '.join(q.get('tags', []))}")

            # Import button
            if st.button("📥 Import All Queries", type="primary"):
                imported = 0
                for q in parsed:
                    if q.get("title") and q.get("sql"):
                        add_query(
                            title=q.get("title", "Untitled"),
                            sql=q.get("sql", ""),
                            module=q.get("module", "General"),
                            cr_id=q.get("cr_id", ""),
                            tables=q.get("tables", ""),
                            purpose=q.get("purpose", ""),
                            tags=q.get("tags", [])
                        )
                        imported += 1

                index_queries_to_chromadb()
                st.success(f"✅ Imported {imported} queries and indexed for search!")
                st.rerun()
        else:
            st.warning("""
            No queries parsed. Make sure your SQL file uses the expected format with `-- title:` comments before each query.
            """)

    # ── Download sample SQL file ──────────────────────────────
    st.markdown("---")
    st.markdown("**📥 Download Sample SQL File** to see the expected format:")
    sample_sql = """-- title: Check weekly repayment records
-- module: Loan
-- cr_id: CR-2024-089
-- tables: loan_repayments
-- purpose: Validate that weekly repayment records are created correctly after frequency change
-- tags: weekly, repayment, loan, frequency
    SELECT * \
    FROM loan_repayments \
    WHERE frequency = 'weekly' \
    ORDER BY created_at DESC;

    -- title: Check loan installment breakdown
-- module: Loan
-- cr_id: CR-2024-089
-- tables: installments
-- purpose: Validate installment records and amounts after repayment schedule change
-- tags: installment, loan, amount, schedule
    SELECT loan_id, installment_no, amount, due_date, status
    FROM installments
    WHERE loan_id = ?
    ORDER BY installment_no;

    -- title: Check SMS notification sent for weekly payment
-- module: Notification
-- cr_id: CR-2024-089
-- tables: notifications
-- purpose: Verify SMS notifications are triggered for weekly payment due dates
-- tags: sms, notification, weekly, payment
    SELECT * \
    FROM notifications
    WHERE type = 'SMS'
      AND trigger_event = 'weekly_payment_due'
    ORDER BY sent_at DESC;

    -- title: Verify borrower loan summary shows weekly schedule
-- module: Loan
-- cr_id: CR-2024-089
-- tables: loan_summary
-- purpose: Check that loan summary report reflects weekly repayment schedule correctly
-- tags: loan, summary, report, weekly
    SELECT loan_id, borrower_id, frequency, total_installments, next_due_date
    FROM loan_summary
    WHERE frequency = 'weekly'; \
                 """
    st.download_button(
        label="⬇️ Download Sample SQL File",
        data=sample_sql,
        file_name="sample_queries.sql",
        mime="text/plain"
    )