from django.db import connection

class ThemeManager:
    DEFAULT_THEME = {
        'primary_color': '#0014A8',
        'secondary_color': '#000E75',
        'success_color': '#28a745',
        'danger_color': '#dc3545',
        'warning_color': '#ffc107',
        'info_color': '#17a2b8',
        'font_family': 'Inter, sans-serif',
        'sidebar_bg': '#ffffff',
        'navbar_bg': '#0014A8',
        'mode': 'light'
    }
    
    @staticmethod
    def get_theme(user_id=None):
        if user_id:
            with connection.cursor() as cursor:
                cursor.execute('''
                    SELECT key, value FROM settings_systemsetting
                    WHERE category = 'theme' AND key LIKE 'theme_%'
                ''')
                theme = {row[0].replace('theme_', ''): row[1] for row in cursor.fetchall()}
                
                if theme:
                    return {**ThemeManager.DEFAULT_THEME, **theme}
        
        return ThemeManager.DEFAULT_THEME
    
    @staticmethod
    def save_theme(theme_data):
        with connection.cursor() as cursor:
            for key, value in theme_data.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO settings_systemsetting
                    (key, value, category, updated_at)
                    VALUES (?, ?, 'theme', datetime('now'))
                ''', [f'theme_{key}', value])
        
        return {'status': 'success', 'message': 'Theme saved'}
    
    @staticmethod
    def reset_theme():
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM settings_systemsetting WHERE category = 'theme'")
        
        return {'status': 'success', 'message': 'Theme reset to default'}
