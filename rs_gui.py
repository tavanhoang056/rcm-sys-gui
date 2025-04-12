import streamlit as st
import pandas as pd
from rs_helper import *
from rs_ui_helper import *


def get_products():
    return pd.read_csv('data/items.csv');

def get_users():
    return pd.read_csv('data/ratings.csv');

def get_random_products(df):
    return df.sample(n=10)

def get_random_users(df):
    return df.sample(n=10)

def display_products(df):
    st.write(df)

def display_users(df):
    st.write(df)

def select_product(df):
    st.markdown("#### 2. Chọn sản phẩm")
    product_options = [(row['product_id'], row['product_name']) for index, row in df.iterrows()]
    selected_product = st.selectbox(
        "Chọn sản phẩm",
        options=product_options,
        format_func=lambda x: x[1]
    )

    return selected_product[0]

def select_user(df):
    st.markdown("#### 1. Chọn người dùng")
    user_options = [(row['user_id'], row['rating']) for index, row in df.iterrows()]
    selected_user = st.selectbox(
        "Chọn người dùng",
        options=user_options,
        format_func=lambda x: x[0]
    )
    return selected_user[0]

def search_products():
    st.markdown("#### 3. Tìm kiếm sản phẩm")
    return st.text_input("Nhập thông tin tìm kiếm")

def get_recommendation_products_by_user(product_id, user_id, df_products, df_users, selected_user):
    # st.write(selected_user)
    if not selected_user.empty:
        recommendations = get_collaborative_filtering_recommendations(
            product_id=product_id,
            user_id=user_id,
            df_products=df_products,
            df_users=df_users,
            top_k=3
        )
        return recommendations
    else:
        return None

def get_recommendation_products_by_id(id, df, selected_product):
    if not selected_product.empty:
        recommendations = get_content_based_recommendations_by_id(
            id=id,
            df=df,
            top_k=6
        )
        return recommendations
    else:
        return None

def get_recommendation_products_by_keyword(keyword, df):
    if keyword and keyword.strip():
        recommendations = get_content_based_recommendations_by_keyword(
            keyword=keyword,
            df=df,
            top_k=6
        )
        return recommendations
    else:
        return None
 

def main():
    st.title("Recommendation System")

    df_products = get_products();

    if 'random_products' not in st.session_state:
        st.session_state.random_products = get_random_products(df_products);
    display_products(st.session_state.random_products)

    df_users = get_users()
    if 'random_users' not in st.session_state:
        st.session_state.random_users = get_random_users(df_users);
    # display_users(st.session_state.random_users)

    selected_user_id = select_user(st.session_state.random_users)
    selected_user = df_users[df_users['user_id'] == selected_user_id]
    # display_user_card(selected_user)

    selected_product_id = select_product(st.session_state.random_products)
    selected_product = df_products[df_products['product_id'] == selected_product_id]
    display_product_card(selected_product)

    recommendation_products_by_user = get_recommendation_products_by_user(selected_product_id, selected_user_id, df_products, df_users, selected_user)
    display_recommended_user(df_users, recommendation_products_by_user)

    recommendation_products_by_id = get_recommendation_products_by_id(selected_product_id, df_products, selected_product)
    display_recommended_products(df_products, recommendation_products_by_id)

    search_product_keyword = search_products()
    recommendation_products_by_keyword = get_recommendation_products_by_keyword(search_product_keyword, df_products)
    display_seach_products(df_products, recommendation_products_by_keyword, search_product_keyword)


main()




