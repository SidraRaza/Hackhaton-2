# Database Backup and Restore Procedures: Phase V

## Overview
This document outlines the backup and restore procedures for the Phase V Advanced Cloud Deployment database, ensuring data protection and disaster recovery capabilities for the enhanced schema with priorities, tags, recurrence, and event-driven architecture.

## Backup Strategy

### 1. Backup Types

#### 1.1 Logical Backups (pg_dump)
- **Frequency**: Daily at 2:00 AM UTC
- **Retention**: 30 days locally, 1 year in cold storage
- **Content**: Complete logical backup of all tables, sequences, functions, and views
- **Compression**: gzip compression to reduce storage requirements
- **Encryption**: AES-256 encryption for sensitive data

#### 1.2 Physical Backups (WAL Archiving)
- **Frequency**: Continuous (WAL shipping)
- **Retention**: 7 days in hot storage, 30 days in warm storage
- **Content**: Write-Ahead Log segments for point-in-time recovery
- **Location**: S3-compatible storage (Neon's built-in backup system)

#### 1.3 Event Store Backups
- **Frequency**: Hourly snapshots of event streams
- **Retention**: 90 days for audit trails
- **Content**: Complete event store with metadata
- **Verification**: SHA256 checksums for data integrity

### 2. Backup Scripts

#### 2.1 Daily Backup Script
```bash
#!/bin/bash
# backup-daily.sh - Daily backup for Phase V database

set -e  # Exit on any error

# Configuration
DB_NAME="${DB_NAME:-todo_app}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-/backups}"
DATE_STAMP=$(date +"%Y%m%d_%H%M%S")
ENCRYPTION_KEY="${ENCRYPTION_KEY:-fallback-key}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR/daily"

echo "Starting daily backup at $(date)"

# Create logical backup
pg_dump \
  --dbname="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME" \
  --format=custom \
  --compress=9 \
  --no-owner \
  --no-privileges \
  --verbose \
  --file="$BACKUP_DIR/daily/backup_$DATE_STAMP.dump"

# Compress the backup
gzip "$BACKUP_DIR/daily/backup_$DATE_STAMP.dump"

# Encrypt if key is provided
if [ -n "$ENCRYPTION_KEY" ]; then
  openssl enc -aes-256-cbc -salt -in "$BACKUP_DIR/daily/backup_$DATE_STAMP.dump.gz" -out "$BACKUP_DIR/daily/backup_$DATE_STAMP.dump.gz.enc" -k "$ENCRYPTION_KEY"
  rm "$BACKUP_DIR/daily/backup_$DATE_STAMP.dump.gz"
  echo "Backup encrypted and saved to $BACKUP_DIR/daily/backup_$DATE_STAMP.dump.gz.enc"
else
  echo "Backup compressed and saved to $BACKUP_DIR/daily/backup_$DATE_STAMP.dump.gz"
fi

# Calculate checksum
if [ -f "$BACKUP_DIR/daily/backup_$DATE_STAMP.dump.gz.enc" ]; then
  sha256sum "$BACKUP_DIR/daily/backup_$DATE_STAMP.dump.gz.enc" > "$BACKUP_DIR/daily/backup_$DATE_STAMP.checksum"
else
  sha256sum "$BACKUP_DIR/daily/backup_$DATE_STAMP.dump.gz" > "$BACKUP_DIR/daily/backup_$DATE_STAMP.checksum"
fi

# Upload to cloud storage (optional)
if [ -n "$AWS_ACCESS_KEY_ID" ]; then
  aws s3 cp "$BACKUP_DIR/daily/backup_$DATE_STAMP.dump.gz.enc" "s3://todo-backups/daily/" --storage-class STANDARD_IA
  aws s3 cp "$BACKUP_DIR/daily/backup_$DATE_STAMP.checksum" "s3://todo-backups/daily/" --storage-class STANDARD_IA
fi

# Clean up old backups (keep last 30 days)
find "$BACKUP_DIR/daily/" -name "*.dump.gz*" -mtime +30 -delete
find "$BACKUP_DIR/daily/" -name "*.checksum" -mtime +30 -delete

echo "Daily backup completed at $(date)"
```

#### 2.2 Weekly Full Backup Script
```bash
#!/bin/bash
# backup-weekly.sh - Weekly full backup with extended retention

set -e

# Configuration
DB_NAME="${DB_NAME:-todo_app}"
BACKUP_DIR="${BACKUP_DIR:-/backups}"
DATE_STAMP=$(date +"%Y%m%d_%H%M%S")

mkdir -p "$BACKUP_DIR/weekly"

echo "Starting weekly full backup at $(date)"

# Create full backup with all objects
pg_dumpall \
  --host="$DB_HOST" \
  --username="$DB_USER" \
  --globals-only \
  --filename="$BACKUP_DIR/weekly/globals_$DATE_STAMP.sql"

pg_dump \
  --dbname="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME" \
  --format=custom \
  --compress=9 \
  --verbose \
  --file="$BACKUP_DIR/weekly/full_backup_$DATE_STAMP.dump"

# Compress and encrypt
gzip "$BACKUP_DIR/weekly/full_backup_$DATE_STAMP.dump"
openssl enc -aes-256-cbc -salt -in "$BACKUP_DIR/weekly/full_backup_$DATE_STAMP.dump.gz" -out "$BACKUP_DIR/weekly/full_backup_$DATE_STAMP.dump.gz.enc" -k "$ENCRYPTION_KEY"

# Upload to long-term storage
if [ -n "$AWS_ACCESS_KEY_ID" ]; then
  aws s3 cp "$BACKUP_DIR/weekly/full_backup_$DATE_STAMP.dump.gz.enc" "s3://todo-backups/weekly/" --storage-class GLACIER
  aws s3 cp "$BACKUP_DIR/weekly/globals_$DATE_STAMP.sql" "s3://todo-backups/weekly/" --storage-class GLACIER
fi

# Clean up old weekly backups (keep last 52 weeks)
find "$BACKUP_DIR/weekly/" -name "*.dump.gz.enc" -mtime +365 -delete
find "$BACKUP_DIR/weekly/" -name "*.sql" -mtime +365 -delete

echo "Weekly backup completed at $(date)"
```

#### 2.3 Event Store Specific Backup
```bash
#!/bin/bash
# backup-events.sh - Backup event store with special handling for events table

set -e

DB_NAME="${DB_NAME:-todo_app}"
BACKUP_DIR="${BACKUP_DIR:-/backups}"
DATE_STAMP=$(date +"%Y%m%d_%H%M%S")

mkdir -p "$BACKUP_DIR/events"

echo "Starting event store backup at $(date)"

# Backup events table separately due to size and importance
pg_dump \
  --dbname="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME" \
  --table="events" \
  --format=custom \
  --compress=9 \
  --verbose \
  --file="$BACKUP_DIR/events/events_backup_$DATE_STAMP.dump"

# Create backup of events with partitioning consideration
# If events table is partitioned by date, backup each partition separately
for partition in $(psql -d "$DB_NAME" -t -c "SELECT partition_of FROM pg_partitioned_table WHERE partition_of = 'events';"); do
  pg_dump \
    --dbname="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME" \
    --table="$partition" \
    --format=custom \
    --compress=9 \
    --verbose \
    --file="$BACKUP_DIR/events/${partition}_backup_$DATE_STAMP.dump"
done

# Compress and upload to high-availability storage
gzip "$BACKUP_DIR/events/events_backup_$DATE_STAMP.dump"
aws s3 cp "$BACKUP_DIR/events/events_backup_$DATE_STAMP.dump.gz" "s3://todo-backups/events/" --storage-class ONEZONE_IA

echo "Event store backup completed at $(date)"
```

### 3. Automated Backup Schedule (Cron Jobs)

#### 3.1 Crontab Entries
```bash
# Add to crontab with: crontab -e

# Daily backups at 2:00 AM UTC
0 2 * * * /opt/todo-app/scripts/backup-daily.sh >> /var/log/todo-backup.log 2>&1

# Weekly backups at 3:00 AM on Sundays
0 3 * * 0 /opt/todo-app/scripts/backup-weekly.sh >> /var/log/todo-weekly-backup.log 2>&1

# Hourly event backups at 15 minutes past the hour
15 * * * * /opt/todo-app/scripts/backup-events.sh >> /var/log/todo-events-backup.log 2>&1

# Weekly backup verification on Saturdays at 4:00 AM
0 4 * * 6 /opt/todo-app/scripts/verify-backups.sh >> /var/log/todo-verify-backup.log 2>&1
```

## Restore Procedures

### 1. Emergency Restore Process

#### 1.1 Immediate Response
1. **Assess the situation**:
   - Determine scope of data loss
   - Identify the time of last known good state
   - Check available backups and their timestamps

2. **Activate incident response**:
   - Notify stakeholders
   - Switch to read-only mode if possible
   - Document the incident for post-mortem

3. **Prepare restore environment**:
   - Provision new database instance if needed
   - Ensure sufficient disk space
   - Prepare restore scripts and procedures

#### 1.2 Restore Process
```bash
#!/bin/bash
# restore-database.sh - Emergency database restore script

set -e

# Configuration
DB_NAME="${RESTORE_DB_NAME:-todo_app_restore}"
BACKUP_FILE="$1"  # Path to backup file
ENCRYPTION_KEY="$2"  # Encryption key if backup is encrypted

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup_file> [encryption_key]"
  exit 1
fi

echo "Starting database restore from $BACKUP_FILE at $(date)"

# Decrypt if necessary
if [[ "$BACKUP_FILE" == *.enc ]]; then
  if [ -z "$ENCRYPTION_KEY" ]; then
    echo "ERROR: Backup is encrypted but no decryption key provided"
    exit 1
  fi

  TEMP_DECRYPTED=$(mktemp --suffix=.dump.gz)
  openssl enc -aes-256-cbc -d -in "$BACKUP_FILE" -out "$TEMP_DECRYPTED" -k "$ENCRYPTION_KEY"
  BACKUP_FILE="$TEMP_DECRYPTED"
fi

# Decompress if necessary
if [[ "$BACKUP_FILE" == *.gz ]]; then
  TEMP_DECOMPRESSED=$(mktemp --suffix=.dump)
  gunzip -c "$BACKUP_FILE" > "$TEMP_DECOMPRESSED"
  BACKUP_FILE="$TEMP_DECOMPRESSED"
fi

# Verify backup integrity using checksum
if [ -f "${BACKUP_FILE%.dump.gz}.checksum" ]; then
  echo "Verifying backup integrity..."
  if ! sha256sum -c "${BACKUP_FILE%.dump.gz}.checksum"; then
    echo "ERROR: Backup integrity check failed"
    exit 1
  fi
  echo "Backup integrity verified"
fi

# Create database if it doesn't exist
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
  PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;"

# Restore the database
pg_restore \
  --dbname="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME" \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  --verbose \
  "$BACKUP_FILE"

# Verify restoration
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "
SELECT
  (SELECT COUNT(*) FROM tasks) as task_count,
  (SELECT COUNT(*) FROM tags) as tag_count,
  (SELECT COUNT(*) FROM events) as event_count;
"

echo "Database restore completed at $(date)"
echo "Please verify application functionality before switching traffic"
```

#### 1.3 Point-in-Time Recovery (PITR)
```bash
#!/bin/bash
# restore-pitr.sh - Point-in-time recovery using WAL files

set -e

TARGET_TIME="$1"  # Target timestamp for recovery
BACKUP_BASE="$2"  # Base backup directory

if [ -z "$TARGET_TIME" ] || [ -z "$BACKUP_BASE" ]; then
  echo "Usage: $0 <target_time> <backup_base_dir>"
  echo "Example: $0 '2026-01-15 14:30:00' /backups/base_20260115"
  exit 1
fi

echo "Starting PITR to $TARGET_TIME using base backup from $BACKUP_BASE"

# Stop PostgreSQL service
sudo systemctl stop postgresql

# Remove current data directory
sudo rm -rf /var/lib/postgresql/15/main/*

# Restore base backup
sudo -u postgres pg_restore --clean --if-exists --no-owner --no-privileges "$BACKUP_BASE/base_backup.dump"

# Configure recovery.conf for WAL replay
cat > /var/lib/postgresql/15/main/recovery.conf << EOF
restore_command = 'cp /backups/wal/%f %p'
recovery_target_time = '$TARGET_TIME'
recovery_target_action = promote
EOF

# Start PostgreSQL in recovery mode
sudo systemctl start postgresql

# Wait for recovery to complete
while sudo -u postgres psql -t -c "SELECT pg_is_in_recovery();" | grep -q "t"; do
  echo "Recovery in progress..."
  sleep 10
done

echo "PITR completed to $TARGET_TIME"