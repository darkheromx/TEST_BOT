#Path : scripts/backup.sh
#!/usr/bin/env bash
# scripts/backup.sh
# Auto Backup P9s_CHATBOT Data & FAISS Index

set -euo pipefail

# 1) กำหนดเส้นทาง
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$BASE_DIR/data"
BACKUP_ROOT="/home/pi/backups"      # โฟลเดอร์ local backup
DATE="$(date +%F)"                  # YYYY-MM-DD
BACKUP_DIR="$BACKUP_ROOT/$DATE"

# 2) สร้างโฟลเดอร์สำรอง
mkdir -p "$BACKUP_DIR"

# 3) คัดลอกไฟล์สำคัญ
cp "$DATA_DIR/main.db"       "$BACKUP_DIR/main.db"
cp "$DATA_DIR/faiss_index.bin" "$BACKUP_DIR/faiss_index.bin"
cp "$DATA_DIR/faq_mapping.pkl" "$BACKUP_DIR/faq_mapping.pkl"

# 4) สำรองขึ้น Cloud ผ่าน rclone
#    – แก้ mydrive: ตามชื่อ remote ของคุณ
REMOTE_NAME="mydrive"
REMOTE_PATH="backups/P9s_CHATBOT/$DATE"

rclone copy "$BACKUP_DIR" "$REMOTE_NAME:$REMOTE_PATH" \
    --create-empty-src-dirs \
    --progress

# 5) ลบสำรองเก่ากว่า 7 วัน (local)
find "$BACKUP_ROOT" -maxdepth 1 -type d -mtime +7 \
    -exec rm -rf {} \;

echo "Backup completed: $BACKUP_DIR → $REMOTE_NAME:$REMOTE_PATH"
