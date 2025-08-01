#!/usr/bin/env bash
# scripts/restore.sh
# Restore P9s_CHATBOT Data from Backup

set -euo pipefail

# 1) กำหนด remote & date
REMOTE_NAME="mydrive"                    # ชื่อ rclone remote
TARGET_DATE="$1"                         # ต้องระบุ YYYY-MM-DD
REMOTE_PATH="backups/P9s_CHATBOT/$TARGET_DATE"
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$BASE_DIR/data"
RESTORE_DIR="/tmp/restore_$TARGET_DATE"

# 2) ดาวน์โหลดสำรองจาก Cloud มา local temp
mkdir -p "$RESTORE_DIR"
rclone copy "$REMOTE_NAME:$REMOTE_PATH" "$RESTORE_DIR" --progress

# 3) หยุด service ก่อน (ถ้าใช้ systemd)
sudo systemctl stop p9s_chatbot.service || true

# 4) สำรองไฟล์ปัจจุบันไว้ก่อน
mkdir -p "$BASE_DIR/data_backup_$(date +%F_%T)"
cp -r "$DATA_DIR"/* "$BASE_DIR/data_backup_$(date +%F_%T)/"

# 5) คัดลอกไฟล์จาก restore ไป data
cp "$RESTORE_DIR/main.db"       "$DATA_DIR/main.db"
cp "$RESTORE_DIR/faiss_index.bin" "$DATA_DIR/faiss_index.bin"
cp "$RESTORE_DIR/faq_mapping.pkl" "$DATA_DIR/faq_mapping.pkl"

# 6) เริ่ม service ใหม่
sudo systemctl start p9s_chatbot.service || true

echo "Restore completed from $TARGET_DATE"
