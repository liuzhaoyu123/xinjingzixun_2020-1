from flask import render_template, jsonify, request

from models import db
from models.index import Category, News
from . import admin_blu


# 后台首页
@admin_blu.route("/admin")
def admin():
    return render_template("admin/index.html")


# 用户统计
@admin_blu.route("/admin/user_count.html")
def user_count():
    return render_template("admin/user_count.html")


# 用户列表
@admin_blu.route("/admin/user_list.html")
def user_list():
    return render_template("admin/user_list.html")


# 新闻审核
@admin_blu.route("/admin/news_review.html")
def news_review():
    return render_template("admin/news_review.html")


# 新闻版式编辑
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


# 新闻分类管理
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
