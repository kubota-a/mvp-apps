from flask import Flask, render_template, request, redirect, abort, flash, url_for, session
from flask_migrate import Migrate
# from flask_login import (
#     LoginManager,
#     login_user,
#     logout_user,
#     login_required,
# )
import os

# ★ADD: .env から環境変数（environment variable：設定値を外出しした変数）を読み込むための import
from dotenv import load_dotenv  # ★ADD


# models.pyからdbとモデルを import
from models import db  # ★SETUP段階では db だけ。User/Memo/Task は後で追加。　例：from models import db, User, Task


# =========================================
# ★ADD: .env から環境変数を読み込む
# =========================================
# 開発環境では .env / .env.production に書いた DATABASE_URL, SECRET_KEY などを
# os.environ から参照できるようにする。
load_dotenv()  # ★ADD


# =========================================
# Flaskアプリ本体（直書き）
# =========================================
app = Flask(__name__)

# Render/本番では必ず環境変数で設定する。ローカルは仮でOK。
# session/flash/flask-loginに必要
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")


# =========================================
# データベース設定（PostgreSQL想定）
# =========================================
# - Render/Neon では DATABASE_URL が環境変数で渡される前提
# - ローカルでも「Postgres想定で書く」ため、基本は DATABASE_URL を使う運用に寄せる
database_url = os.environ.get("DATABASE_URL")    # 環境変数から"DATABASE_URL"とう値を取得して変数database_urlに格納

if not database_url:    # database_urlがNoneまたは空文字の場合、エラーを出して停止する
    raise RuntimeError("DATABASE_URL is not set")

# サービスによっては "postgres://" が来ることがあるため、接続エラー予防の補正
# （SQLAlchemyは "postgresql://" を推奨）
database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Render本番で接続が安定しやすい設定（なくても動くが、事故が減る）
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,    # 切れた接続を自動で検知
    "pool_recycle": 300,    # 長時間起動での接続切れ対策
}

# db init（models.pyのdbをアプリに紐付ける）
db.init_app(app)
migrate = Migrate(app, db)


# =========================================
# 動作確認用ルート
# =========================================

@app.route("/")
def index():
    return "MVP-01 Role Todo: Hello!"