
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, g


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.update(
        SECRET_KEY="polling-app-secret",
        DATABASE=os.path.join(app.root_path, "polls.db")
    )

    if test_config:
        app.config.update(test_config)

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db

    @app.teardown_appcontext
    def close_db(error=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        db = get_db()

        db.execute("""
            CREATE TABLE IF NOT EXISTS polls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poll_id INTEGER NOT NULL,
                option_text TEXT NOT NULL,
                FOREIGN KEY (poll_id) REFERENCES polls(id)
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poll_id INTEGER NOT NULL,
                option_id INTEGER NOT NULL,
                voter_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (poll_id) REFERENCES polls(id),
                FOREIGN KEY (option_id) REFERENCES options(id),
                UNIQUE (poll_id, voter_id)
            )
        """)

        db.commit()

    with app.app_context():
        init_db()

    @app.route("/")
    def index():
        polls = get_db().execute(
            "SELECT * FROM polls ORDER BY id DESC"
        ).fetchall()

        return render_template("index.html", polls=polls)

    @app.route("/create", methods=["GET", "POST"])
    def create_poll():
        if request.method == "POST":

            question = request.form.get("question", "").strip()

            options = [
                value.strip()
                for value in request.form.getlist("options")
                if value.strip()
            ]

            if not question:
                flash("Please enter a poll question.", "error")
                return render_template("create_poll.html")

            if len(options) < 2:
                flash("A poll must have at least two options.", "error")
                return render_template("create_poll.html")

            normalized = [option.casefold() for option in options]

            if len(normalized) != len(set(normalized)):
                flash("Duplicate options are not allowed.", "error")
                return render_template("create_poll.html")

            db = get_db()

            cursor = db.execute(
                "INSERT INTO polls (question) VALUES (?)",
                (question,)
            )

            poll_id = cursor.lastrowid

            db.executemany(
                "INSERT INTO options (poll_id, option_text) VALUES (?, ?)",
                [(poll_id, option) for option in options]
            )

            db.commit()

            flash("Poll created successfully!", "success")

            return redirect(url_for("poll_detail", poll_id=poll_id))

        return render_template("create_poll.html")

    @app.route("/poll/<int:poll_id>", methods=["GET"])
    def poll_detail(poll_id):

        db = get_db()

        poll = db.execute(
            "SELECT * FROM polls WHERE id = ?",
            (poll_id,)
        ).fetchone()

        if poll is None:
            return "Poll not found", 404

        options = db.execute(
            "SELECT * FROM options WHERE poll_id = ?",
            (poll_id,)
        ).fetchall()

        return render_template(
            "poll_detail.html",
            poll=poll,
            options=options
        )

    @app.route("/poll/<int:poll_id>/vote", methods=["POST"])
    def vote(poll_id):

        db = get_db()

        poll = db.execute(
            "SELECT * FROM polls WHERE id = ?",
            (poll_id,)
        ).fetchone()

        if poll is None:
            return "Poll not found", 404

        voter_id = request.form.get("voter_id", "").strip().casefold()
        option_id = request.form.get("option_id", "").strip()

        if not voter_id:
            flash("Please enter your voter ID.", "error")
            return redirect(url_for("poll_detail", poll_id=poll_id))

        if not option_id.isdigit():
            flash("Please select a valid option.", "error")
            return redirect(url_for("poll_detail", poll_id=poll_id))

        option = db.execute(
            """
            SELECT * FROM options
            WHERE id = ? AND poll_id = ?
            """,
            (int(option_id), poll_id)
        ).fetchone()

        if option is None:
            flash("Invalid voting option.", "error")
            return redirect(url_for("poll_detail", poll_id=poll_id))

        try:
            db.execute(
                """
                INSERT INTO votes (poll_id, option_id, voter_id)
                VALUES (?, ?, ?)
                """,
                (poll_id, int(option_id), voter_id)
            )

            db.commit()

            flash("Your vote was submitted successfully!", "success")

        except sqlite3.IntegrityError:
            db.rollback()

            flash("You have already voted in this poll.", "error")

        return redirect(url_for("poll_detail", poll_id=poll_id))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)