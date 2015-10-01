# coding:utf-8
import six
import logging
import traceback
from tornado import escape
from tornado.web import RequestHandler, HTTPError


class RESTfulHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def check_xsrf_cookie(self):
        # RESTful 禁用 XSRF 保护机制
        pass

    def finish(self, chunk=None, message=None):
        if chunk is None:
            chunk = {}
        if isinstance(chunk, dict):
            chunk = {"code": self._status_code, "content": chunk}
        if message:
            chunk["message"] = message
        callback = escape.utf8(self.get_argument("callback", None))
        if callback:
            self.set_header("Content-Type", "application/x-javascript")
            if isinstance(chunk, dict):
                chunk = escape.json_encode(chunk)
            setattr(self, '_write_buffer', [callback, "(", chunk, ")"] if chunk else [])
            super(RESTfulHandler, self).finish()
        else:
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            super(RESTfulHandler, self).finish(escape.json_encode(chunk))

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
            exception = "".join([ln for ln in traceback.format_exception(*exc_info)])
            if status_code == 500 and not debug:
                pass
            if debug:
                e.error["exception"] = exception
            self.clear()
            self.set_status(200)
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.finish(six.text_type(e))
        except Exception:
            logging.error(traceback.format_exc())
            return super(RESTfulHandler, self).write_error(status_code, **kwargs)


class RESTfulHTTPError(HTTPError):
    """ API 错误异常模块：
        API服务器产生内部服务器错误时总是向客户返回JSON格式的数据.
    """
    _error_types = {400: "参数错误",
                    401: "认证失败",
                    403: "未经授权",
                    404: "终端错误",
                    405: "未许可的方法",
                    500: "服务器错误"}

    def __init__(self, status_code=400, error_detail="", error_type="", content="", log_message=None, *args):
        super(RESTfulHTTPError, self).__init__(int(status_code), log_message, *args)
        self.error_detail = error_detail
        self.error = {'type': error_type} if error_type else {'type': self._error_types.get(self.status_code, "未知错误")}
        self.content = content if content else {}

    def __str__(self):
        message = {"code": self.status_code}
        self._set_message(message, ["error", "content"])
        if self.error_detail:
            message["error"]["detail"] = self.error_detail
        return escape.json_encode(message)

    def _set_message(self, err, names):
        for name in names:
            v = getattr(self, name)
            if v:
                err[name] = v
