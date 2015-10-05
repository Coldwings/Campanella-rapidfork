# coding:utf-8
from datetime import datetime
import decimal
import json
import six
import logging
import traceback
from tornado import escape
from tornado.web import RequestHandler, HTTPError


def tojson(data, ensure_ascii=True, default=False, **kwargs):
    def serializable(obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        raise TypeError

    _default = serializable if default else None
    return json.dumps(data,
                      ensure_ascii=ensure_ascii,
                      default=_default,
                      separators=(',', ':'),
                      **
                      kwargs).replace("</", "<\\/")


class RESTfulHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def check_xsrf_cookie(self):
        """ RESTful 禁用 XSRF 保护机制 """
        pass

    def finish(self, chunk=None, message=None):
        if chunk is None:
            chunk = {}
        if isinstance(chunk, dict):
            chunk = {"code": self._status_code, "content": chunk}
            if message:
                chunk["message"] = message
            chunk = tojson(chunk, default=True, ensure_ascii=False)
        else:
            chunk = six.text_type(chunk)
        callback = escape.utf8(self.get_argument("callback", None))
        if callback:
            self.set_header("Content-Type", "application/x-javascript")
            setattr(self, '_write_buffer', [callback, "(", chunk, ")"] if chunk else [])
            super(RESTfulHandler, self).finish()
        else:
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            super(RESTfulHandler, self).finish(chunk)

    def write_error(self, status_code, **kwargs):
        """覆盖自定义错误."""
        debug = self.settings.get("debug", False)
        try:
            exc_info = kwargs.pop('exc_info')
            e = exc_info[1]
            if isinstance(e, RESTfulHTTPError):
                pass
            elif isinstance(e, HTTPError):
                e = RESTfulHTTPError(e.status_code)
            else:
                e = RESTfulHTTPError(500)
            exception = "".join([ln for ln in traceback.format_exception(
                *exc_info)])
            if status_code == 500 and not debug:
                pass
            if debug:
                e.error["exception"] = exception
            self.clear()
            self.set_status(200)  # 使 RESTful 接口错误总是返回成功(200 OK)
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.finish(six.text_type(e))
        except Exception:
            logging.error(traceback.format_exc())
            return super(RESTfulHandler, self).write_error(status_code, **
                                                           kwargs)


class RESTfulHTTPError(HTTPError):
    """ API 错误异常模块：
        API服务器产生内部服务器错误时总是向客户返回JSON格式的数据.
    """
    _error_types = {
        400: "参数错误",
        401: "认证失败",
        403: "未经授权",
        404: "终端错误",
        405: "未许可的方法",
        500: "服务器错误"
    }

    def __init__(self, status_code=400, error_detail="", error_type="", content="", log_message=None, *args):
        super(RESTfulHTTPError, self).__init__(int(status_code), log_message, *
                                               args)
        self.error_detail = error_detail
        self.error = {'type': error_type} if error_type else {
            'type': self._error_types.get(self.status_code, "未知错误")
        }
        self.content = content if content else {}

    def __str__(self):
        message = {"code": self.status_code}
        self._set_message(message, ["error", "content"])
        if self.error_detail:
            message["error"]["detail"] = self.error_detail
        return tojson(message, default=True, ensure_ascii=False)

    def _set_message(self, err, names):
        for name in names:
            v = getattr(self, name)
            if v:
                err[name] = v


class DefaultRESTfulHandler(RESTfulHandler):
    """ 不存在的RESTfultHandler请求都返回JSON格式404错误
        *** 在相应的urls最末行设置如(r".*", DefaultRESTfulHandler)路由即可
    """

    def prepare(self):
        super(DefaultRESTfulHandler, self).prepare()
        raise RESTfulHTTPError(404)
