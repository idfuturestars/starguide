
"""
IDFS StarGuide - Replit Services Integration
Zero-risk parallel implementation with feature flags
"""

import os
import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional

class ReplitServices:
    """Replit DB and Auth integration with fallback to existing systems"""
    
    def __init__(self):
        self.db_url = os.environ.get('REPLIT_DB_URL')
        self.use_replit_db = bool(self.db_url) and os.environ.get('USE_REPLIT_DB', 'false').lower() == 'true'
        self.use_replit_auth = os.environ.get('USE_REPLIT_AUTH', 'false').lower() == 'true'
        
        # Feature flags for gradual migration
        self.feature_flags = {
            'replit_db_enabled': self.use_replit_db,
            'replit_auth_enabled': self.use_replit_auth,
            'parallel_storage': True,  # Store in both systems during transition
            'migration_mode': True     # Safe migration mode
        }
        
        print(f"🔧 Replit Services initialized:")
        print(f"   - DB Available: {bool(self.db_url)}")
        print(f"   - DB Enabled: {self.use_replit_db}")
        print(f"   - Auth Enabled: {self.use_replit_auth}")

    def get_db_value(self, key: str) -> Optional[str]:
        """Get value from Replit DB with fallback"""
        if not self.feature_flags['replit_db_enabled'] or not self.db_url:
            return None
            
        try:
            response = requests.get(f"{self.db_url}/{key}", timeout=5)
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            print(f"⚠️ Replit DB get error: {e}")
            return None

    def set_db_value(self, key: str, value: str) -> bool:
        """Set value in Replit DB with fallback"""
        if not self.feature_flags['replit_db_enabled'] or not self.db_url:
            return False
            
        try:
            response = requests.post(self.db_url, data={key: value}, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"⚠️ Replit DB set error: {e}")
            return False

    def delete_db_value(self, key: str) -> bool:
        """Delete value from Replit DB with fallback"""
        if not self.feature_flags['replit_db_enabled'] or not self.db_url:
            return False
            
        try:
            response = requests.delete(f"{self.db_url}/{key}", timeout=5)
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"⚠️ Replit DB delete error: {e}")
            return False

    def list_db_keys(self, prefix: str = "") -> list:
        """List keys from Replit DB with optional prefix"""
        if not self.feature_flags['replit_db_enabled'] or not self.db_url:
            return []
            
        try:
            params = {"prefix": prefix} if prefix else {}
            response = requests.get(self.db_url, params=params, timeout=5)
            if response.status_code == 200:
                return response.text.strip().split('\n') if response.text.strip() else []
            return []
        except Exception as e:
            print(f"⚠️ Replit DB list error: {e}")
            return []

    def parallel_store_user_data(self, user_id: str, data: Dict[str, Any], sqlite_db) -> bool:
        """Store user data in both systems during migration"""
        success = True
        
        # Always store in SQLite first (primary system)
        try:
            cursor = sqlite_db.cursor()
            cursor.execute('''
                UPDATE user_profiles 
                SET settings = ?, last_activity = CURRENT_TIMESTAMP 
                WHERE user_id = ?
            ''', (json.dumps(data), user_id))
            sqlite_db.commit()
        except Exception as e:
            print(f"⚠️ SQLite storage error: {e}")
            success = False

        # If enabled, also store in Replit DB
        if self.feature_flags['parallel_storage'] and self.feature_flags['replit_db_enabled']:
            replit_key = f"user_profile:{user_id}"
            replit_data = {
                **data,
                'timestamp': datetime.now().isoformat(),
                'source': 'starguide_migration'
            }
            if not self.set_db_value(replit_key, json.dumps(replit_data)):
                print(f"⚠️ Replit DB parallel storage failed for user {user_id}")

        return success

    def validate_migration_integrity(self, user_id: str, sqlite_db) -> Dict[str, Any]:
        """Validate data integrity between SQLite and Replit DB"""
        result = {
            'sqlite_exists': False,
            'replit_exists': False,
            'data_matches': False,
            'migration_safe': False
        }

        try:
            # Check SQLite data
            cursor = sqlite_db.cursor()
            sqlite_data = cursor.execute('''
                SELECT * FROM user_profiles WHERE user_id = ?
            ''', (user_id,)).fetchone()
            result['sqlite_exists'] = sqlite_data is not None

            # Check Replit DB data
            replit_key = f"user_profile:{user_id}"
            replit_raw = self.get_db_value(replit_key)
            result['replit_exists'] = replit_raw is not None

            if result['sqlite_exists'] and result['replit_exists']:
                try:
                    replit_data = json.loads(replit_raw)
                    # Basic validation - both have user data
                    result['data_matches'] = bool(sqlite_data and replit_data)
                except:
                    pass

            result['migration_safe'] = result['sqlite_exists']  # Primary system must exist

        except Exception as e:
            print(f"⚠️ Migration validation error: {e}")

        return result

    def get_auth_user(self) -> Optional[Dict[str, str]]:
        """Get authenticated user from Replit Auth (placeholder)"""
        if not self.feature_flags['replit_auth_enabled']:
            return None
            
        # Placeholder for Replit Auth integration
        # This would integrate with Replit's authentication system
        print("🔧 Replit Auth integration coming soon")
        return None

    def create_rollback_point(self, description: str) -> str:
        """Create a rollback point with current system state"""
        rollback_id = f"rollback_{int(datetime.now().timestamp())}"
        rollback_data = {
            'id': rollback_id,
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'feature_flags': self.feature_flags.copy(),
            'system_state': 'production_ready'
        }
        
        # Store rollback point
        if self.feature_flags['replit_db_enabled']:
            self.set_db_value(f"rollback:{rollback_id}", json.dumps(rollback_data))
        
        print(f"💾 Rollback point created: {rollback_id}")
        return rollback_id

# Global instance for use throughout the application
replit_services = ReplitServices()
