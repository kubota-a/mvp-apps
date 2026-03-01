from flask_sqlalchemy import SQLAlchemy  # SQLAlchemy（ORM：PythonのクラスでDBを扱えるライブラリ）
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import CheckConstraint, text
from sqlalchemy.sql import func  # Postgresでも安全な日時関数


# アプリ全体で共有する DB オブジェクト
db = SQLAlchemy()


# --- Userモデル---
class User(UserMixin, db.Model):    # ログイン判定ができるように「UserMixin」が必要
    __tablename__ = "users"    # 実際のDB上のテーブル名をusersに指定(設計と合わせる。※モデル名は「単数形」がルール)

    # テーブル全体への制約追加オプション
    __table_args__ = (
        CheckConstraint(    # チェック制約（ロールは増えてもあと1つ程度の想定なので、rolesマスタ化はしない）
            "role IN ('user', 'admin')",    # role は 'user' か 'admin' のどちらかだけ許可
            name = "ck_users_role_valid"    # 制約名の設定
            ),
        )

    id = db.Column(db.BigInteger, primary_key=True)    # 自動採番の大きな（拡張性を考慮）整数型・主キー
    login_id = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50), nullable=False)    # 画面表示用の氏名
    role = db.Column(db.String(20), nullable=False, server_default=text("'user'"))    # デフォルトは一般ユーザー 
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)    # タイムゾーン付き日時・作成日時（今）を自動で入れる・入力必須

    # Userクラス専用の、保存前にパスワードをハッシュ化するメソッド　signup（ユーザー作成）のときに使用
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    # 入力されたパスワードとハッシュを照合するメソッド　login（ログイン）のときに使用
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # デバッグ、Flaskシェル、ログ出力した際に、オブジェクトを「User 3」のように短くわかりやすく表すための関数
    def __repr__(self) -> str:
        return f"<User {self.login_id}>"    # ※「login_id」部分はMVPによって変わる

# --- Taskモデル ---
class Task(db.Model):
    __tablename__ = "tasks"    # 実際のDB上のテーブル名をtasksに指定

    id = db.Column(db.BigInteger, primary_key=True)    # 自動採番の大きな（拡張性を考慮）整数型・主キー
    user_id = db.Column(
        db.BigInteger, 
        db.ForeignKey("users.id"), 
        nullable=False, 
        index=True    # 一覧取得の高速化のためインデックス付与
        )
    status_id = db.Column(db.SmallInteger, db.ForeignKey("statuses.id"), nullable=False)
    title = db.Column(db.String(100), nullable=False)    # タスク内容
    due_at = db.Column(db.DateTime(timezone=True), nullable=False)    # 期限日時（手打ちか選択かはDB側では考慮いらない）
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)    # 作成日時（今）
    updated_at = db.Column(   # 更新日時
        db.DateTime(timezone=True), 
        server_default=db.func.now(),     # 最初の作成時はcreated_atと同じ日時が入り、
        onupdate=db.func.now(),     # その後UPDATEのたびに最新の"今"に更新される
        nullable=False
        ) 
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)    # 削除日時（論理削除用。値が入っていれば削除済み。※デフォルト値付けたらレコード作成時から日時が入って最初から「削除済み扱い」になってしまうので付けない。日時はPython側でセットする）

# --- Statusモデル ---
class Status(db.Model):
    __tablename__ = "statuses"    # 実際のDB上のテーブル名をstatusesに指定

    id = db.Column(db.SmallInteger, primary_key=True)    # 自動採番の小さな整数型・主キー
    name = db.Column(db.String(20), unique=True, nullable=False)    # ステータス名
    display_order = db.Column(db.SmallInteger, nullable=False)    # UI表示順