from apps.vadmin.analysis.views import app as vadmin_analysis_app
from apps.vadmin.auth.utils.login import app as auth_app
from apps.vadmin.auth.views import app as vadmin_auth_app
from apps.vadmin.help.views import app as vadmin_help_app
from apps.vadmin.record.views import app as vadmin_record_app
from apps.vadmin.resource.views import app as vadmin_resource_app
from apps.vadmin.system.views import app as vadmin_system_app
from apps.vadmin.workplace.views import app as vadmin_workplace_app


# 引入应用中的路由
urlpatterns = [
    {"ApiRouter": auth_app, "prefix": "/auth", "tags": ["系统認證"]},
    {"ApiRouter": vadmin_auth_app, "prefix": "/vadmin/auth", "tags": ["權限管理"]},
    {"ApiRouter": vadmin_system_app, "prefix": "/vadmin/system", "tags": ["系统管理"]},
    {"ApiRouter": vadmin_record_app, "prefix": "/vadmin/record", "tags": ["紀錄管理"]},
    {"ApiRouter": vadmin_workplace_app, "prefix": "/vadmin/workplace", "tags": ["工作區管理"]},
    {"ApiRouter": vadmin_analysis_app, "prefix": "/vadmin/analysis", "tags": ["數據分析管理"]},
    {"ApiRouter": vadmin_help_app, "prefix": "/vadmin/help", "tags": ["幫助中心管理"]},
    {"ApiRouter": vadmin_resource_app, "prefix": "/vadmin/resource", "tags": ["資源管理"]},
]
