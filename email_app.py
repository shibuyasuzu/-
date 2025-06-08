import streamlit as st
import json
import os
from datetime import datetime
from typing import Dict, List

# テンプレートファイルのパス
TEMPLATES_FILE = "email_templates.json"

# セッション状態の初期化
if 'templates' not in st.session_state:
    st.session_state.templates = load_templates()

def load_templates() -> Dict:
    """テンプレートファイルを読み込む"""
    if os.path.exists(TEMPLATES_FILE):
        with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_templates(templates: Dict):
    """テンプレートファイルに保存"""
    with open(TEMPLATES_FILE, 'w', encoding='utf-8') as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)

def get_template_variables(template_text: str) -> List[str]:
    """テンプレート内の変数を抽出（{変数名}形式）"""
    import re
    return list(set(re.findall(r'\{(\w+)\}', template_text)))

def replace_variables(template: str, variables: Dict[str, str]) -> str:
    """変数を置換してメール本文を生成"""
    result = template
    for key, value in variables.items():
        result = result.replace(f'{{{key}}}', value)
    return result

# メインアプリケーション
st.title("📧 メールテンプレート管理")

# サイドバーでモード選択
mode = st.sidebar.selectbox(
    "モードを選択",
    ["メール作成", "テンプレート管理"]
)

if mode == "メール作成":
    st.header("メール作成")
    
    # テンプレート選択
    template_names = list(st.session_state.templates.keys())
    if not template_names:
        st.warning("テンプレートが登録されていません。まず「テンプレート管理」でテンプレートを作成してください。")
        st.stop()
    
    selected_template = st.selectbox("テンプレートを選択", template_names)
    
    if selected_template:
        template_data = st.session_state.templates[selected_template]
        
        # 変数入力フォーム
        st.subheader("入力項目")
        variables = get_template_variables(template_data['subject'] + template_data['body'])
        
        input_values = {}
        for var in variables:
            input_values[var] = st.text_input(f"{var}:", key=f"input_{var}")
        
        # プレビュー
        if st.button("プレビュー生成"):
            st.subheader("メールプレビュー")
            
            # 件名
            subject = replace_variables(template_data['subject'], input_values)
            st.text_input("件名:", value=subject, disabled=True)
            
            # 本文
            body = replace_variables(template_data['body'], input_values)
            st.text_area("本文:", value=body, height=300, disabled=True)
            
            # コピー用のテキスト
            st.subheader("コピー用テキスト")
            full_email = f"件名: {subject}\n\n{body}"
            st.code(full_email, language=None)
            
            # クリップボードコピー用のJavaScript（注意：ブラウザの制限があります）
            st.info("上記のテキストを選択してコピーしてください。")

elif mode == "テンプレート管理":
    st.header("テンプレート管理")
    
    # 新規テンプレート作成
    with st.expander("新しいテンプレートを作成"):
        new_name = st.text_input("テンプレート名:")
        new_subject = st.text_input("件名テンプレート:", placeholder="例: {会社名}へのお問い合わせ")
        new_body = st.text_area(
            "本文テンプレート:", 
            height=200,
            placeholder="例:\n{宛先}様\n\nいつもお世話になっております。\n{送信者名}です。\n\n{内容}\n\nよろしくお願いいたします。"
        )
        
        if st.button("テンプレートを保存"):
            if new_name and new_subject and new_body:
                st.session_state.templates[new_name] = {
                    'subject': new_subject,
                    'body': new_body,
                    'created_at': datetime.now().isoformat()
                }
                save_templates(st.session_state.templates)
                st.success(f"テンプレート「{new_name}」を保存しました！")
                st.rerun()
            else:
                st.error("すべての項目を入力してください。")
    
    # 既存テンプレート一覧
    st.subheader("既存テンプレート")
    
    if st.session_state.templates:
        for name, data in st.session_state.templates.items():
            with st.expander(f"📄 {name}"):
                st.write("**件名:**", data['subject'])
                st.write("**本文:**")
                st.code(data['body'], language=None)
                
                # 削除ボタン
                if st.button(f"削除", key=f"delete_{name}"):
                    del st.session_state.templates[name]
                    save_templates(st.session_state.templates)
                    st.success(f"テンプレート「{name}」を削除しました！")
                    st.rerun()
    else:
        st.info("まだテンプレートが登録されていません。")

# 使用方法の説明
with st.sidebar:
    st.markdown("---")
    st.markdown("### 使い方")
    st.markdown("""
    1. **テンプレート管理**でテンプレートを作成
    2. 変数は `{変数名}` の形式で記述
    3. **メール作成**でテンプレートを選択
    4. 変数に値を入力してプレビュー生成
    """)
