from flask import render_template

from . import admin_blu

# 后台首页
@admin_blu.route("/admin")
def admin():
    return render_template("admin/index.html")

# 用户统计
@admin_blu.route("/user_count.html")
def user_count():
    return render_template("admin/user_count.html")

# 用户列表
@admin_blu.route("/user_list.html")
def user_list():
    return render_template("admin/user_list.html")

# 新闻审核
@admin_blu.route("/news_review.html")
def news_review():
    return render_template("admin/news_review.html")

# 新闻版式编辑
@admin_blu.route("/news_edit.html")
def news_edit():
    return render_template("admin/news_edit.html")

# 新闻分类管理
@admin_blu.route("/news_type.html")
def news_type():
    return render_template("admin/news_type.html")