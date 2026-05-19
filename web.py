from flask import Flask, redirect, render_template, request, url_for

from crawler.run import run as run_crawler
from crawler.schools import SCHOOLS
from storage.db import get_stats, list_posts


app = Flask(__name__)


@app.route("/")
def index():
    keyword = request.args.get("q", "").strip()
    school = request.args.get("school", "").strip()
    posts = list_posts(keyword=keyword, school=school)
    stats = get_stats()

    return render_template(
        "index.html",
        posts=posts,
        stats=stats,
        schools=SCHOOLS,
        keyword=keyword,
        selected_school=school,
    )


@app.post("/crawl")
def crawl():
    run_crawler()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
