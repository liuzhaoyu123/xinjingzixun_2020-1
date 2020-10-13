from flask import render_template, request, redirect, url_for
from flask import jsonify

from models import db
from models.index import Category, News
from . import admin_blu


@admin_blu.route("/admin")
def admin():
    return render_template("admin/index.html")


@admin_blu.route("/admin/user_count.html")
def user_count():
    return render_template("admin/user_count.html")


@admin_blu.route("/admin/user_list.html")
def user_list():
    return render_template("admin/user_list.html")


@admin_blu.route("/admin/news_review.html")
def news_review():
    page = int(request.args.get("page", 1))
    paginate = db.session.query(News).order_by(-News.create_time).paginate(page, 5, False)
    return render_template("admin/news_review.html", paginate=paginate)


@admin_blu.route("/admin/news_review_detail.html")
def news_review_detail():
    return render_template("admin/news_review_detail.html")


@admin_blu.route("/admin/news_edit.html")
def news_edit():
    page = int(request.args.get("page", 1))
    paginate = db.session.query(News).paginate(page, 5, False)
    return render_template("admin/news_edit.html", paginate=paginate)


@admin_blu.route("/admin/news_edit_detail.html")
def news_edit_detail():
    # 查询当前新闻
    news_id = int(request.args.get("id", 0))
    news = db.session.query(News).filter(News.id == news_id).first()
    # 获取新闻可选择的所有列表
    categorys = db.session.query(Category).filter(Category.id != 1).all()
    return render_template("admin/news_edit_detail.html", news=news, categorys=categorys)


@admin_blu.route("/admin/news_edit_detail/<int:news_id>", methods=["POST"])
def save_news(news_id):
    # 更新新闻
    news = db.session.query(News).filter(News.id == news_id).first()
    if not news:
        # 如果没有id，那么就无需保存
        ret = {
            "errno": 5002,
            "errmsg": "没有对应的新闻"
        }
        return jsonify(ret)

    news.title = request.form.get("title")
    news.digest = request.form.get("digest")
    news.content = request.form.get("content")
    news.category_id = request.form.get("category_id")
    index_image_url = request.form.get("index_image_url")
    if index_image_url:
        news.index_image_url = index_image_url

    # 将修改的信息写入到数据库，此时真的更新成功
    db.session.commit()
    ret = {
        "errno": 0,
        "errmsg": "成功"
    }
    return jsonify(ret)


@admin_blu.route("/admin/news_type.html")
def news_type():
    news_types = db.session.query(Category).filter(Category.id != 1).all()
    return render_template("admin/news_type.html", news_types=news_types)


@admin_blu.route("/admin/news_type", methods=["POST"])
def news_type_edit_or_add():
    # 提取参数
    category_id = request.json.get("id")
    category_name = request.json.get("name")

    # 如果有id，那么就是表示编辑，否则认为是添加
    if category_id:
        # 编辑
        category = db.session.query(Category).filter(Category.id == category_id).first()
        if not category:
            ret = {
                "errno": 5001,
                "errmsg": "没有要修改的分类"
            }

            return jsonify(ret)

        category.name = category_name
        db.session.commit()
        ret = {
            "errno": 0,
            "errmsg": "成功"
        }

        return jsonify(ret)

    else:
        # 添加
        new_category = Category()
        new_category.name = category_name
        db.session.add(new_category)
        db.session.commit()
        ret = {
            "errno": 0,
            "errmsg": "成功"
        }

        return jsonify(ret)
