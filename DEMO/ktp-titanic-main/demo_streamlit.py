import streamlit as st

st.title("Trung tâm tin học")
st.subheader("Hành trang tốt nghiệp Data Science")
# Using menu
menu = ["Home", "HTDS"]
choice = st.sidebar.selectbox('Menu', menu)
if choice == 'Home':    
    st.subheader("[Trang chủ](https://csc.edu.vn)")  
elif choice == 'HTDS':    
    st.subheader("[Hành trang TN Data Science](https://csc.edu.vn/data-science-machine-learning/Hanh-trang-tot-nghiep-Data-Science_224)")
