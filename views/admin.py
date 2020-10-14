from datetime import datetime, timedelta

from flask import render_template, request, redirect, url_for, session
from flask import jsonify
from sqlalchemy import extract

from models import db
from models.index import Category, News, User
from . import admin_blu


@admin_blu.route("/admin")
def admin():
    user_id = session.get("user_id")
    user = db.session.query(User).filter(User.id == user_id).first()
    if not user:
        # 如果用户未登录，那么直接跳转到前台首页
        return redirect("index_blu.index")

    return render_template("admin/index.html",user=user)


@admin_blu.route("/admin/user_count.html")
def user_count():
    # 查询总数
    total_count = db.session.query(User).count()

    # 统计当月用户的新增数量
    now_date = datetime.now()  # datetime
    year = now_date.year
    month = now_date.month
    month_count = db.session.query(User).filter(extract('year', User.create_time) == year,
                                                extract('month', User.create_time) == month).count()

    # 统计当天用户的新增数量
    day = now_date.day
    day_count = db.session.query(User).filter(extract("year", User.create_time) == year,
                                              extract("month", User.create_time) == month,
                                              extract("day", User.create_time) == day).count()

    # 计算出近30天的数据
    counts_li = []
    date_li = []
    begin_date = now_date - timedelta(days=29)

    for i in range(0, 30):
        # 计算当前日期
        cur_date = begin_date + timedelta(days=i)

        # 获取当前日期的年月日
        year = cur_date.year
        month = cur_date.month
        day = cur_date.day

        # 计算出当天新增用户数量
        count = db.session.query(User).filter(extract('year', User.last_login) == year,
                                              extract('month', User.last_login) == month,
                                              extract('day', User.last_login) == day).count()

        # 把当天新增用户数量保存在counts_li列表中
        counts_li.append(count)

        # 保存当前日期
        date_str = cur_date.strftime('%Y-%m-%d')
        date_li.append(date_str)

    return render_template("admin/user_count.html", total_count=total_count, month_count=month_count,
                           day_count=day_count, counts_li=counts_li, date_li=date_li)


@admin_blu.route("/admin/user_list.html")
def user_list():
    page = int(request.args.get("page", 1))
    paginate = db.session.query(User).paginate(page, 5, False)
    return render_template("admin/user_list.html", paginate=paginate)


@admin_blu.route("/admin/news_review.html")
def news_review():
    page = int(request.args.get("page", 1))
    paginate = db.session.query(News).order_by(-News.create_time).paginate(page, 5, False)
    return render_template("admin/news_review.html", paginate=paginate)


@admin_blu.route("/admin/news_review_detail.html")
def news_review_detail():
    # 提取新闻
    news_id = int(request.args.get('id', 0))
    news = db.session.query(News).filter(News.id == news_id).first()
    return render_template("admin/news_review_detail.html", news=news)


@admin_blu.route("/admin/news_review_detail/<int:news_id>", methods=["POST"])
def save_news_review_detail(news_id):
    # 获取新闻
    news = db.session.query(News).filter(News.id == news_id).first()
    if not news:
        # 如果没有这个新闻，就返回error信息
        return jsonify({
            "errno": 5003,
            "errmsg": "未找到对应的新闻"
        })

    # 提取，审核结果
    action = request.json.get("action")
    if action == "accept":
        news.status = 0
    else:
        news.status = -1

    # 保存到数据库
    db.session.commit()

    # 返回对应信息
    return jsonify({
        "errno": 0,
        "errmsg": "成功"
    })


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
