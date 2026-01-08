import os
import datetime
import subprocess
import shutil

def backup_database():
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'backup_db_{timestamp}.sqlite3'
    
    try:
        shutil.copy2('db.sqlite3', f'backups/{backup_file}')
        return f'Database backup created: {backup_file}'
    except Exception as e:
        return f'Backup failed: {str(e)}'

def backup_media():
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f'backups/media_{timestamp}'
    
    try:
        shutil.copytree('media', backup_dir)
        return f'Media backup created: {backup_dir}'
    except Exception as e:
        return f'Media backup failed: {str(e)}'

def cleanup_old_backups(days=7):
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    deleted = 0
    
    for filename in os.listdir('backups'):
        filepath = os.path.join('backups', filename)
        if os.path.getctime(filepath) < cutoff.timestamp():
            if os.path.isfile(filepath):
                os.remove(filepath)
            else:
                shutil.rmtree(filepath)
            deleted += 1
    
    return f'Cleaned up {deleted} old backup files'

if __name__ == '__main__':
    os.makedirs('backups', exist_ok=True)
    print(backup_database())
    print(backup_media())
    print(cleanup_old_backups())