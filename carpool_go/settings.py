from pathlib import Path
import os, dj_database_url
BASE_DIR=Path(__file__).resolve().parent.parent
SECRET_KEY=os.getenv('SECRET_KEY','dev-only-change-me')
DEBUG=os.getenv('DEBUG','1' if not os.getenv('RENDER') else '0')=='1'
# 2026-10-05：開發模式允許區網 IP 連入；Render 正式環境仍採白名單。
if DEBUG:
    ALLOWED_HOSTS=['*']
else:
    ALLOWED_HOSTS=['localhost','127.0.0.1','[::1]']
    if os.getenv('RENDER_EXTERNAL_HOSTNAME'): ALLOWED_HOSTS.append(os.getenv('RENDER_EXTERNAL_HOSTNAME'))
    extra=os.getenv('ALLOWED_HOSTS','')
    if extra: ALLOWED_HOSTS += [x.strip() for x in extra.split(',') if x.strip()]
CSRF_TRUSTED_ORIGINS=[x.strip() for x in os.getenv('CSRF_TRUSTED_ORIGINS','').split(',') if x.strip()]
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','rides']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF='carpool_go.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION='carpool_go.wsgi.application'; ASGI_APPLICATION='carpool_go.asgi.application'
DATABASES={'default':dj_database_url.config(default=f"sqlite:///{BASE_DIR/'db.sqlite3'}",conn_max_age=600,conn_health_checks=True)}
AUTH_PASSWORD_VALIDATORS=[]
LANGUAGE_CODE='zh-hant'; TIME_ZONE='Asia/Taipei'; USE_I18N=True; USE_TZ=True
STATIC_URL='/static/'; STATIC_ROOT=BASE_DIR/'staticfiles'; STATICFILES_DIRS=[BASE_DIR/'static']
STORAGES={'staticfiles':{'BACKEND':'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https')
