from flask_sqlalchemy import SQLAlchemy  # SQLAlchemy（ORM：PythonのクラスでDBを扱えるライブラリ）
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import CheckConstraint, text
# from sqlalchemy.sql import func  # Postgresでも安全な日時関数


# アプリ全体で共有する DB オブジェクト
db = SQLAlchemy()


# --- Userモデル---
class User(UserMixin, db.Model):    # ログイン判定ができるように「UserMixin」が必要
    __tablename__ = "users"    # 実際のDB上のテーブル名をusersに指定(設計と合わせる)

    # テーブル全体への制約追加オプション
    __table_args__ = (
        CheckConstraint(    # チェック制約
            "role IN ('user', 'admin')",    # role は 'user' か 'admin' のどちらかだけ許可
            name = "ck_users_role_valid"    # 制約名の設定
        ),
    )

    # カラム定義
    id = db.Column(db.BigInteger, primary_key=True)    # 自動採番の大きな（拡張性を考慮）整数型・主キー
    login_id = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50), nullable=False)    # 画面表示用の氏名
    role = db.Column(db.String(20), nullable=False, server_default=text("'user'"))    # デフォルトは一般ユーザー 
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)    # タイムゾーン付き日時・作成日時を自動で入れる・入力必須

    # Userクラス専用の、保存前にパスワードをハッシュ化するメソッド　signup（ユーザー作成）のときに使用
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    # 入力されたパスワードとハッシュを照合するメソッド　login（ログイン）のときに使用
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # デバッグ、Flaskシェル、ログ出力した際に、オブジェクトを「User 3」のように短くわかりやすく表すための関数
    def __repr__(self) -> str:
        return f"<User {self.login_id}>"    # ※「login_id」部分はMVPによって変わる
    