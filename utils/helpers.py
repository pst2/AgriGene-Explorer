import re
import streamlit as st

def init_session_state() -> None:
    """Khởi tạo các biến mặc định trong st.session_state nếu chưa có."""
    if 'ncbi_email' not in st.session_state:
        st.session_state['ncbi_email'] = ''
    if 'ncbi_api_key' not in st.session_state:
        st.session_state['ncbi_api_key'] = ''
    if 'max_results' not in st.session_state:
        st.session_state['max_results'] = 50
    if 'search_results' not in st.session_state:
        st.session_state['search_results'] = None

def is_valid_email(email: str) -> bool:
    """
    Kiểm tra định dạng email hợp lệ.
    
    Args:
        email (str): Địa chỉ email cần kiểm tra.
        
    Returns:
        bool: True nếu hợp lệ, False nếu không.
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None