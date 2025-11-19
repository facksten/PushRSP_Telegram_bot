# راهنمای Deploy - PushTutor

## روش ۱: اجرای مستقیم

### نصب

```bash
# Clone repository
git clone <repo-url>
cd pushtutor

# Setup
chmod +x setup.sh
./setup.sh

# Configure
nano .env
# یا
vim .env
```

### اجرا

```bash
# در terminal
./run.sh

# یا مستقیم
python main.py
```

## روش ۲: Systemd Service

### نصب Service

```bash
# ویرایش فایل service
nano pushtutor.service

# تغییر مسیرها:
# - YOUR_USERNAME
# - /path/to/pushtutor

# کپی به systemd
sudo cp pushtutor.service /etc/systemd/system/

# فعال‌سازی
sudo systemctl daemon-reload
sudo systemctl enable pushtutor
sudo systemctl start pushtutor
```

### مدیریت Service

```bash
# وضعیت
sudo systemctl status pushtutor

# لاگ‌ها
sudo journalctl -u pushtutor -f

# ری‌استارت
sudo systemctl restart pushtutor

# توقف
sudo systemctl stop pushtutor
```

## روش ۳: Docker

### Build & Run

```bash
# Build image
docker-compose build

# اجرا
docker-compose up -d

# لاگ‌ها
docker-compose logs -f

# توقف
docker-compose down
```

### مدیریت

```bash
# ری‌استارت
docker-compose restart

# rebuild
docker-compose up -d --build

# حذف همه
docker-compose down -v
```

## روش ۴: Screen/Tmux

### با Screen

```bash
# ایجاد session
screen -S pushtutor

# اجرا
python main.py

# Detach: Ctrl+A و بعد D

# برگشت
screen -r pushtutor
```

### با Tmux

```bash
# ایجاد session
tmux new -s pushtutor

# اجرا
python main.py

# Detach: Ctrl+B و بعد D

# برگشت
tmux attach -t pushtutor
```

## Auto-restart با Supervisor

### نصب

```bash
sudo apt-get install supervisor
```

### کانفیگ

```ini
[program:pushtutor]
command=/path/to/pushtutor/venv/bin/python main.py
directory=/path/to/pushtutor
user=YOUR_USERNAME
autostart=true
autorestart=true
stderr_logfile=/path/to/pushtutor/logs/supervisor_error.log
stdout_logfile=/path/to/pushtutor/logs/supervisor.log
```

```bash
sudo cp pushtutor_supervisor.conf /etc/supervisor/conf.d/
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start pushtutor
```

## بررسی سلامت

### Health Check Script

```bash
#!/bin/bash
# health_check.sh

if ! pgrep -f "python main.py" > /dev/null; then
    echo "⚠️  PushTutor is not running!"
    # ارسال نوتیفیکیشن یا ری‌استارت
else
    echo "✅ PushTutor is running"
fi
```

### Cron برای Monitoring

```bash
# افزودن به crontab
crontab -e

# چک هر 5 دقیقه
*/5 * * * * /path/to/health_check.sh
```

## Backup

### دیتابیس

```bash
# کپی دیتابیس
cp pushtutor.db backups/pushtutor_$(date +%Y%m%d_%H%M%S).db

# یا با cron
0 2 * * * cp /path/to/pushtutor.db /path/to/backups/pushtutor_$(date +\%Y\%m\%d).db
```

### Session Files

```bash
# Userbot session
cp userbot_session.session backups/
```

## Monitoring و Logging

### مشاهده Logs

```bash
# Real-time
tail -f logs/pushtutor.log

# با grep
grep ERROR logs/pushtutor.log

# Last 100 lines
tail -n 100 logs/pushtutor.log
```

### Log Rotation با Logrotate

```bash
# /etc/logrotate.d/pushtutor
/path/to/pushtutor/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0644 user user
}
```

## Security

### محدود کردن دسترسی

```bash
# فایل .env
chmod 600 .env

# Session files
chmod 600 *.session

# Database
chmod 600 *.db
```

### Firewall

```bash
# اگر نیاز به باز کردن پورت نیست
# فقط outgoing connections لازمه
```

## Troubleshooting

### خطای Database Lock

```bash
# بستن همه instance‌های در حال اجرا
pkill -f "python main.py"

# حذف lock
rm pushtutor.db-journal
```

### مشکل Memory

```bash
# مشاهده استفاده
ps aux | grep python

# محدود کردن memory در systemd
MemoryLimit=512M
```

### خطای Import

```bash
# بررسی virtual environment
which python
pip list

# نصب مجدد
pip install -r requirements.txt --force-reinstall
```

## Performance

### پیشنهادات

- استفاده از PostgreSQL به جای SQLite در production
- فعال‌سازی Redis برای cache
- استفاده از load balancer برای چند instance
- Monitoring با Prometheus + Grafana

## Update

```bash
# گرفتن آخرین نسخه
git pull

# نصب dependencies جدید
pip install -r requirements.txt

# migrate database (اگر لازم باشه)
# python migrate.py

# ری‌استارت
sudo systemctl restart pushtutor
# یا
docker-compose restart
```
