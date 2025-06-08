import streamlit as st
import json
import os
from datetime import datetime
from typing import Dict, List
import re

# テンプレートファイルのパス
TEMPLATES_FILE = "email_templates.json"

# 事前定義されたテンプレート（元のCLIツールから）
PREDEFINED_TEMPLATES = {
    "アルバイト応募": {
        "subject": "【アルバイトへの応募について】{your_name}",
        "body": """{company_name}様

初めてご連絡いたします。{your_name}と申します。
{found_source}にて貴店のアルバイト募集情報を拝見し、応募したくご連絡いたしました。

応募可能な場合は今後の選考についてご連絡いただけますと幸いです。
何卒よろしくお願いします。

{your_name}""",
        "variables": ["company_name", "your_name", "found_source"],
        "created_at": datetime.now().isoformat()
    },
    "面接日程調整(承諾)": {
        "subject": "面接日程について - {your_name}",
        "body": """{company_name}様

お世話になっております。先日アルバイトに応募しました{your_name}です。
このたびは面接日程のご連絡をいただきありがとうございます。

面接日時、頂いた日程で承知しました。
{date}に{place}に伺います。

当日は何卒よろしくお願いします。

{your_name}""",
        "variables": ["company_name", "your_name", "date", "place"],
        "created_at": datetime.now().isoformat()
    },
    "面接日程調整(都合が悪い場合)": {
        "subject": "面接日程再調整のお願い - {your_name}",
        "body": """{company_name}様

お世話になっております。先日アルバイトに応募しました{your_name}です。
このたびは面接日程のご連絡をいただきありがとうございます。

申し訳ございませんが、ご提案いただいた{proposed_date}は
都合がつかないため、面接を受けることができません。

つきましては、以下の日程でご都合はいかがでしょうか。
{alternative_dates}

ご検討のほど、何卒よろしくお願いいたします。

{your_name}""",
        "variables": ["company_name", "your_name", "proposed_date", "alternative_dates"],
        "created_at": datetime.now().isoformat()
    }
}

# セッション状態の初期化
def init_session_state():
    if 'templates' not in st.session_state:
        st.session_state.templates = load_templates()
    if 'show_cli_mode' not in st.session_state:
        st.session_state.show_cli_mode = False

def load_templates() -> Dict:
    """テンプレートファイルを読み込む"""
    templates = {}
    
    # 事前定義テンプレートを追加
    templates.update(PREDEFINED_TEMPLATES)
    
    # 保存されたカスタムテンプレートを読み込み
    if os.path.exists(TEMPLATES_FILE):
        try:
            with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
                custom_templates = json.load(f)
                templates.update(custom_templates)
        except Exception as e:
            st.error(f"テンプレートファイルの読み込みエラー: {e}")
    
    return templates

def save_templates(templates: Dict):
    """カスタムテンプレートのみファイルに保存"""
    custom_templates = {}
    for name, data in templates.items():
        if name not in PREDEFINED_TEMPLATES:
            custom_templates[name] = data
    
    try:
        with open(TEMPLATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(custom_templates, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"テンプレートの保存エラー: {e}")

def get_template_variables(template_text: str) -> List[str]:
    """テンプレート内の変数を抽出（{変数名}形式）"""
    return list(set(re.findall(r'\{(\w+)\}', template_text)))

def replace_variables(template: str, variables: Dict[str, str]) -> str:
    """変数を置換してメール本文を生成"""
    result = template
    for key, value in variables.items():
        result = result.replace(f'{{{key}}}', value)
    return result

def format_alternative_dates(dates_text: str) -> str:
    """代替日程のフォーマット"""
    if not dates_text.strip():
        return "改めて都合の良い日程をご相談させていただければと思います。\nご迷惑をおかけして申し訳ございません。"
    
    dates = [d.strip() for d in dates_text.split('\n') if d.strip()]
    if not dates:
        return "改めて都合の良い日程をご相談させていただければと思います。\nご迷惑をおかけして申し訳ございません。"
    
    formatted_dates = []
    for i, date in enumerate(dates[:3], 1):  # 最大3つまで
        formatted_dates.append(f"{i}. {date}")
    
    return '\n'.join(formatted_dates)

# メインアプリケーション
def main():
    # ページ設定を最初に行う
    try:
        st.set_page_config(
            page_title="メールテンプレート生成ツール",
            page_icon="📧",
            layout="wide"
        )
    except st.errors.StreamlitAPIException:
        # ページ設定が既に行われている場合は無視
        pass
    
    init_session_state()
    
    st.title("📧 メールテンプレート生成ツール")
    st.markdown("---")
    
    # サイドバーでモード選択
    with st.sidebar:
        st.header("🔧 機能選択")
        mode = st.selectbox(
            "使用する機能を選択してください",
            ["🚀 クイック作成", "📝 カスタム作成", "⚙️ テンプレート管理"]
        )
        
        st.markdown("---")
        st.markdown("### 📖 使い方ガイド")
        st.markdown("""
        **🚀 クイック作成**
        - アルバイト関連の定型メールを素早く作成
        
        **📝 カスタム作成**
        - 任意のテンプレートでメール作成
        - 変数は `{変数名}` で指定
        
        **⚙️ テンプレート管理**
        - オリジナルテンプレートの作成・編集
        """)

    if mode == "🚀 クイック作成":
        st.header("🚀 クイック作成モード")
        st.markdown("アルバイト関連のメールを素早く作成できます")
        
        # クイック選択
        quick_options = {
            "1️⃣ アルバイト応募": "アルバイト応募",
            "2️⃣ 面接日程調整(承諾)": "面接日程調整(承諾)",
            "3️⃣ 面接日程調整(都合が悪い場合)": "面接日程調整(都合が悪い場合)"
        }
        
        selected_option = st.selectbox("メールの種類を選択してください", list(quick_options.keys()))
        template_name = quick_options[selected_option]
        
        if template_name in st.session_state.templates:
            template_data = st.session_state.templates[template_name]
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📝 入力項目")
                input_values = {}
                
                for var in template_data['variables']:
                    if var == "alternative_dates":
                        input_values[var] = st.text_area(
                            "代替日程 (1行につき1つ、最大3つ):",
                            height=100,
                            placeholder="例:\n2024年12月15日(日) 14:00-16:00\n2024年12月20日(金) 10:00-12:00"
                        )
                    else:
                        # 日本語ラベルのマッピング
                        label_map = {
                            "company_name": "会社名・店舗名",
                            "your_name": "あなたの名前",
                            "found_source": "応募先を見つけた方法",
                            "date": "面接日時",
                            "place": "面接場所",
                            "proposed_date": "相手が提案した日時"
                        }
                        label = label_map.get(var, var)
                        input_values[var] = st.text_input(f"{label}:")
            
            with col2:
                st.subheader("👀 プレビュー")
                
                # 代替日程の特別処理
                if "alternative_dates" in input_values:
                    input_values["alternative_dates"] = format_alternative_dates(input_values["alternative_dates"])
                
                # 件名
                subject = replace_variables(template_data['subject'], input_values)
                st.text_input("📧 件名:", value=subject, disabled=True)
                
                # 本文
                body = replace_variables(template_data['body'], input_values)
                st.text_area("📄 本文:", value=body, height=400, disabled=True)
                
                # コピー用
                if st.button("📋 テキストをコピー用形式で表示", type="primary"):
                    st.subheader("📋 コピー用テキスト")
                    full_email = f"件名: {subject}\n\n{body}"
                    st.code(full_email, language=None)

    elif mode == "📝 カスタム作成":
        st.header("📝 カスタム作成モード")
        
        # テンプレート選択
        template_names = [name for name in st.session_state.templates.keys() if name not in PREDEFINED_TEMPLATES]
        
        if not template_names:
            st.warning("カスタムテンプレートが登録されていません。「テンプレート管理」で作成してください。")
            st.info("💡 クイック作成モードでは事前定義されたテンプレートを使用できます。")
        else:
            selected_template = st.selectbox("テンプレートを選択", template_names)
            
            if selected_template:
                template_data = st.session_state.templates[selected_template]
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("📝 入力項目")
                    variables = get_template_variables(template_data['subject'] + template_data['body'])
                    
                    input_values = {}
                    for var in variables:
                        input_values[var] = st.text_input(f"{var}:", key=f"custom_input_{var}")
                
                with col2:
                    st.subheader("👀 プレビュー")
                    
                    # 件名
                    subject = replace_variables(template_data['subject'], input_values)
                    st.text_input("📧 件名:", value=subject, disabled=True)
                    
                    # 本文
                    body = replace_variables(template_data['body'], input_values)
                    st.text_area("📄 本文:", value=body, height=400, disabled=True)
                    
                    # コピー用
                    if st.button("📋 テキストをコピー用形式で表示", type="primary"):
                        st.subheader("📋 コピー用テキスト")
                        full_email = f"件名: {subject}\n\n{body}"
                        st.code(full_email, language=None)

    elif mode == "⚙️ テンプレート管理":
        st.header("⚙️ テンプレート管理")
        
        # 新規テンプレート作成
        with st.expander("➕ 新しいテンプレートを作成", expanded=True):
            st.markdown("💡 変数は `{変数名}` の形式で記述してください")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                new_name = st.text_input("テンプレート名:", placeholder="例: お礼メール")
                new_subject = st.text_input("件名テンプレート:", placeholder="例: {件名} - {送信者名}")
            
            with col2:
                new_body = st.text_area(
                    "本文テンプレート:", 
                    height=200,
                    placeholder="例:\n{宛先}様\n\nいつもお世話になっております。\n{送信者名}です。\n\n{内容}\n\nよろしくお願いいたします。\n\n{送信者名}"
                )
            
            if st.button("💾 テンプレートを保存", type="primary"):
                if new_name and new_subject and new_body:
                    if new_name not in PREDEFINED_TEMPLATES:
                        variables = get_template_variables(new_subject + new_body)
                        st.session_state.templates[new_name] = {
                            'subject': new_subject,
                            'body': new_body,
                            'variables': variables,
                            'created_at': datetime.now().isoformat()
                        }
                        save_templates(st.session_state.templates)
                        st.success(f"✅ テンプレート「{new_name}」を保存しました！")
                        st.rerun()
                    else:
                        st.error("❌ その名前は事前定義テンプレートと重複しています。")
                else:
                    st.error("❌ すべての項目を入力してください。")
        
        # 既存テンプレート一覧
        st.subheader("📚 既存テンプレート")
        
        # 事前定義テンプレート
        st.markdown("### 🔒 事前定義テンプレート")
        for name, data in PREDEFINED_TEMPLATES.items():
            with st.expander(f"📄 {name} (編集不可)"):
                st.write("**件名:**", data['subject'])
                st.write("**本文:**")
                st.code(data['body'], language=None)
                st.info("💡 このテンプレートは編集・削除できません")
        
        # カスタムテンプレート
        custom_templates = {k: v for k, v in st.session_state.templates.items() if k not in PREDEFINED_TEMPLATES}
        
        if custom_templates:
            st.markdown("### ✏️ カスタムテンプレート")
            for name, data in custom_templates.items():
                with st.expander(f"📄 {name}"):
                    st.write("**件名:**", data['subject'])
                    st.write("**本文:**")
                    st.code(data['body'], language=None)
                    
                    # 削除ボタン
                    if st.button(f"🗑️ 削除", key=f"delete_{name}", type="secondary"):
                        del st.session_state.templates[name]
                        save_templates(st.session_state.templates)
                        st.success(f"✅ テンプレート「{name}」を削除しました！")
                        st.rerun()
        else:
            st.info("📝 カスタムテンプレートはまだ登録されていません。")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"アプリケーションの起動中にエラーが発生しました: {e}")
        st.info("ページを再読み込みしてみてください。")
