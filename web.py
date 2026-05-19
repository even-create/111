from flask import Flask, redirect, render_template, request, url_for

from crawler.run import run as run_crawler
from crawler.schools import SCHOOLS
from storage.db import get_notify_settings, get_stats, get_years, list_posts, set_setting


app = Flask(__name__)


@app.route("/")
def index():
    keyword = request.args.get("q", "").strip()
    school = request.args.get("school", "").strip()
    school_type = request.args.get("school_type", "").strip()
    category = request.args.get("category", "").strip()
    year = request.args.get("year", "").strip()
    posts = list_posts(
        keyword=keyword,
        school=school,
        school_type=school_type,
        category=category,
        year=year,
    )
    stats = get_stats()
    stats["monitored"] = len(SCHOOLS)

    return render_template(
        "index.html",
        posts=posts,
        stats=stats,
        schools=SCHOOLS,
        years=get_years(),
        notify=get_notify_settings(),
        keyword=keyword,
        selected_school=school,
        selected_school_type=school_type,
        selected_category=category,
        selected_year=year,
    )


@app.post("/crawl")
def crawl():
    run_crawler()
    return redirect(url_for("index"))


@app.post("/settings/notify")
def save_notify_settings():
    enabled = "notify_enabled" in request.form
    serverchan_key = request.form.get("serverchan_key", "").strip()
    set_setting("notify_enabled", "true" if enabled else "false")
    set_setting("serverchan_key", serverchan_key)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
