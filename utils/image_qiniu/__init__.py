# -*- coding: utf-8 -*-
# flake8: noqa

from qiniu import Auth, put_file, etag
import qiniu.config

# 需要填写你的 Access Key 和 Secret Key
access_key = 'heT0_p9fPWbTMINhhxHbRL6XohWs7hI2PixaG1Vw'
secret_key = '1do20REgJpHL_f586cKulLPwXf1y5q0-Fx0JrqyP'

# 构建鉴权对象
q = Auth(access_key, secret_key)

# 要上传的空间
bucket_name = 'liuzhaoyu'

# url前缀
url_prefix = "http://qhpwv2fa1.hd-bkt.clouddn.com/"


def upload_image_to_qiniu(localfile, key):
    """
    上传图片到七牛云
    :param localfile:要上传的文件路径
    :param key:保存到七牛云之后的文件名
    :return: 上传成功之后，图片在七牛云的完整路径 包括http://
    """
    # 上传后保存的文件名
    # key = 'my-python-logo.png'

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)

    # 要上传文件的本地路径
    # localfile = './bbb.png'

    ret, info = put_file(token, key, localfile)
    print(info)
    assert ret['key'] == key
    assert ret['hash'] == etag(localfile)

    return url_prefix + key


if __name__ == "__main__":
    upload_image_to_qiniu()
