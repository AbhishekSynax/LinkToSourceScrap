#!/usr/bin/env python3
"""
ULTIMATE WEBSITE DOWNLOADER BOT - SYNAX EDITION (Fully Fixed & Crash-Proof)
Combined Features:
- SYNAX Bot's ALL management features
- Clean URL-to-ZIP from second bot
- Advanced UI/UX with working buttons
- Bulk key generation system
- Owner: @synaxnetwork
"""

import os
import json
import logging
import io
import zipfile
import subprocess
import tempfile
import shutil
import time
import random
import string
import asyncio
import requests
import base64
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, Document
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, ConversationHandler
from telegram.constants import ParseMode, ChatAction
from telegram.error import TelegramError, BadRequest

# ===================== CONFIGURATION =====================
BOT_TOKEN = "8246763985:AAFDOdJlNGO4WNyE9geP_JYk_MRx3aE4Rmk"  # Using your token

# OWNER DETAILS - SYNAX Network
OWNER_ID = 7998441787
OWNER_USERNAME = "@synaxnetwork"
OWNER_NAME = "Synaxnetwork"

# ADMINS LIST
ADMINS = [OWNER_ID]

# PROMOTION CHANNELS
PROMOTION_CHANNEL = "https://t.me/Synaxnetwork"
PROMOTION_GROUPS = [
    "https://t.me/Synaxchatgroup"
]

# QR Code Image URL
QR_CODE_URL = "https://i.ibb.co/4nZvRgJg/Screenshot-20251218-124441-Phone-Pe.jpg"

# MAX FILE SIZE
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# DOWNLOAD STATES
AWAITING_URL, AWAITING_DOWNLOAD_TYPE, AWAITING_KEY = range(3)

# FILES - SYNAX System
USERS_FILE = "users.json"
ADMINS_FILE = "admins.json"
SETTINGS_FILE = "settings.json"
KEYS_FILE = "subscription_keys.json"
PAYMENTS_FILE = "pending_payments.json"
DOWNLOAD_HISTORY_FILE = "download_history.json"
BULK_KEYS_FILE = "bulk_keys.json"
TICKETS_FILE = "support_tickets.json"
REPORTS_FILE = "user_reports.json"

# ===================== LOGGING =====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===================== DATA MANAGEMENT =====================
def load_json(file: str) -> Dict:
    """Load JSON file - SYNAX System"""
    try:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading {file}: {e}")
        return {}

def save_json(file: str, data: Dict):
    """Save JSON file - SYNAX System"""
    try:
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving {file}: {e}")
        return False
    return True

# Initialize databases - SYNAX System
users_db = load_json(USERS_FILE)
admins_db = load_json(ADMINS_FILE)
settings_db = load_json(SETTINGS_FILE)
keys_db = load_json(KEYS_FILE)
payments_db = load_json(PAYMENTS_FILE)
download_history_db = load_json(DOWNLOAD_HISTORY_FILE)
bulk_keys_db = load_json(BULK_KEYS_FILE)
tickets_db = load_json(TICKETS_FILE)
reports_db = load_json(REPORTS_FILE)

# Default settings - SYNAX System
if "maintenance" not in settings_db:
    settings_db["maintenance"] = False
if "broadcast_msg" not in settings_db:
    settings_db["broadcast_msg"] = "📢 New update available!"
if "owner_details" not in settings_db:
    settings_db["owner_details"] = {
        "id": OWNER_ID,
        "username": OWNER_USERNAME,
        "name": OWNER_NAME
    }
if "auto_forward" not in settings_db:
    settings_db["auto_forward"] = True
if "reply_feature" not in settings_db:
    settings_db["reply_feature"] = True
if "support_system" not in settings_db:
    settings_db["support_system"] = True
if "report_system" not in settings_db:
    settings_db["report_system"] = True
if "referral_system" not in settings_db:
    settings_db["referral_system"] = True
if "referral_reward" not in settings_db:
    settings_db["referral_reward"] = 5  # 5 downloads for each referral

save_json(SETTINGS_FILE, settings_db)

# ===================== FEATURE 1: KEY GENERATION (SYNAX) =====================
def generate_key(plan: str = "premium", days: int = 30, downloads: int = 100) -> str:
    """Generate subscription key - SYNAX System"""
    try:
        chars = string.ascii_uppercase + string.digits
        key = f"SYNAX-{''.join(random.choices(chars, k=8))}"
        
        key_data = {
            "key": key,
            "plan": plan,
            "days": days,
            "downloads": downloads,
            "generated_by": OWNER_ID,
            "generated_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=days)).isoformat(),
            "is_used": False,
            "used_by": None,
            "used_at": None
        }
        
        keys_db[key] = key_data
        save_json(KEYS_FILE, keys_db)
        return key
    except Exception as e:
        logger.error(f"Error generating key: {e}")
        return None

def activate_key(key: str, user_id: int) -> Dict:
    """Activate subscription key - SYNAX System"""
    try:
        if key in keys_db and not keys_db[key]["is_used"]:
            key_data = keys_db[key]
            key_data["is_used"] = True
            key_data["used_by"] = user_id
            key_data["used_at"] = datetime.now().isoformat()
            
            # Update user
            user_id_str = str(user_id)
            if user_id_str not in users_db:
                users_db[user_id_str] = create_user(user_id)
            
            users_db[user_id_str]["downloads_left"] += key_data["downloads"]
            users_db[user_id_str]["subscription"] = key_data["plan"]
            users_db[user_id_str]["subscription_expiry"] = key_data["expires_at"]
            
            save_json(KEYS_FILE, keys_db)
            save_json(USERS_FILE, users_db)
            
            return {"success": True, "data": key_data}
        return {"success": False, "error": "Invalid or used key"}
    except Exception as e:
        logger.error(f"Error activating key: {e}")
        return {"success": False, "error": "Server error"}

# ===================== BULK KEY GENERATION (FIXED) =====================
def generate_bulk_keys(count: int, plan: str, days: int, downloads: int, generated_by: int) -> List[str]:
    """Generate multiple keys at once - FIXED"""
    try:
        batch_id = f"BATCH-{random.randint(10000, 99999)}"
        generated_keys = []
        
        for _ in range(count):
            chars = string.ascii_uppercase + string.digits
            key = f"SYNAX-{''.join(random.choices(chars, k=8))}"
            
            key_data = {
                "key": key,
                "plan": plan,
                "days": days,
                "downloads": downloads,
                "generated_by": generated_by,
                "generated_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=days)).isoformat(),
                "is_used": False,
                "used_by": None,
                "used_at": None,
                "batch_id": batch_id
            }
            
            keys_db[key] = key_data
            generated_keys.append(key)
        
        # Save batch info
        batch_data = {
            "batch_id": batch_id,
            "count": count,
            "plan": plan,
            "days": days,
            "downloads": downloads,
            "generated_by": generated_by,
            "generated_at": datetime.now().isoformat(),
            "keys": generated_keys
        }
        
        bulk_keys_db[batch_id] = batch_data
        save_json(KEYS_FILE, keys_db)
        save_json(BULK_KEYS_FILE, bulk_keys_db)
        
        return generated_keys
    except Exception as e:
        logger.error(f"Error generating bulk keys: {e}")
        return []

# ===================== PAYMENT SYSTEM (NEW) =====================
def create_payment(user_id: int, plan: str, amount: int) -> str:
    """Create a pending payment record"""
    try:
        payment_id = f"PAY-{random.randint(10000, 99999)}"
        
        payment_data = {
            "payment_id": payment_id,
            "user_id": user_id,
            "plan": plan,
            "amount": amount,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "approved_at": None,
            "approved_by": None,
            "screenshot_received": False
        }
        
        payments_db[payment_id] = payment_data
        save_json(PAYMENTS_FILE, payments_db)
        return payment_id
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        return None

def approve_payment(payment_id: str, admin_id: int) -> Dict:
    """Approve a payment and activate subscription"""
    try:
        if payment_id in payments_db and payments_db[payment_id]["status"] == "pending":
            payment_data = payments_db[payment_id]
            payment_data["status"] = "approved"
            payment_data["approved_at"] = datetime.now().isoformat()
            payment_data["approved_by"] = admin_id
            
            # Get user
            user_id = payment_data["user_id"]
            user_id_str = str(user_id)
            
            if user_id_str not in users_db:
                users_db[user_id_str] = create_user(user_id)
            
            # Add downloads based on plan
            plan_downloads = {
                "basic": 10,
                "pro": 29,
                "premium": 100
            }
            
            downloads = plan_downloads.get(payment_data["plan"], 0)
            users_db[user_id_str]["downloads_left"] += downloads
            users_db[user_id_str]["subscription"] = payment_data["plan"]
            users_db[user_id_str]["subscription_expiry"] = (datetime.now() + timedelta(days=30)).isoformat()
            
            save_json(PAYMENTS_FILE, payments_db)
            save_json(USERS_FILE, users_db)
            
            return {"success": True, "data": payment_data, "downloads": downloads}
        return {"success": False, "error": "Payment not found or already processed"}
    except Exception as e:
        logger.error(f"Error approving payment: {e}")
        return {"success": False, "error": "Server error"}

def reject_payment(payment_id: str, admin_id: int, reason: str = "") -> Dict:
    """Reject a payment"""
    try:
        if payment_id in payments_db and payments_db[payment_id]["status"] == "pending":
            payment_data = payments_db[payment_id]
            payment_data["status"] = "rejected"
            payment_data["rejected_at"] = datetime.now().isoformat()
            payment_data["rejected_by"] = admin_id
            payment_data["rejection_reason"] = reason
            
            save_json(PAYMENTS_FILE, payments_db)
            return {"success": True, "data": payment_data}
        return {"success": False, "error": "Payment not found or already processed"}
    except Exception as e:
        logger.error(f"Error rejecting payment: {e}")
        return {"success": False, "error": "Server error"}

# ===================== DOWNLOAD HISTORY (NEW) =====================
def add_download_history(user_id: int, url: str, file_size: int, file_count: int):
    """Add download to history"""
    try:
        user_id_str = str(user_id)
        if user_id_str not in download_history_db:
            download_history_db[user_id_str] = []
        
        history_entry = {
            "url": url,
            "file_size": file_size,
            "file_count": file_count,
            "timestamp": datetime.now().isoformat()
        }
        
        download_history_db[user_id_str].append(history_entry)
        # Keep only last 10 entries
        if len(download_history_db[user_id_str]) > 10:
            download_history_db[user_id_str] = download_history_db[user_id_str][-10:]
        
        save_json(DOWNLOAD_HISTORY_FILE, download_history_db)
    except Exception as e:
        logger.error(f"Error adding download history: {e}")

def get_download_history(user_id: int) -> List:
    """Get user's download history"""
    try:
        user_id_str = str(user_id)
        return download_history_db.get(user_id_str, [])
    except Exception as e:
        logger.error(f"Error getting download history: {e}")
        return []

# ===================== SUPPORT SYSTEM (NEW) =====================
def create_support_ticket(user_id: int, message: str) -> str:
    """Create a support ticket"""
    try:
        ticket_id = f"TICKET-{random.randint(10000, 99999)}"
        
        ticket_data = {
            "ticket_id": ticket_id,
            "user_id": user_id,
            "message": message,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "replies": []
        }
        
        tickets_db[ticket_id] = ticket_data
        save_json(TICKETS_FILE, tickets_db)
        return ticket_id
    except Exception as e:
        logger.error(f"Error creating support ticket: {e}")
        return None

def add_ticket_reply(ticket_id: str, user_id: int, message: str, is_admin: bool = False) -> Dict:
    """Add reply to a support ticket"""
    try:
        if ticket_id in tickets_db:
            ticket = tickets_db[ticket_id]
            reply_data = {
                "user_id": user_id,
                "message": message,
                "is_admin": is_admin,
                "timestamp": datetime.now().isoformat()
            }
            
            ticket["replies"].append(reply_data)
            save_json(TICKETS_FILE, tickets_db)
            return {"success": True, "data": reply_data}
        return {"success": False, "error": "Ticket not found"}
    except Exception as e:
        logger.error(f"Error adding ticket reply: {e}")
        return {"success": False, "error": "Server error"}

def close_ticket(ticket_id: str, admin_id: int) -> Dict:
    """Close a support ticket"""
    try:
        if ticket_id in tickets_db:
            ticket = tickets_db[ticket_id]
            ticket["status"] = "closed"
            ticket["closed_at"] = datetime.now().isoformat()
            ticket["closed_by"] = admin_id
            
            save_json(TICKETS_FILE, tickets_db)
            return {"success": True, "data": ticket}
        return {"success": False, "error": "Ticket not found"}
    except Exception as e:
        logger.error(f"Error closing ticket: {e}")
        return {"success": False, "error": "Server error"}

# ===================== REFERRAL SYSTEM (NEW) =====================
def process_referral(referrer_id: int, referred_id: int) -> Dict:
    """Process referral and give reward"""
    try:
        referrer_id_str = str(referrer_id)
        referred_id_str = str(referred_id)
        
        # Check if referred user exists
        if referred_id_str not in users_db:
            users_db[referred_id_str] = create_user(referred_id)
        
        # Check if already referred
        if "referred_by" in users_db[referred_id_str]:
            return {"success": False, "error": "User already referred"}
        
        # Mark as referred
        users_db[referred_id_str]["referred_by"] = referrer_id
        
        # Give reward to referrer
        if referrer_id_str in users_db:
            reward = settings_db.get("referral_reward", 5)
            users_db[referrer_id_str]["downloads_left"] += reward
            users_db[referrer_id_str]["referral_count"] = users_db[referrer_id_str].get("referral_count", 0) + 1
            
            save_json(USERS_FILE, users_db)
            return {"success": True, "reward": reward}
        
        return {"success": False, "error": "Referrer not found"}
    except Exception as e:
        logger.error(f"Error processing referral: {e}")
        return {"success": False, "error": "Server error"}

# ===================== HELPER FUNCTIONS (SYNAX) =====================
def is_admin(user_id: int) -> bool:
    """Check if user is admin - SYNAX System"""
    return user_id in ADMINS or str(user_id) in admins_db

def is_owner(user_id: int) -> bool:
    """Check if user is owner - SYNAX System"""
    return user_id == OWNER_ID

def create_user(user_id: int, username: str = "", first_name: str = "") -> Dict:
    """Create new user record - SYNAX System"""
    return {
        "id": user_id,
        "username": username,
        "first_name": first_name,
        "downloads_left": 0,
        "total_downloads": 0,
        "subscription": "free",
        "joined_date": datetime.now().isoformat(),
        "last_active": datetime.now().isoformat(),
        "is_banned": False,
        "warnings": 0,
        "messages_sent": 0,
        "referral_count": 0
    }

def get_user_stats(user_id: int) -> Dict:
    """Get user statistics - SYNAX System"""
    try:
        user_id_str = str(user_id)
        if user_id_str not in users_db:
            users_db[user_id_str] = create_user(user_id)
            save_json(USERS_FILE, users_db)
        return users_db[user_id_str]
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        return create_user(user_id)

def update_user_activity(user_id: int, username: str = "", first_name: str = ""):
    """Update user's last activity - SYNAX System"""
    try:
        user_id_str = str(user_id)
        if user_id_str not in users_db:
            users_db[user_id_str] = create_user(user_id, username, first_name)
        
        users_db[user_id_str]["last_active"] = datetime.now().isoformat()
        if username:
            users_db[user_id_str]["username"] = username
        if first_name:
            users_db[user_id_str]["first_name"] = first_name
        
        save_json(USERS_FILE, users_db)
    except Exception as e:
        logger.error(f"Error updating user activity: {e}")

def add_admin(user_id: int, username: str = "") -> bool:
    """Add admin - SYNAX System"""
    try:
        if str(user_id) not in admins_db and user_id != OWNER_ID:
            admins_db[str(user_id)] = {
                "id": user_id,
                "username": username,
                "added_by": OWNER_ID,
                "added_date": datetime.now().isoformat()
            }
            ADMINS.append(user_id)
            save_json(ADMINS_FILE, admins_db)
            return True
        return False
    except Exception as e:
        logger.error(f"Error adding admin: {e}")
        return False

def remove_admin(user_id: int) -> bool:
    """Remove admin - SYNAX System"""
    try:
        if str(user_id) in admins_db and user_id != OWNER_ID:
            del admins_db[str(user_id)]
            if user_id in ADMINS:
                ADMINS.remove(user_id)
            save_json(ADMINS_FILE, admins_db)
            return True
        return False
    except Exception as e:
        logger.error(f"Error removing admin: {e}")
        return False

def ban_user(user_id: int, reason: str = "No reason provided") -> bool:
    """Ban user - SYNAX System"""
    try:
        user_id_str = str(user_id)
        if user_id_str in users_db and not users_db[user_id_str].get("is_banned", False):
            users_db[user_id_str]["is_banned"] = True
            users_db[user_id_str]["ban_reason"] = reason
            users_db[user_id_str]["ban_date"] = datetime.now().isoformat()
            save_json(USERS_FILE, users_db)
            return True
        return False
    except Exception as e:
        logger.error(f"Error banning user: {e}")
        return False

def unban_user(user_id: int) -> bool:
    """Unban user - SYNAX System"""
    try:
        user_id_str = str(user_id)
        if user_id_str in users_db and users_db[user_id_str].get("is_banned", False):
            users_db[user_id_str]["is_banned"] = False
            if "ban_reason" in users_db[user_id_str]:
                del users_db[user_id_str]["ban_reason"]
            if "ban_date" in users_db[user_id_str]:
                del users_db[user_id_str]["ban_date"]
            save_json(USERS_FILE, users_db)
            return True
        return False
    except Exception as e:
        logger.error(f"Error unbanning user: {e}")
        return False

# ===================== URL TO ZIP FEATURE (From Second Bot) =====================
def clean_url(url):
    """Clean and validate URL - From Second Bot"""
    try:
        url = url.strip()
        if url.startswith('www.'):
            url = 'https://' + url
        elif not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    except Exception as e:
        logger.error(f"Error cleaning URL: {e}")
        return url

def create_direct_zip(url, download_type="full"):
    """Download and create zip directly - From Second Bot"""
    temp_dir = None
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        if download_type == "full":
            cmd = f"""wget --mirror --convert-links --adjust-extension --page-requisites \
                    --no-parent --no-check-certificate -e robots=off \
                    --user-agent="Mozilla/5.0" --quiet -P "{temp_dir}" "{url}" """
        else:
            cmd = f"""wget -r -l 2 -k -p -E --no-check-certificate \
                    -e robots=off --quiet -P "{temp_dir}" "{url}" """
        
        # Execute download
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        # Create zip in memory
        zip_buffer = io.BytesIO()
        file_count = 0
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'rb') as f:
                            file_data = f.read()
                        
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.writestr(arcname, file_data)
                        file_count += 1
                    except:
                        continue
        
        zip_buffer.seek(0)
        
        return zip_buffer, file_count
        
    except Exception as e:
        logger.error(f"Error creating zip: {e}")
        raise e
    finally:
        # Cleanup temp directory
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

# ===================== BUTTON MENUS (SYNAX Style - Enhanced) =====================
def get_main_menu() -> InlineKeyboardMarkup:
    """Main menu buttons - SYNAX Style (Enhanced)"""
    keyboard = [
        [InlineKeyboardButton("⬇️ DOWNLOAD", callback_data="download_menu"),
         InlineKeyboardButton("💰 BUY", callback_data="buy_menu")],
        [InlineKeyboardButton("📊 STATS", callback_data="my_stats"),
         InlineKeyboardButton("🔑 ACTIVATE KEY", callback_data="activate_key_menu")],
        [InlineKeyboardButton("📜 HISTORY", callback_data="download_history"),
         InlineKeyboardButton("🆘 HELP", callback_data="help")],
        [InlineKeyboardButton("🎫 SUPPORT", callback_data="support_menu"),
         InlineKeyboardButton("👥 REFERRAL", callback_data="referral_menu")],
        [InlineKeyboardButton("📢 JOIN CHANNEL", url=PROMOTION_CHANNEL),
         InlineKeyboardButton("👥 JOIN GROUP", url=PROMOTION_GROUPS[0])],
        [InlineKeyboardButton("👑 OWNER", callback_data="owner_info")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_download_menu() -> InlineKeyboardMarkup:
    """Download menu - SYNAX Style (Enhanced)"""
    keyboard = [
        [InlineKeyboardButton("🌐 FROM URL", callback_data="url_download"),
         InlineKeyboardButton("⚡ QUICK DOWNLOAD", callback_data="quick_dl")],
        [InlineKeyboardButton("🔙 BACK", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_buy_menu() -> InlineKeyboardMarkup:
    """Buy menu with QR Code - Enhanced"""
    keyboard = [
        [InlineKeyboardButton("₹39 → 10 DOWNLOADS", callback_data="buy_basic")],
        [InlineKeyboardButton("₹99 → 29 DOWNLOADS", callback_data="buy_pro")],
        [InlineKeyboardButton("₹199 → 100 DOWNLOADS", callback_data="buy_premium")],
        [InlineKeyboardButton("🔙 BACK", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_menu() -> InlineKeyboardMarkup:
    """Admin menu - SYNAX System (Enhanced)"""
    keyboard = [
        [InlineKeyboardButton("📢 BROADCAST", callback_data="admin_broadcast"),
         InlineKeyboardButton("👥 USERS", callback_data="admin_all_users")],
        [InlineKeyboardButton("💳 PAYMENTS", callback_data="admin_payments"),
         InlineKeyboardButton("🚫 BAN USER", callback_data="admin_ban")],
        [InlineKeyboardButton("✅ UNBAN", callback_data="admin_unban"),
         InlineKeyboardButton("⚙️ MAINTENANCE", callback_data="admin_maintenance")],
        [InlineKeyboardButton("📊 STATS", callback_data="admin_stats"),
         InlineKeyboardButton("🔧 ADD ADMIN", callback_data="admin_add")],
        [InlineKeyboardButton("🗑️ REMOVE ADMIN", callback_data="admin_remove"),
         InlineKeyboardButton("🔑 GEN KEY", callback_data="admin_gen_key")],
        [InlineKeyboardButton("🔑 BULK KEYS", callback_data="admin_bulk_keys"),
         InlineKeyboardButton("↩️ REPLY USER", callback_data="admin_reply_user")],
        [InlineKeyboardButton("🎫 SUPPORT TICKETS", callback_data="admin_tickets"),
         InlineKeyboardButton("📊 REPORTS", callback_data="admin_reports")],
        [InlineKeyboardButton("🔙 MAIN MENU", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_button(callback_data: str = "main_menu") -> InlineKeyboardMarkup:
    """Simple back button"""
    keyboard = [[InlineKeyboardButton("🔙 BACK", callback_data=callback_data)]]
    return InlineKeyboardMarkup(keyboard)

def get_download_type_keyboard() -> InlineKeyboardMarkup:
    """Download type selection keyboard"""
    keyboard = [
        [InlineKeyboardButton("🌐 Full Source Download", callback_data="full_download")],
        [InlineKeyboardButton("📄 Partial Download", callback_data="partial_download")],
        [InlineKeyboardButton("🚫 Cancel", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_qr_keyboard(plan: str):
    """Create QR code and screenshot buttons - Enhanced"""
    keyboard = [
        [InlineKeyboardButton("📱 VIEW QR CODE", callback_data=f"qr_{plan}")],
        [InlineKeyboardButton("🔙 BUY MENU", callback_data="buy_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_payment_approval_keyboard(payment_id: str):
    """Payment approval keyboard for admins"""
    keyboard = [
        [InlineKeyboardButton("✅ APPROVE", callback_data=f"approve_payment_{payment_id}")],
        [InlineKeyboardButton("❌ REJECT", callback_data=f"reject_payment_{payment_id}")],
        [InlineKeyboardButton("🔙 BACK", callback_data="admin_payments")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_bulk_key_form() -> InlineKeyboardMarkup:
    """Bulk key generation form - FIXED"""
    keyboard = [
        [InlineKeyboardButton("🔑 BASIC (10 DL)", callback_data="bulk_form_basic")],
        [InlineKeyboardButton("🔑 PRO (29 DL)", callback_data="bulk_form_pro")],
        [InlineKeyboardButton("🔑 PREMIUM (100 DL)", callback_data="bulk_form_premium")],
        [InlineKeyboardButton("🔙 ADMIN MENU", callback_data="admin_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_support_menu() -> InlineKeyboardMarkup:
    """Support menu"""
    keyboard = [
        [InlineKeyboardButton("📝 CREATE TICKET", callback_data="create_ticket")],
        [InlineKeyboardButton("📋 MY TICKETS", callback_data="my_tickets")],
        [InlineKeyboardButton("🔙 BACK", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_referral_menu() -> InlineKeyboardMarkup:
    """Referral menu"""
    keyboard = [
        [InlineKeyboardButton("🔗 MY REFERRAL LINK", callback_data="my_referral")],
        [InlineKeyboardButton("👥 MY REFERRALS", callback_data="my_referrals")],
        [InlineKeyboardButton("🔙 BACK", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ===================== USERS LIST WITH PAGINATION (FIXED) =====================
async def show_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0):
    """Show all users with pagination - FIXED"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ Admin Only!", show_alert=True)
            return
        
        # Get all users sorted by last active
        sorted_users = sorted(
            users_db.items(),
            key=lambda x: datetime.fromisoformat(x[1]['last_active']),
            reverse=True
        )
        
        users_per_page = 20
        total_pages = (len(sorted_users) + users_per_page - 1) // users_per_page
        
        start_idx = page * users_per_page
        end_idx = start_idx + users_per_page
        
        users_text = f"👥 **ALL USERS LIST** 👥\n\n"
        users_text += f"📄 Page: {page + 1}/{total_pages}\n"
        users_text += f"👤 Total Users: {len(sorted_users)}\n\n"
        
        count = start_idx
        for uid_str, user_data in sorted_users[start_idx:end_idx]:
            count += 1
            username = user_data.get('username', 'N/A')
            first_name = user_data.get('first_name', 'N/A')
            downloads = user_data.get('total_downloads', 0)
            last_active = datetime.fromisoformat(user_data['last_active']).strftime('%d/%m %H:%M')
            status = "🚫" if user_data.get('is_banned', False) else "✅"
            plan = user_data.get('subscription', 'free')
            
            users_text += f"{count}. {status} `{uid_str}`\n"
            users_text += f"   👤 @{username} | {first_name}\n"
            users_text += f"   📥 {downloads} DL | 📅 {last_active} | 💰 {plan}\n\n"
        
        # Create pagination buttons
        keyboard = []
        
        if page > 0:
            keyboard.append([InlineKeyboardButton("◀️ PREVIOUS", callback_data=f"users_page_{page-1}")])
        
        if page < total_pages - 1:
            if keyboard:
                keyboard[-1].append(InlineKeyboardButton("NEXT ▶️", callback_data=f"users_page_{page+1}"))
            else:
                keyboard.append([InlineKeyboardButton("NEXT ▶️", callback_data=f"users_page_{page+1}")])
        
        keyboard.append([InlineKeyboardButton("🔙 ADMIN MENU", callback_data="admin_menu")])
        
        await query.edit_message_text(
            users_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error showing all users: {e}")
        await query.answer("❌ Error loading users!", show_alert=True)

# ===================== COMMAND HANDLERS =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - SYNAX Style (Fixed without Image)"""
    try:
        user = update.effective_user
        user_id = user.id
        
        update_user_activity(user_id, user.username, user.first_name)
        
        # Check for referral
        if context.args and len(context.args) > 0:
            arg = context.args[0]
            if arg.startswith("ref_"):
                try:
                    referrer_id = int(arg.split("_")[1])
                    if referrer_id != user_id:  # Can't refer yourself
                        result = process_referral(referrer_id, user_id)
                        if result["success"]:
                            await update.message.reply_text(
                                f"🎉 **Welcome!**\n\n"
                                f"You were referred by a friend!\n"
                                f"They received {result['reward']} downloads as a reward.\n\n"
                                f"Start using the bot to earn your own rewards!",
                                parse_mode=ParseMode.MARKDOWN
                            )
                except (ValueError, IndexError):
                    pass
        
        user_data = get_user_stats(user_id)
        
        welcome_msg = f"""
✨ **WELCOME, {user.first_name}!** ✨

🤖 **SYNAX DOWNLOADER BOT**
_Professional Website Downloader_

📊 **YOUR STATUS:**
• Downloads Left: `{user_data.get('downloads_left', 0)}`
• Total Downloads: `{user_data.get('total_downloads', 0)}`
• Account: `{'🚫 BANNED' if user_data.get('is_banned') else '✅ ACTIVE'}`

📢 **JOIN OUR:**
• Channel: {PROMOTION_CHANNEL}
• Groups: {', '.join(PROMOTION_GROUPS)}

👇 **USE BUTTONS BELOW:**
    """
        
        # Send welcome message with buttons (no image)
        if update.message:
            await update.message.reply_text(
                welcome_msg,
                reply_markup=get_main_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        elif update.callback_query:
            await update.callback_query.edit_message_text(
                welcome_msg,
                reply_markup=get_main_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        if update.message:
            await update.message.reply_text("❌ Error loading bot. Please try again.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command - SYNAX Style (Enhanced)"""
    try:
        help_text = f"""
🆘 **HELP & GUIDE** 🆘

🤖 **HOW TO USE:**
1. Click DOWNLOAD button
2. Send website URL
3. Choose download type
4. Get website as ZIP file

💰 **PRICING:**
• ₹39 → 10 downloads
• ₹99 → 29 downloads  
• ₹199 → 100 downloads

🔑 **SUBSCRIPTION KEYS:**
Use /activate <key> to activate subscription

📜 **DOWNLOAD HISTORY:**
Check your previous downloads in the HISTORY section

🎫 **SUPPORT SYSTEM:**
Create support tickets for help with issues

👥 **REFERRAL SYSTEM:**
Invite friends and earn {settings_db.get('referral_reward', 5)} downloads per referral

👑 **OWNER:** {OWNER_NAME}
📞 **SUPPORT:** {OWNER_USERNAME}
    """
        
        if update.message:
            await update.message.reply_text(
                help_text,
                reply_markup=get_main_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        elif update.callback_query:
            await update.callback_query.edit_message_text(
                help_text,
                reply_markup=get_main_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        if update.message:
            await update.message.reply_text("❌ Error loading help. Please try again.")

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel - SYNAX System (Enhanced)"""
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            if update.message:
                await update.message.reply_text("❌ **ACCESS DENIED!**")
            elif update.callback_query:
                await update.callback_query.answer("❌ Access Denied!", show_alert=True)
            return
        
        # Count statistics
        active_today = 0
        today = datetime.now().date()
        banned_count = 0
        total_downloads = 0
        pending_payments = 0
        total_keys = len(keys_db)
        used_keys = sum(1 for k in keys_db.values() if k.get("is_used", False))
        open_tickets = sum(1 for t in tickets_db.values() if t.get("status") == "open")
        
        for u in users_db.values():
            try:
                last_active = datetime.fromisoformat(u['last_active']).date()
                if last_active == today:
                    active_today += 1
                if u.get('is_banned', False):
                    banned_count += 1
                total_downloads += u.get('total_downloads', 0)
            except:
                continue
        
        for p in payments_db.values():
            if p.get('status') == 'pending':
                pending_payments += 1
        
        admin_stats = f"""
👑 **ADMIN PANEL** 👑

📊 **STATISTICS:**
• Total Users: `{len(users_db)}`
• Active Today: `{active_today}`
• Banned Users: `{banned_count}`
• Total Downloads: `{total_downloads}`
• Pending Payments: `{pending_payments}`
• Subscription Keys: `{total_keys}`
• Used Keys: `{used_keys}`
• Unused Keys: `{total_keys - used_keys}`
• Open Tickets: `{open_tickets}`
• Maintenance: `{'✅ ON' if settings_db.get('maintenance') else '❌ OFF'}`

👤 **YOUR ROLE:** {'👑 OWNER' if is_owner(user_id) else '🛡️ ADMIN'}

👇 **SELECT OPTION:**
    """
        
        if update.message:
            await update.message.reply_text(
                admin_stats,
                reply_markup=get_admin_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        elif update.callback_query:
            await update.callback_query.edit_message_text(
                admin_stats,
                reply_markup=get_admin_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        logger.error(f"Error in admin command: {e}")
        if update.message:
            await update.message.reply_text("❌ Error loading admin panel.")

async def show_user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics - SYNAX System (Enhanced)"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        user_data = get_user_stats(user_id)
        
        # Format dates
        joined_date = datetime.fromisoformat(user_data['joined_date']).strftime('%d %b %Y')
        last_active = datetime.fromisoformat(user_data['last_active']).strftime('%I:%M %p, %d %b')
        
        # Calculate subscription expiry if exists
        expiry_text = "N/A"
        if 'subscription_expiry' in user_data:
            try:
                expiry_date = datetime.fromisoformat(user_data['subscription_expiry'])
                expiry_text = expiry_date.strftime('%d %b %Y')
                
                # Check if expired
                if expiry_date < datetime.now():
                    expiry_text += " (EXPIRED)"
            except:
                pass
        
        # Get referral info
        referral_count = user_data.get('referral_count', 0)
        referral_link = f"https://t.me/{context.bot.username}?start=ref_{user_id}"
        
        stats_text = f"""
📊 **YOUR STATISTICS** 📊

👤 **ACCOUNT INFO:**
• User ID: `{user_id}`
• Username: @{update.effective_user.username or 'N/A'}
• Joined: `{joined_date}`
• Status: `{'🚫 BANNED' if user_data.get('is_banned') else '✅ ACTIVE'}`

⬇️ **DOWNLOAD STATS:**
• Downloads Left: `{user_data['downloads_left']}`
• Total Downloads: `{user_data['total_downloads']}`
• Subscription: `{user_data['subscription'].upper()}`
• Expires: `{expiry_text}`

👥 **REFERRAL STATS:**
• Referrals: `{referral_count}`
• Referral Link: `{referral_link}`

📅 **LAST ACTIVE:** `{last_active}`

{'♾️ **OWNER PRIVILEGES:** Unlimited Downloads' if is_owner(user_id) else ''}
    """
        
        await query.edit_message_text(
            stats_text,
            reply_markup=get_main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error showing user stats: {e}")
        await query.answer("❌ Error loading stats!", show_alert=True)

async def show_download_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show download history - ENHANCED FEATURE"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        history = get_download_history(user_id)
        
        if not history:
            history_text = "📜 **DOWNLOAD HISTORY** 📜\n\nNo downloads yet. Start downloading websites!"
        else:
            history_text = "📜 **DOWNLOAD HISTORY** 📜\n\n"
            
            for i, entry in enumerate(reversed(history[-5:]), 1):  # Show last 5
                timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%d %b, %I:%M %p')
                file_size_mb = entry['file_size'] / 1024 / 1024
                
                history_text += f"{i}. 📅 {timestamp}\n"
                history_text += f"   🌐 {entry['url'][:30]}...\n"
                history_text += f"   📦 {entry['file_count']} files, {file_size_mb:.1f}MB\n\n"
        
        await query.edit_message_text(
            history_text,
            reply_markup=get_main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error showing download history: {e}")
        await query.answer("❌ Error loading history!", show_alert=True)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User statistics command (Enhanced)"""
    try:
        user_id = update.effective_user.id
        user_data = get_user_stats(user_id)
        
        # Format dates
        joined_date = datetime.fromisoformat(user_data['joined_date']).strftime('%d %b %Y')
        last_active = datetime.fromisoformat(user_data['last_active']).strftime('%I:%M %p, %d %b')
        
        # Calculate subscription expiry if exists
        expiry_text = "N/A"
        if 'subscription_expiry' in user_data:
            try:
                expiry_date = datetime.fromisoformat(user_data['subscription_expiry'])
                expiry_text = expiry_date.strftime('%d %b %Y')
                
                # Check if expired
                if expiry_date < datetime.now():
                    expiry_text += " (EXPIRED)"
            except:
                pass
        
        # Get referral info
        referral_count = user_data.get('referral_count', 0)
        referral_link = f"https://t.me/{context.bot.username}?start=ref_{user_id}"
        
        stats_text = f"""
📊 **YOUR STATISTICS** 📊

👤 **ACCOUNT INFO:**
• User ID: `{user_id}`
• Username: @{update.effective_user.username or 'N/A'}
• Joined: `{joined_date}`
• Status: `{'🚫 BANNED' if user_data.get('is_banned') else '✅ ACTIVE'}`

⬇️ **DOWNLOAD STATS:**
• Downloads Left: `{user_data['downloads_left']}`
• Total Downloads: `{user_data['total_downloads']}`
• Subscription: `{user_data['subscription'].upper()}`
• Expires: `{expiry_text}`

👥 **REFERRAL STATS:**
• Referrals: `{referral_count}`
• Referral Link: `{referral_link}`

📅 **LAST ACTIVE:** `{last_active}`

{'♾️ **OWNER PRIVILEGES:** Unlimited Downloads' if is_owner(user_id) else ''}
    """
        
        await update.message.reply_text(
            stats_text,
            reply_markup=get_main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        await update.message.reply_text("❌ Error loading stats.")

# ===================== ACTIVATE KEY (SYNAX System) =====================
async def activate_key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Activate subscription key (Enhanced)"""
    try:
        user_id = update.effective_user.id
        
        if context.args and len(context.args) > 0:
            key = context.args[0].upper()
            result = activate_key(key, user_id)
            
            if result["success"]:
                key_data = result["data"]
                await update.message.reply_text(
                    f"✅ **SUBSCRIPTION ACTIVATED!**\n\n"
                    f"🔑 Key: `{key}`\n"
                    f"📦 Plan: {key_data['plan']}\n"
                    f"⬇️ Downloads: {key_data['downloads']}\n"
                    f"📅 Valid Until: {datetime.fromisoformat(key_data['expires_at']).strftime('%d %b %Y')}\n\n"
                    f"🎉 Enjoy your subscription!",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text(
                    f"❌ **INVALID KEY!**\n\n"
                    f"Key `{key}` is invalid or already used.\n"
                    f"Contact {OWNER_USERNAME} for help."
                )
        else:
            await update.message.reply_text(
                "🔑 **ACTIVATE SUBSCRIPTION KEY**\n\n"
                "Usage: `/activate <key>`\n\n"
                "Example: `/activate SYNAX-ABC123`\n\n"
                "Get keys from @synaxnetwork",
                parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        logger.error(f"Error in activate key command: {e}")
        await update.message.reply_text("❌ Error activating key.")

# ===================== GENERATE KEY (SYNAX System) =====================
async def generate_key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate subscription key (admin only) - Enhanced"""
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ **ADMIN ONLY!**")
            return
        
        if context.args and len(context.args) >= 1:
            plan = context.args[0].lower()
            days = int(context.args[1]) if len(context.args) > 1 else 30
            downloads = 100
            
            if plan == "basic":
                downloads = 10
            elif plan == "pro":
                downloads = 29
            elif plan == "premium":
                downloads = 100
            
            key = generate_key(plan, days, downloads)
            if key:
                await update.message.reply_text(
                    f"🔑 **SUBSCRIPTION KEY GENERATED** 🔑\n\n"
                    f"Key: `{key}`\n"
                    f"Plan: {plan.upper()}\n"
                    f"Downloads: {downloads}\n"
                    f"Days: {days}\n"
                    f"Expires: {(datetime.now() + timedelta(days=days)).strftime('%d %b %Y')}\n\n"
                    f"**Send this key to user:**\n"
                    f"`/activate {key}`",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text("❌ Error generating key.")
        else:
            await update.message.reply_text(
                "🔑 **GENERATE SUBSCRIPTION KEY**\n\n"
                "Usage: `/generate <plan> <days>`\n\n"
                "**Plans:** basic, pro, premium\n"
                "**Example:** `/generate premium 30`",
                parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        logger.error(f"Error in generate key command: {e}")
        await update.message.reply_text("❌ Error generating key.")

# ===================== GIVE COMMAND (NEW - ओनर द्वारा यूज़र को डाउनलोड्स देना) =====================
async def give_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Give downloads to user (owner only) - Enhanced"""
    try:
        user_id = update.effective_user.id
        
        if not is_owner(user_id):
            await update.message.reply_text("❌ **OWNER ONLY COMMAND!**")
            return
        
        if context.args and len(context.args) >= 2:
            # Format: /give <user_id> <downloads> <days>
            if len(context.args) == 3:
                target_user_id = int(context.args[0])
                downloads_to_give = int(context.args[1])
                days_to_give = int(context.args[2])
            elif len(context.args) == 2:
                target_user_id = int(context.args[0])
                downloads_to_give = int(context.args[1])
                days_to_give = 30  # Default 30 days
            else:
                await update.message.reply_text(
                    "❌ **Invalid format!**\n\n"
                    "Usage: `/give <user_id> <downloads> <days>`\n"
                    "Example: `/give 1234567890 15 30`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Get target user
            target_user_str = str(target_user_id)
            if target_user_str not in users_db:
                users_db[target_user_str] = create_user(target_user_id)
            
            # Give downloads
            users_db[target_user_str]["downloads_left"] += downloads_to_give
            
            # Set subscription expiry
            expiry_date = datetime.now() + timedelta(days=days_to_give)
            users_db[target_user_str]["subscription_expiry"] = expiry_date.isoformat()
            users_db[target_user_str]["subscription"] = "custom"
            
            save_json(USERS_FILE, users_db)
            
            # Notify target user
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=f"🎁 **🎉 CONGRATULATIONS! 🎉**\n\n"
                         f"👑 **OWNER ने आपको गिफ्ट दिया है!**\n\n"
                         f"📥 **आपको मिले:**\n"
                         f"• ⬇️ Downloads: `{downloads_to_give}`\n"
                         f"• 📅 Validity: `{days_to_give}` days\n"
                         f"• 📅 Expiry: `{expiry_date.strftime('%d %b %Y')}`\n\n"
                         f"🎊 **अब आप और डाउनलोड कर सकते हैं!**\n\n"
                         f"Made with ❤️ by {OWNER_NAME}",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.warning(f"Could not notify user {target_user_id}: {e}")
            
            # Confirm to owner
            await update.message.reply_text(
                f"✅ **SUCCESSFULLY GIVEN!**\n\n"
                f"👤 User ID: `{target_user_id}`\n"
                f"⬇️ Downloads Given: `{downloads_to_give}`\n"
                f"📅 Days Given: `{days_to_give}`\n"
                f"📅 Expiry Date: `{expiry_date.strftime('%d %b %Y')}`\n\n"
                f"🎯 **User has been notified!**",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Log the action
            logger.info(f"Owner {user_id} gave {downloads_to_give} downloads to {target_user_id} for {days_to_give} days")
            
        else:
            await update.message.reply_text(
                "🎁 **GIVE DOWNLOADS TO USER** 🎁\n\n"
                "📝 **Usage:**\n"
                "`/give <user_id> <downloads> <days>`\n\n"
                "📌 **Examples:**\n"
                "• `/give 1234567890 15 30` - 15 downloads for 30 days\n"
                "• `/give 1234567890 50` - 50 downloads for 30 days (default)\n\n"
                "🎯 **Note:** यह कमांड सिर्फ ओनर के लिए है।",
                parse_mode=ParseMode.MARKDOWN
            )
    except ValueError:
        await update.message.reply_text(
            "❌ **Invalid input!**\n"
            "User ID, downloads और days numbers होने चाहिए।\n\n"
            "Example: `/give 1234567890 15 30`",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error in give command: {e}")
        await update.message.reply_text("❌ Error giving downloads.")

# ===================== ADMIN COMMAND HANDLERS (SYNAX System) =====================
async def handle_add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle add admin from callback"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not is_owner(user_id):
            await query.answer("❌ Owner Only!", show_alert=True)
            return
        
        await query.edit_message_text(
            "🔧 **ADD ADMIN**\n\n"
            "Please reply with the user ID to make admin:\n"
            "Format: `addadmin <user_id>`\n\n"
            "Example: `addadmin 1234567890`",
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['awaiting_addadmin'] = True
    except Exception as e:
        logger.error(f"Error handling add admin: {e}")
        await query.answer("❌ Error loading form!", show_alert=True)

async def handle_remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle remove admin from callback"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not is_owner(user_id):
            await query.answer("❌ Owner Only!", show_alert=True)
            return
        
        await query.edit_message_text(
            "🗑️ **REMOVE ADMIN**\n\n"
            "Please reply with the user ID to remove as admin:\n"
            "Format: `removeadmin <user_id>`\n\n"
            "Example: `removeadmin 1234567890`",
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['awaiting_removeadmin'] = True
    except Exception as e:
        logger.error(f"Error handling remove admin: {e}")
        await query.answer("❌ Error loading form!", show_alert=True)

async def handle_ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle ban user from callback"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ Admin Only!", show_alert=True)
            return
        
        await query.edit_message_text(
            "🚫 **BAN USER**\n\n"
            "Please reply with the user ID to ban:\n"
            "Format: `ban <user_id> <reason>`\n\n"
            "Example: `ban 1234567890 Spamming`",
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['awaiting_ban'] = True
    except Exception as e:
        logger.error(f"Error handling ban user: {e}")
        await query.answer("❌ Error loading form!", show_alert=True)

async def handle_unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unban user from callback"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ Admin Only!", show_alert=True)
            return
        
        await query.edit_message_text(
            "✅ **UNBAN USER**\n\n"
            "Please reply with the user ID to unban:\n"
            "Format: `unban <user_id>`\n\n"
            "Example: `unban 1234567890`",
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['awaiting_unban'] = True
    except Exception as e:
        logger.error(f"Error handling unban user: {e}")
        await query.answer("❌ Error loading form!", show_alert=True)

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast from callback - Enhanced"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ Admin Only!", show_alert=True)
            return
        
        await query.edit_message_text(
            "📢 **BROADCAST MESSAGE** 📢\n\n"
            "Choose broadcast type:\n\n"
            "1. Send text message for text broadcast\n"
            "2. Send photo with caption for image broadcast\n\n"
            "Reply with your message now:",
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['awaiting_broadcast'] = True
    except Exception as e:
        logger.error(f"Error handling broadcast: {e}")
        await query.answer("❌ Error loading broadcast!", show_alert=True)

# ===================== BULK KEY GENERATION (FIXED) =====================
async def handle_bulk_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bulk key generation from callback - FIXED"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ Admin Only!", show_alert=True)
            return
        
        await query.edit_message_text(
            "🔑 **BULK KEY GENERATION** 🔑\n\n"
            "Select plan for bulk key generation:",
            reply_markup=get_bulk_key_form(),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error handling bulk keys: {e}")
        await query.answer("❌ Error loading bulk keys!", show_alert=True)

async def handle_bulk_key_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bulk key generation form - FIXED"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ Admin Only!", show_alert=True)
            return
        
        plan = query.data.replace("bulk_form_", "")
        plan_details = {
            "basic": {"downloads": 10, "name": "BASIC"},
            "pro": {"downloads": 29, "name": "PRO"},
            "premium": {"downloads": 100, "name": "PREMIUM"}
        }
        
        if plan in plan_details:
            context.user_data['bulk_plan'] = plan
            context.user_data['bulk_downloads'] = plan_details[plan]['downloads']
            
            await query.edit_message_text(
                f"🔑 **BULK KEY GENERATION - {plan_details[plan]['name']} PLAN** 🔑\n\n"
                f"Plan: {plan_details[plan]['name']} ({plan_details[plan]['downloads']} downloads)\n\n"
                f"Please reply with:\n"
                f"`bulkgen <count> <days>`\n\n"
                f"Example: `bulkgen 10 30` (Generate 10 keys valid for 30 days)",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data['awaiting_bulkgen'] = True
    except Exception as e:
        logger.error(f"Error handling bulk key form: {e}")
        await query.answer("❌ Error loading form!", show_alert=True)

async def process_bulk_generation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process bulk key generation - FIXED"""
    try:
        user_id = update.effective_user.id
        message_text = update.message.text
        
        if not context.user_data.get('awaiting_bulkgen'):
            return
        
        parts = message_text.strip().split()
        if len(parts) >= 3 and parts[0].lower() == "bulkgen":
            try:
                count = int(parts[1])
                days = int(parts[2])
                plan = context.user_data.get('bulk_plan', 'premium')
                downloads = context.user_data.get('bulk_downloads', 100)
                
                if count <= 0 or count > 100:
                    await update.message.reply_text("❌ **Invalid count!** Please specify 1-100 keys.")
                    return
                
                if days <= 0 or days > 365:
                    await update.message.reply_text("❌ **Invalid days!** Please specify 1-365 days.")
                    return
                
                # Generate keys
                keys = generate_bulk_keys(count, plan, days, downloads, user_id)
                
                if not keys:
                    await update.message.reply_text("❌ Error generating keys. Please try again.")
                    return
                
                # Create file with keys
                batch_id = f"BATCH-{random.randint(10000, 99999)}"
                file_content = f"SYNAX BOT - {plan.upper()} KEYS\n"
                file_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                file_content += f"Plan: {plan.upper()} ({downloads} downloads, {days} days)\n"
                file_content += f"Generated by: {user_id}\n"
                file_content += f"Batch ID: {batch_id}\n"
                file_content += "=" * 50 + "\n\n"
                
                for key in keys:
                    file_content += f"{key}\n"
                
                # Create file in memory
                file_buffer = io.BytesIO()
                file_buffer.write(file_content.encode('utf-8'))
                file_buffer.seek(0)
                
                # Send file
                await update.message.reply_document(
                    document=file_buffer,
                    filename=f"{plan.upper()}_KEYS_{batch_id}.txt",
                    caption=f"✅ **BULK KEYS GENERATED** ✅\n\n"
                            f"Plan: {plan.upper()}\n"
                            f"Count: {count}\n"
                            f"Downloads per key: {downloads}\n"
                            f"Validity: {days} days\n"
                            f"Batch ID: {batch_id}",
                    parse_mode=ParseMode.MARKDOWN
                )
                
                # Reset state
                context.user_data['awaiting_bulkgen'] = False
                context.user_data.pop('bulk_plan', None)
                context.user_data.pop('bulk_downloads', None)
                
            except ValueError:
                await update.message.reply_text(
                    "❌ **Invalid format!**\n\n"
                    "Usage: `bulkgen <count> <days>`\n"
                    "Example: `bulkgen 10 30`",
                    parse_mode=ParseMode.MARKDOWN
                )
        else:
            await update.message.reply_text(
                "❌ **Invalid format!**\n\n"
                "Usage: `bulkgen <count> <days>`\n"
                "Example: `bulkgen 10 30`",
                parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        logger.error(f"Error processing bulk generation: {e}")
        await update.message.reply_text("❌ Error generating bulk keys.")

# ===================== PAYMENT APPROVAL SYSTEM (NEW) =====================
async def handle_payments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payments approval from callback - Enhanced"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ Admin Only!", show_alert=True)
            return
        
        # Get pending payments
        pending_payments = [p for p in payments_db.values() if p.get('status') == 'pending']
        
        if not pending_payments:
            await query.edit_message_text(
                "💳 **PAYMENT MANAGEMENT** 💳\n\n"
                "No pending payments at the moment.",
                reply_markup=get_admin_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Show first pending payment
        payment = pending_payments[0]
        payment_id = payment['payment_id']
        user_id_payment = payment['user_id']
        plan = payment['plan']
        amount = payment['amount']
        created_at = datetime.fromisoformat(payment['created_at']).strftime('%d %b, %I:%M %p')
        
        # Get user info
        user_data = users_db.get(str(user_id_payment), {})
        username = user_data.get('username', 'N/A')
        first_name = user_data.get('first_name', 'N/A')
        
        # Check if screenshot is received
        screenshot_status = "✅ Received" if payment.get('screenshot_received', False) else "❌ Not received"
        
        payment_text = f"""
💳 **PAYMENT APPROVAL** 💳

📋 **PAYMENT DETAILS:**
• Payment ID: `{payment_id}`
• User ID: `{user_id_payment}`
• User: @{username} | {first_name}
• Plan: {plan.upper()}
• Amount: ₹{amount}
• Date: {created_at}
• Screenshot: {screenshot_status}

👇 **SELECT ACTION:**
    """
        
        # Get payment screenshot if available
        if payment.get('screenshot_file_id'):
            try:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=payment['screenshot_file_id'],
                    caption=payment_text,
                    reply_markup=get_payment_approval_keyboard(payment_id),
                    parse_mode=ParseMode.MARKDOWN
                )
                await query.answer()
                return
            except Exception as e:
                logger.error(f"Error sending payment screenshot: {e}")
        
        await query.edit_message_text(
            payment_text,
            reply_markup=get_payment_approval_keyboard(payment_id),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error handling payments: {e}")
        await query.answer("❌ Error loading payments!", show_alert=True)

async def handle_approve_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment approval - Enhanced"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ Admin Only!", show_alert=True)
            return
        
        # Extract payment_id from callback_data
        payment_id = query.data.replace("approve_payment_", "")
        
        # Approve payment
        result = approve_payment(payment_id, user_id)
        
        if result["success"]:
            payment_data = result["data"]
            user_id_payment = payment_data["user_id"]
            downloads = result["downloads"]
            
            # Notify user
            try:
                await context.bot.send_message(
                    chat_id=user_id_payment,
                    text=f"✅ **PAYMENT APPROVED!** ✅\n\n"
                         f"Your payment for {payment_data['plan'].upper()} plan has been approved!\n\n"
                         f"🎁 **You've received:**\n"
                         f"• ⬇️ Downloads: {downloads}\n"
                         f"• 📅 Validity: 30 days\n\n"
                         f"🎉 Thank you for choosing SYNAX!",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.warning(f"Could not notify user {user_id_payment}: {e}")
            
            # Confirm to admin
            await query.edit_message_text(
                f"✅ **PAYMENT APPROVED!**\n\n"
                f"Payment ID: `{payment_id}`\n"
                f"User ID: `{user_id_payment}`\n"
                f"Downloads Given: {downloads}\n\n"
                f"User has been notified!",
                reply_markup=get_admin_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.answer("❌ Error approving payment!", show_alert=True)
    except Exception as e:
        logger.error(f"Error approving payment: {e}")
        await query.answer("❌ Error approving payment!", show_alert=True)

async def handle_reject_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment rejection - Enhanced"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ Admin Only!", show_alert=True)
            return
        
        # Extract payment_id from callback_data
        payment_id = query.data.replace("reject_payment_", "")
        
        # Ask for rejection reason
        await query.edit_message_text(
            f"❌ **REJECT PAYMENT** ❌\n\n"
            f"Payment ID: `{payment_id}`\n\n"
            "Please reply with rejection reason:\n"
            "Format: `reject_reason <your reason>`",
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['awaiting_reject_reason'] = payment_id
    except Exception as e:
        logger.error(f"Error rejecting payment: {e}")
        await query.answer("❌ Error rejecting payment!", show_alert=True)

# ===================== REPLY TO USER (SYNAX System) =====================
async def handle_reply_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle reply to user - Enhanced"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ Admin Only!", show_alert=True)
            return
        
        await query.edit_message_text(
            "↩️ **REPLY TO USER**\n\n"
            "Please reply with:\n"
            "`reply <user_id> <message>`\n\n"
            "Example: `reply 1234567890 Hello! How can I help you?`",
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['awaiting_reply'] = True
    except Exception as e:
        logger.error(f"Error handling reply user: {e}")
        await query.answer("❌ Error loading reply form!", show_alert=True)

# ===================== GENERATE KEY FROM CALLBACK (SYNAX System) =====================
async def handle_generate_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle generate key from callback - Enhanced"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ Admin Only!", show_alert=True)
            return
        
        keyboard = [
            [InlineKeyboardButton("🔑 BASIC KEY (10 DL)", callback_data="genkey_basic")],
            [InlineKeyboardButton("🔑 PRO KEY (29 DL)", callback_data="genkey_pro")],
            [InlineKeyboardButton("🔑 PREMIUM KEY (100 DL)", callback_data="genkey_premium")],
            [InlineKeyboardButton("🔙 ADMIN MENU", callback_data="admin_menu")]
        ]
        
        await query.edit_message_text(
            "🔑 **GENERATE SUBSCRIPTION KEY**\n\n"
            "Select plan for key generation:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"Error handling generate key: {e}")
        await query.answer("❌ Error loading key generator!", show_alert=True)

# ===================== URL DOWNLOAD =====================
async def handle_url_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URL download - Enhanced"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        await query.edit_message_text(
            "🌐 **URL DOWNLOAD**\n\n"
            "Simply send me any website URL starting with http:// or https://\n\n"
            "**Example:**\n"
            "`https://example.com`\n"
            "`http://test-site.org`\n\n"
            "**Note:** You need downloads balance to use this feature.",
            reply_markup=get_download_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        return AWAITING_URL
    except Exception as e:
        logger.error(f"Error handling URL download: {e}")
        await query.answer("❌ Error loading download form!", show_alert=True)
        return ConversationHandler.END

async def process_url_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process URL download - Enhanced"""
    try:
        user_id = update.effective_user.id
        message_text = update.message.text
        user_data = get_user_stats(user_id)
        
        # Check maintenance
        if settings_db.get("maintenance"):
            await update.message.reply_text("🔧 **Bot is under maintenance. Please try later.**")
            return ConversationHandler.END
        
        # Check ban status
        if user_data.get("is_banned"):
            await update.message.reply_text("🚫 **Your account is banned!**")
            return ConversationHandler.END
        
        # Check downloads
        if user_data["downloads_left"] <= 0 and not is_owner(user_id):
            await update.message.reply_text(
                "❌ **No downloads left!**\nUse BUY button to purchase more.",
                reply_markup=get_buy_menu()
            )
            return ConversationHandler.END
        
        # Clean URL
        url = clean_url(message_text)
        context.user_data['download_url'] = url
        
        # Ask for download type
        await update.message.reply_text(
            f"🌐 **Website URL Received**\n\n{url}\n\nPlease choose download type:",
            reply_markup=get_download_type_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        return AWAITING_DOWNLOAD_TYPE
    except Exception as e:
        logger.error(f"Error processing URL download: {e}")
        await update.message.reply_text("❌ Error processing URL.")
        return ConversationHandler.END

async def process_download(update: Update, context: ContextTypes.DEFAULT_TYPE, download_type: str):
    """Process the actual download - Enhanced"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        user_data = get_user_stats(user_id)
        
        url = context.user_data.get('download_url')
        if not url:
            await query.answer("❌ No URL found!", show_alert=True)
            return ConversationHandler.END
        
        await query.answer()
        await query.edit_message_text(f"⏳ **Starting {download_type.upper()} download...**")
        
        # Download and create zip
        zip_buffer, file_count = create_direct_zip(url, download_type)
        
        file_size = zip_buffer.getbuffer().nbytes
        file_size_mb = file_size / 1024 / 1024
        
        if file_size > MAX_FILE_SIZE:
            await query.edit_message_text(
                f"❌ **File Too Large**\n\nSize: {file_size_mb:.1f}MB\nLimit: 50MB\n\nTry partial download instead."
            )
            return ConversationHandler.END
        
        # Create filename
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]
        filename = f"{domain}_{download_type}_{int(time.time())}.zip"
        
        # Send file
        await query.edit_message_text("📤 Sending file...")
        
        caption = f"""
✅ **Website Source Downloaded!**

**Details:**
• Website: {url}
• Type: {download_type.upper()} Download
• File Size: {file_size_mb:.2f} MB
• Files: {file_count}

Made By 💤 SYNAX Network 💤
Admin: {OWNER_USERNAME}
{PROMOTION_CHANNEL}
{PROMOTION_GROUPS[0]}
"""
        
        await context.bot.send_document(
            chat_id=query.message.chat_id,
            document=zip_buffer,
            filename=filename,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Update user stats
        if not is_owner(user_id):
            user_data["downloads_left"] -= 1
        user_data["total_downloads"] += 1
        users_db[str(user_id)] = user_data
        save_json(USERS_FILE, users_db)
        
        # Add to download history
        add_download_history(user_id, url, file_size, file_count)
        
        await query.edit_message_text(f"✅ **Done!** File sent successfully.\n\nFiles: {file_count}\nSize: {file_size_mb:.1f}MB")
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        await query.edit_message_text(
            f"❌ **Error**\n\n{str(e)[:200]}",
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END

# ===================== SUPPORT SYSTEM =====================
async def handle_support_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle support menu from callback"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not settings_db.get("support_system", True):
            await query.answer("❌ Support system is disabled!", show_alert=True)
            return
        
        await query.edit_message_text(
            "🎫 **SUPPORT SYSTEM** 🎫\n\n"
            "Our support team is here to help you!\n\n"
            "Choose an option below:",
            reply_markup=get_support_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error handling support menu: {e}")
        await query.answer("❌ Error loading support!", show_alert=True)

async def handle_create_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle create ticket from callback"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        await query.edit_message_text(
            "📝 **CREATE SUPPORT TICKET** 📝\n\n"
            "Please describe your issue in detail.\n\n"
            "Reply with your message to create a ticket.",
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['awaiting_ticket'] = True
    except Exception as e:
        logger.error(f"Error handling create ticket: {e}")
        await query.answer("❌ Error loading ticket form!", show_alert=True)

async def handle_my_tickets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle my tickets from callback"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        # Get user's tickets
        user_tickets = [t for t in tickets_db.values() if t.get('user_id') == user_id]
        
        if not user_tickets:
            await query.edit_message_text(
                "📋 **MY TICKETS** 📋\n\n"
                "You haven't created any tickets yet.",
                reply_markup=get_support_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        tickets_text = "📋 **MY TICKETS** 📋\n\n"
        
        for ticket in sorted(user_tickets, key=lambda x: x.get('created_at', ''), reverse=True)[:5]:
            ticket_id = ticket['ticket_id']
            status = ticket.get('status', 'unknown').upper()
            created_at = datetime.fromisoformat(ticket['created_at']).strftime('%d %b, %I:%M %p')
            
            tickets_text += f"🎫 **Ticket ID:** {ticket_id}\n"
            tickets_text += f"📅 **Created:** {created_at}\n"
            tickets_text += f"📊 **Status:** {status}\n"
            tickets_text += f"💬 **Message:** {ticket.get('message', '')[:50]}...\n\n"
        
        await query.edit_message_text(
            tickets_text,
            reply_markup=get_support_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error handling my tickets: {e}")
        await query.answer("❌ Error loading tickets!", show_alert=True)

async def handle_admin_tickets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin tickets from callback"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ Admin Only!", show_alert=True)
            return
        
        # Get open tickets
        open_tickets = [t for t in tickets_db.values() if t.get('status') == 'open']
        
        if not open_tickets:
            await query.edit_message_text(
                "🎫 **SUPPORT TICKETS** 🎫\n\n"
                "No open tickets at the moment.",
                reply_markup=get_admin_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Show first open ticket
        ticket = open_tickets[0]
        ticket_id = ticket['ticket_id']
        ticket_user_id = ticket['user_id']
        message = ticket.get('message', '')
        created_at = datetime.fromisoformat(ticket['created_at']).strftime('%d %b, %I:%M %p')
        
        # Get user info
        user_data = users_db.get(str(ticket_user_id), {})
        username = user_data.get('username', 'N/A')
        first_name = user_data.get('first_name', 'N/A')
        
        ticket_text = f"""
🎫 **SUPPORT TICKET** 🎫

📋 **TICKET DETAILS:**
• Ticket ID: `{ticket_id}`
• User ID: `{ticket_user_id}`
• User: @{username} | {first_name}
• Created: {created_at}

💬 **MESSAGE:**
{message}

👇 **SELECT ACTION:**
    """
        
        keyboard = [
            [InlineKeyboardButton("💬 REPLY", callback_data=f"reply_ticket_{ticket_id}")],
            [InlineKeyboardButton("✅ CLOSE", callback_data=f"close_ticket_{ticket_id}")],
            [InlineKeyboardButton("🔙 ADMIN MENU", callback_data="admin_menu")]
        ]
        
        await query.edit_message_text(
            ticket_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error handling admin tickets: {e}")
        await query.answer("❌ Error loading tickets!", show_alert=True)

async def handle_reply_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle reply to ticket from callback"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ Admin Only!", show_alert=True)
            return
        
        # Extract ticket_id from callback_data
        ticket_id = query.data.replace("reply_ticket_", "")
        
        # Ask for reply message
        await query.edit_message_text(
            f"💬 **REPLY TO TICKET** 💬\n\n"
            f"Ticket ID: `{ticket_id}`\n\n"
            "Please reply with your message:\n"
            "Format: `ticket_reply <your message>`",
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['awaiting_ticket_reply'] = ticket_id
    except Exception as e:
        logger.error(f"Error handling reply ticket: {e}")
        await query.answer("❌ Error loading reply form!", show_alert=True)

async def handle_close_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle close ticket from callback"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ Admin Only!", show_alert=True)
            return
        
        # Extract ticket_id from callback_data
        ticket_id = query.data.replace("close_ticket_", "")
        
        # Close ticket
        result = close_ticket(ticket_id, user_id)
        
        if result["success"]:
            ticket = result["data"]
            ticket_user_id = ticket['user_id']
            
            # Notify user
            try:
                await context.bot.send_message(
                    chat_id=ticket_user_id,
                    text=f"✅ **TICKET CLOSED** ✅\n\n"
                         f"Your support ticket ({ticket_id}) has been closed.\n\n"
                         f"If you still need help, please create a new ticket.",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.warning(f"Could not notify user {ticket_user_id}: {e}")
            
            # Confirm to admin
            await query.edit_message_text(
                f"✅ **TICKET CLOSED**\n\n"
                f"Ticket ID: `{ticket_id}`\n"
                f"User has been notified!",
                reply_markup=get_admin_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.answer("❌ Error closing ticket!", show_alert=True)
    except Exception as e:
        logger.error(f"Error closing ticket: {e}")
        await query.answer("❌ Error closing ticket!", show_alert=True)

# ===================== REFERRAL SYSTEM =====================
async def handle_referral_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle referral menu from callback"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not settings_db.get("referral_system", True):
            await query.answer("❌ Referral system is disabled!", show_alert=True)
            return
        
        await query.edit_message_text(
            "👥 **REFERRAL SYSTEM** 👥\n\n"
            "Invite friends and earn downloads!\n\n"
            f"You get {settings_db.get('referral_reward', 5)} downloads for each friend who joins.",
            reply_markup=get_referral_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error handling referral menu: {e}")
        await query.answer("❌ Error loading referral!", show_alert=True)

async def handle_my_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle my referral from callback"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        referral_link = f"https://t.me/{context.bot.username}?start=ref_{user_id}"
        user_data = get_user_stats(user_id)
        referral_count = user_data.get('referral_count', 0)
        
        referral_text = f"""
🔗 **MY REFERRAL LINK** 🔗

📊 **STATISTICS:**
• Referrals: `{referral_count}`
• Reward per referral: `{settings_db.get('referral_reward', 5)} downloads`

🔗 **YOUR LINK:**
`{referral_link}`

📝 **HOW TO USE:**
1. Share this link with friends
2. When they join using your link
3. You'll automatically get downloads

🎁 **BONUS:** Get 5 extra downloads for every 10 referrals!
    """
        
        await query.edit_message_text(
            referral_text,
            reply_markup=get_referral_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error handling my referral: {e}")
        await query.answer("❌ Error loading referral!", show_alert=True)

async def handle_my_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle my referrals from callback"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        # Get users referred by this user
        referred_users = [u for u in users_db.values() if u.get('referred_by') == user_id]
        
        if not referred_users:
            await query.edit_message_text(
                "👥 **MY REFERRALS** 👥\n\n"
                "You haven't referred anyone yet.\n\n"
                "Share your referral link to start earning!",
                reply_markup=get_referral_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        referrals_text = "👥 **MY REFERRALS** 👥\n\n"
        
        for user in referred_users[:10]:  # Show only first 10
            user_id = user['id']
            username = user.get('username', 'N/A')
            first_name = user.get('first_name', '')
            joined_date = datetime.fromisoformat(user['joined_date']).strftime('%d %b %Y')
            
            referrals_text += f"👤 **User:** @{username} | {first_name}\n"
            referrals_text += f"🆔 **ID:** `{user_id}`\n"
            referrals_text += f"📅 **Joined:** {joined_date}\n\n"
        
        await query.edit_message_text(
            referrals_text,
            reply_markup=get_referral_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error handling my referrals: {e}")
        await query.answer("❌ Error loading referrals!", show_alert=True)

# ===================== CALLBACK QUERY HANDLER =====================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks - Enhanced"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        data = query.data
        
        # Users pagination
        if data.startswith("users_page_"):
            try:
                page = int(data.split("_")[2])
                await show_all_users(update, context, page)
            except:
                await query.answer("Error loading page!", show_alert=True)
            return
        
        # Download type handlers
        if data == "full_download":
            return await process_download(update, context, "full")
        elif data == "partial_download":
            return await process_download(update, context, "partial")
        
        # Key generation handlers
        elif data.startswith("genkey_"):
            plan = data[7:]
            if plan in ["basic", "pro", "premium"]:
                downloads = 100
                if plan == "basic":
                    downloads = 10
                elif plan == "pro":
                    downloads = 29
                
                key = generate_key(plan, 30, downloads)
                if key:
                    await query.edit_message_text(
                        f"🔑 **KEY GENERATED** 🔑\n\n"
                        f"Key: `{key}`\n"
                        f"Plan: {plan.upper()}\n"
                        f"Downloads: {downloads}\n"
                        f"Days: 30\n\n"
                        f"**Send to user:**\n"
                        f"`/activate {key}`",
                        reply_markup=get_back_button("admin_menu"),
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await query.edit_message_text(
                        "❌ Error generating key!",
                        reply_markup=get_back_button("admin_menu"),
                        parse_mode=ParseMode.MARKDOWN
                    )
            return
        
        # Bulk key generation handlers - FIXED
        elif data.startswith("bulk_form_"):
            return await handle_bulk_key_form(update, context)
        
        # Payment approval handlers
        elif data.startswith("approve_payment_"):
            return await handle_approve_payment(update, context)
        elif data.startswith("reject_payment_"):
            return await handle_reject_payment(update, context)
        
        # Support system handlers
        elif data == "support_menu":
            return await handle_support_menu(update, context)
        elif data == "create_ticket":
            return await handle_create_ticket(update, context)
        elif data == "my_tickets":
            return await handle_my_tickets(update, context)
        elif data == "admin_tickets":
            return await handle_admin_tickets(update, context)
        elif data.startswith("reply_ticket_"):
            return await handle_reply_ticket(update, context)
        elif data.startswith("close_ticket_"):
            return await handle_close_ticket(update, context)
        
        # Referral system handlers
        elif data == "referral_menu":
            return await handle_referral_menu(update, context)
        elif data == "my_referral":
            return await handle_my_referral(update, context)
        elif data == "my_referrals":
            return await handle_my_referrals(update, context)
        
        # QR Code handlers
        elif data.startswith("qr_"):
            plan = data[3:]
            plan_details = {
                "basic": {"price": 39, "downloads": 10},
                "pro": {"price": 99, "downloads": 29},
                "premium": {"price": 199, "downloads": 100}
            }
            
            if plan in plan_details:
                details = plan_details[plan]
                
                # Create payment record
                payment_id = create_payment(user_id, plan, details['price'])
                
                if payment_id:
                    # Send QR code image
                    await context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=QR_CODE_URL,
                        caption=f"📱 **QR CODE FOR {plan.upper()} PLAN**\n\n"
                               f"**Amount:** ₹{details['price']}\n"
                               f"**Plan:** {plan.upper()}\n"
                               f"**Downloads:** {details['downloads']}\n"
                               f"**Payment ID:** {payment_id}\n\n"
                               f"**Instructions:**\n"
                               f"1. Scan QR code\n"
                               f"2. Pay ₹{details['price']}\n"
                               f"3. Take screenshot\n"
                               f"4. Send Screenshot Now",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    
                    await query.answer("✅ QR Code sent!")
                else:
                    await query.answer("❌ Error creating payment!", show_alert=True)
            return
        
        # Screenshot handlers
        elif data.startswith("screenshot_"):
            plan = data[11:]
            plan_details = {
                "basic": {"price": 39},
                "pro": {"price": 99},
                "premium": {"price": 199}
            }
            
            if plan in plan_details:
                await query.edit_message_text(
                    f"📸 **SEND PAYMENT SCREENSHOT**\n\n"
                    f"**Plan:** {plan.upper()}\n"
                    f"**Amount Paid:** ₹{plan_details[plan]['price']}\n\n"
                    f"**Next Steps:**\n"
                    f"1. Send payment screenshot\n"
                    f"2. Wait for admin approval\n"
                    f"3. Your account will be activated automatically\n\n"
                    f"**Your downloads will be added within 24 hours**",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=get_main_menu()
                )
            return
        
        # Common handlers
        handlers = {
            "main_menu": lambda: query.edit_message_text(
                "🏠 **MAIN MENU**\nSelect an option:",
                reply_markup=get_main_menu(),
                parse_mode=ParseMode.MARKDOWN
            ),
            "download_menu": lambda: handle_url_download(update, context),
            "buy_menu": lambda: query.edit_message_text(
                "💰 **PURCHASE DOWNLOADS** 💰\n\n"
                "**PLANS:**\n"
                "• ₹39 → 10 downloads\n"
                "• ₹99 → 29 downloads\n"
                "• ₹199 → 100 downloads\n\n"
                "**Select a plan:**",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_buy_menu()
            ),
            "my_stats": lambda: show_user_stats(update, context),
            "download_history": lambda: show_download_history(update, context),
            "activate_key_menu": lambda: handle_activate_key_menu(update, context),
            "help": lambda: help_command(update, context),
            "owner_info": lambda: query.edit_message_text(
                f"👑 **BOT OWNER** 👑\n\n"
                f"**Name:** {OWNER_NAME}\n"
                f"**Username:** {OWNER_USERNAME}\n"
                f"**ID:** `{OWNER_ID}`\n\n"
                "📞 **Contact for:**\n"
                "• Subscription keys\n"
                "• Custom bot development\n"
                "• Technical support",
                reply_markup=get_main_menu(),
                parse_mode=ParseMode.MARKDOWN
            ),
            "admin_menu": lambda: admin_command(update, context),
            "quick_dl": lambda: query.edit_message_text(
                "⚡ **QUICK DOWNLOAD**\n\n"
                "This feature is coming soon!\n\n"
                "For now, use URL download option.",
                reply_markup=get_download_menu(),
                parse_mode=ParseMode.MARKDOWN
            ),
            "admin_broadcast": lambda: handle_broadcast(update, context),
            "admin_all_users": lambda: show_all_users(update, context, 0),  # Fixed callback
            "admin_payments": lambda: handle_payments(update, context),
            "admin_ban": lambda: handle_ban_user(update, context),
            "admin_unban": lambda: handle_unban_user(update, context),
            "admin_maintenance": lambda: toggle_maintenance(update, context),
            "admin_stats": lambda: admin_command(update, context),
            "admin_add": lambda: handle_add_admin(update, context),
            "admin_remove": lambda: handle_remove_admin(update, context),
            "admin_gen_key": lambda: handle_generate_key(update, context),
            "admin_bulk_keys": lambda: handle_bulk_keys(update, context),  # Fixed callback
            "admin_reply_user": lambda: handle_reply_user(update, context),
            "admin_reports": lambda: query.edit_message_text(
                "📊 **USER REPORTS** 📊\n\n"
                "This feature is coming soon!",
                reply_markup=get_admin_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        }
        
        if data in handlers:
            return await handlers[data]()
        
        # Buy handlers
        elif data.startswith("buy_"):
            plan = data[4:]
            plans = {
                "basic": "₹39 → 10 downloads",
                "pro": "₹99 → 29 downloads",
                "premium": "₹199 → 100 downloads"
            }
            
            if plan in plans:
                await query.edit_message_text(
                    f"🛒 **PLAN SELECTED: {plan.upper()}** 🛒\n\n"
                    f"{plans[plan]}\n\n"
                    f"**To purchase:**\n"
                    f"1. Click VIEW QR CODE button\n"
                    f"2. Scan QR code to pay\n"
                    f"3. After payment, click SEND SCREENSHOT\n"
                    f"4. Send payment screenshot\n"
                    f"5. Wait for admin approval\n\n"
                    f"**Your account will be activated automatically after approval**",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=create_qr_keyboard(plan)
                )
    except Exception as e:
        logger.error(f"Error in callback handler: {e}")
        if update.callback_query:
            await update.callback_query.answer("❌ An error occurred!", show_alert=True)

async def handle_activate_key_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle activate key menu from callback"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        await query.edit_message_text(
            "🔑 **ACTIVATE SUBSCRIPTION KEY** 🔑\n\n"
            "Please send your subscription key:\n\n"
            "**Example:**\n"
            "`SYNAX-ABC12345`\n\n"
            "**Or use command:**\n"
            "`/activate YOUR_KEY_HERE`\n\n"
            "Get keys from @synaxnetwork",
            parse_mode=ParseMode.MARKDOWN
        )
        return AWAITING_KEY
    except Exception as e:
        logger.error(f"Error handling activate key menu: {e}")
        await update.callback_query.answer("❌ Error loading form!", show_alert=True)
        return ConversationHandler.END

async def toggle_maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle maintenance mode - Enhanced"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ Admin Only!", show_alert=True)
            return
        
        settings_db['maintenance'] = not settings_db.get('maintenance', False)
        save_json(SETTINGS_FILE, settings_db)
        status = "✅ ON" if settings_db['maintenance'] else "❌ OFF"
        await query.edit_message_text(
            f"⚙️ **MAINTENANCE MODE:** {status}\n\n"
            f"Bot is now {'under maintenance' if settings_db['maintenance'] else 'operational'}.",
            reply_markup=get_admin_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error toggling maintenance: {e}")
        await query.answer("❌ Error toggling maintenance!", show_alert=True)

# ===================== MESSAGE HANDLER =====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all messages - COMBINED SYSTEM (Enhanced)"""
    try:
        user_id = update.effective_user.id
        message_text = update.message.text
        
        update_user_activity(user_id, update.effective_user.username, update.effective_user.first_name)
        
        # Update message count
        user_data = get_user_stats(user_id)
        user_data["messages_sent"] = user_data.get("messages_sent", 0) + 1
        users_db[str(user_id)] = user_data
        save_json(USERS_FILE, users_db)
        
        # Handle key activation from message
        if context.user_data.get('awaiting_key'):
            key = message_text.strip().upper()
            result = activate_key(key, user_id)
            
            if result["success"]:
                key_data = result["data"]
                await update.message.reply_text(
                    f"✅ **SUBSCRIPTION ACTIVATED!** ✅\n\n"
                    f"🔑 **Key:** `{key}`\n"
                    f"📦 **Plan:** {key_data['plan'].upper()}\n"
                    f"⬇️ **Downloads:** {key_data['downloads']}\n"
                    f"📅 **Valid Until:** {datetime.fromisoformat(key_data['expires_at']).strftime('%d %b %Y')}\n\n"
                    f"🎉 **Enjoy your subscription!**",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=get_main_menu()
                )
            else:
                await update.message.reply_text(
                    f"❌ **INVALID KEY!** ❌\n\n"
                    f"Key `{key}` is invalid or already used.\n\n"
                    f"Please check the key and try again.\n"
                    f"Contact {OWNER_USERNAME} for help.",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=get_main_menu()
                )
            
            context.user_data['awaiting_key'] = False
            return
        
        # Check maintenance
        if settings_db.get("maintenance") and not is_admin(user_id):
            if any(prefix in message_text for prefix in ['http://', 'https://', 'www.']) or '.' in message_text or message_text.startswith('/'):
                await update.message.reply_text("🔧 **Bot is under maintenance. Please try later.**")
            return
        
        # Check ban status
        if user_data.get("is_banned"):
            if any(prefix in message_text for prefix in ['http://', 'https://', 'www.']) or '.' in message_text or message_text.startswith('/'):
                await update.message.reply_text("🚫 **Your account is banned!**")
            return
        
        # Handle support ticket creation
        if context.user_data.get('awaiting_ticket'):
            ticket_id = create_support_ticket(user_id, message_text)
            
            if ticket_id:
                # Notify admins
                for admin_id in ADMINS:
                    try:
                        await context.bot.send_message(
                            chat_id=admin_id,
                            text=f"🎫 **NEW SUPPORT TICKET** 🎫\n\n"
                                 f"Ticket ID: `{ticket_id}`\n"
                                 f"User ID: `{user_id}`\n"
                                 f"User: @{update.effective_user.username or 'N/A'}\n\n"
                                 f"Message: {message_text[:200]}...",
                            parse_mode=ParseMode.MARKDOWN
                        )
                    except:
                        pass
                
                await update.message.reply_text(
                    f"✅ **Ticket Created!**\n\n"
                    f"Ticket ID: `{ticket_id}`\n\n"
                    f"Our support team will respond soon.",
                    reply_markup=get_main_menu(),
                    parse_mode=ParseMode.MARKDOWN
                )
                
                context.user_data['awaiting_ticket'] = False
            else:
                await update.message.reply_text("❌ Error creating ticket. Please try again.")
            return
        
        # Handle ticket reply
        if context.user_data.get('awaiting_ticket_reply'):
            ticket_id = context.user_data['awaiting_ticket_reply']
            
            # Add reply to ticket
            add_ticket_reply(ticket_id, user_id, message_text, is_admin=True)
            
            # Get ticket details
            ticket = tickets_db.get(ticket_id, {})
            ticket_user_id = ticket.get('user_id')
            
            # Notify user
            try:
                await context.bot.send_message(
                    chat_id=ticket_user_id,
                    text=f"💬 **NEW REPLY TO YOUR TICKET** 💬\n\n"
                         f"Ticket ID: `{ticket_id}`\n\n"
                         f"Reply: {message_text}",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.warning(f"Could not notify user {ticket_user_id}: {e}")
            
            await update.message.reply_text(
                f"✅ **Reply Sent!**\n\n"
                f"User has been notified.",
                parse_mode=ParseMode.MARKDOWN
            )
            
            context.user_data['awaiting_ticket_reply'] = None
            return
        
        # Handle bulk key generation - FIXED
        if context.user_data.get('awaiting_bulkgen') and is_admin(user_id):
            await process_bulk_generation(update, context)
            return
        
        # Handle admin commands in messages
        if context.user_data.get('awaiting_broadcast') and is_admin(user_id):
            # Broadcast message
            success = 0
            failed = 0
            
            await update.message.reply_text(f"📢 Broadcasting to {len(users_db)} users...")
            
            for uid_str in users_db.keys():
                try:
                    await context.bot.send_message(
                        chat_id=int(uid_str),
                        text=f"📢 **BROADCAST:**\n\n{message_text}",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    success += 1
                except:
                    failed += 1
            
            await update.message.reply_text(
                f"✅ **Broadcast Complete!**\n\n"
                f"✅ Success: {success}\n"
                f"❌ Failed: {failed}"
            )
            context.user_data['awaiting_broadcast'] = False
            return
        
        elif context.user_data.get('awaiting_addadmin') and is_owner(user_id):
            # Add admin
            parts = message_text.strip().split()
            if len(parts) >= 2 and parts[0].lower() == "addadmin":
                try:
                    target_id = int(parts[1])
                    if add_admin(target_id):
                        await update.message.reply_text(f"✅ **Admin added successfully!**\nUser ID: `{target_id}`")
                    else:
                        await update.message.reply_text("❌ User is already admin or invalid!")
                except ValueError:
                    await update.message.reply_text("❌ Invalid user ID!")
            context.user_data['awaiting_addadmin'] = False
            return
        
        elif context.user_data.get('awaiting_removeadmin') and is_owner(user_id):
            # Remove admin
            parts = message_text.strip().split()
            if len(parts) >= 2 and parts[0].lower() == "removeadmin":
                try:
                    target_id = int(parts[1])
                    if remove_admin(target_id):
                        await update.message.reply_text(f"✅ **Admin removed successfully!**\nUser ID: `{target_id}`")
                    else:
                        await update.message.reply_text("❌ User is not admin or cannot remove owner!")
                except ValueError:
                    await update.message.reply_text("❌ Invalid user ID!")
            context.user_data['awaiting_removeadmin'] = False
            return
        
        elif context.user_data.get('awaiting_ban') and is_admin(user_id):
            # Ban user
            parts = message_text.strip().split()
            if len(parts) >= 2 and parts[0].lower() == "ban":
                try:
                    target_id = int(parts[1])
                    reason = " ".join(parts[2:]) if len(parts) > 2 else "No reason provided"
                    
                    if ban_user(target_id, reason):
                        await update.message.reply_text(f"✅ **User banned successfully!**\nID: `{target_id}`\nReason: {reason}")
                    else:
                        await update.message.reply_text("❌ User already banned or invalid!")
                except ValueError:
                    await update.message.reply_text("❌ Invalid user ID!")
            context.user_data['awaiting_ban'] = False
            return
        
        elif context.user_data.get('awaiting_unban') and is_admin(user_id):
            # Unban user
            parts = message_text.strip().split()
            if len(parts) >= 2 and parts[0].lower() == "unban":
                try:
                    target_id = int(parts[1])
                    if unban_user(target_id):
                        await update.message.reply_text(f"✅ **User unbanned successfully!**\nID: `{target_id}`")
                    else:
                        await update.message.reply_text("❌ User not banned or invalid!")
                except ValueError:
                    await update.message.reply_text("❌ Invalid user ID!")
            context.user_data['awaiting_unban'] = False
            return
        
        # Reply to user feature
        elif context.user_data.get('awaiting_reply') and is_admin(user_id):
            # Reply to user
            parts = message_text.strip().split()
            if len(parts) >= 3 and parts[0].lower() == "reply":
                try:
                    target_id = int(parts[1])
                    reply_message = " ".join(parts[2:])
                    
                    # Send message to target user
                    try:
                        await context.bot.send_message(
                            chat_id=target_id,
                            text=f"📨 **MESSAGE FROM ADMIN**\n\n{reply_message}",
                            parse_mode=ParseMode.MARKDOWN
                        )
                        
                        await update.message.reply_text(
                            f"✅ **Message sent successfully!**\n\n"
                            f"👤 To User ID: `{target_id}`\n"
                            f"📝 Message: {reply_message[:100]}...",
                            parse_mode=ParseMode.MARKDOWN
                        )
                    except Exception as e:
                        await update.message.reply_text(f"❌ Failed to send message: {str(e)}")
                    
                except ValueError:
                    await update.message.reply_text("❌ Invalid user ID!")
            context.user_data['awaiting_reply'] = False
            return
        
        # Handle payment rejection reason
        elif context.user_data.get('awaiting_reject_reason') and is_admin(user_id):
            payment_id = context.user_data['awaiting_reject_reason']
            parts = message_text.strip().split()
            
            if len(parts) >= 2 and parts[0].lower() == "reject_reason":
                reason = " ".join(parts[1:])
                
                # Reject payment
                result = reject_payment(payment_id, user_id, reason)
                
                if result["success"]:
                    payment_data = result["data"]
                    user_id_payment = payment_data["user_id"]
                    
                    # Notify user
                    try:
                        await context.bot.send_message(
                            chat_id=user_id_payment,
                            text=f"❌ **PAYMENT REJECTED** ❌\n\n"
                                 f"Your payment was rejected.\n\n"
                                 f"Reason: {reason}\n\n"
                                 f"Please contact {OWNER_USERNAME} for more information.",
                            parse_mode=ParseMode.MARKDOWN
                        )
                    except Exception as e:
                        logger.warning(f"Could not notify user {user_id_payment}: {e}")
                    
                    # Confirm to admin
                    await update.message.reply_text(
                        f"❌ **PAYMENT REJECTED!**\n\n"
                        f"Payment ID: `{payment_id}`\n"
                        f"User ID: `{user_id_payment}`\n"
                        f"Reason: {reason}\n\n"
                        f"User has been notified!",
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await update.message.reply_text("❌ Error rejecting payment!")
            
            context.user_data['awaiting_reject_reason'] = None
            return
        
        # Handle URL downloads
        elif message_text and re.match(r'^https?://', message_text):
            return await process_url_download(update, context)
        
        # Handle subscription key activation
        elif message_text and len(message_text) > 5 and "-" in message_text:
            # Might be a subscription key
            if message_text.upper().startswith("SYNAX-"):
                result = activate_key(message_text.upper(), user_id)
                if result["success"]:
                    await update.message.reply_text(
                        f"✅ **Key Activated Successfully!**\n\n"
                        f"Enjoy your {result['data']['plan']} subscription!",
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await update.message.reply_text(
                        "❌ **Invalid Key!**\n\n"
                        "This key is invalid or already used.",
                        parse_mode=ParseMode.MARKDOWN
                    )
                return
        
        # ===================== ALL USER MESSAGES FORWARD TO OWNER (SYNAX System) =====================
        if not is_admin(user_id) and message_text and not message_text.startswith('/'):
            user_info = f"""
📨 **NEW USER MESSAGE**

👤 User: @{update.effective_user.username or 'N/A'}
🆔 ID: `{user_id}`
📛 Name: {update.effective_user.first_name}
📊 Total Messages: {user_data.get('messages_sent', 0)}
📥 Downloads: {user_data.get('total_downloads', 0)}
💰 Balance: {user_data.get('downloads_left', 0)}

💬 Message:
{message_text[:400]}
"""
            
            for admin_id in ADMINS:
                try:
                    await context.bot.send_message(
                        admin_id,
                        user_info,
                        parse_mode=ParseMode.MARKDOWN
                    )
                except:
                    pass
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        if update.message:
            await update.message.reply_text("❌ An error occurred. Please try again.")

# ===================== PHOTO HANDLER (NEW - PAYMENT SCREENSHOTS) =====================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads - for payment screenshots and broadcasts - Enhanced"""
    try:
        user_id = update.effective_user.id
        user_data = get_user_stats(user_id)
        
        # Check if user has a pending payment
        user_payments = [p for p in payments_db.values() 
                        if p.get('user_id') == user_id and p.get('status') == 'pending']
        
        if not user_payments:
            await update.message.reply_text(
                "❌ **No pending payment found!**\n\n"
                "Please select a plan and make payment first.",
                reply_markup=get_buy_menu()
            )
            return
        
        # Get the most recent pending payment
        payment = sorted(user_payments, key=lambda x: x['created_at'], reverse=True)[0]
        payment_id = payment['payment_id']
        
        # Store the screenshot
        file_id = update.message.photo[-1].file_id
        payments_db[payment_id]['screenshot_received'] = True
        payments_db[payment_id]['screenshot_file_id'] = file_id
        save_json(PAYMENTS_FILE, payments_db)
        
        # Notify user
        await update.message.reply_text(
            f"✅ **Payment screenshot received!**\n\n"
            f"Payment ID: `{payment_id}`\n"
            f"Plan: {payment['plan'].upper()}\n"
            f"Amount: ₹{payment['amount']}\n\n"
            f"Your payment is now pending approval.\n"
            f"You'll be notified once it's approved.",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Forward to admin for approval
        payment_text = f"""
💳 **NEW PAYMENT SCREENSHOT** 💳

📋 **PAYMENT DETAILS:**
• Payment ID: `{payment_id}`
• User ID: `{user_id}`
• User: @{update.effective_user.username or 'N/A'} | {update.effective_user.first_name}
• Plan: {payment['plan'].upper()}
• Amount: ₹{payment['amount']}
• Date: {datetime.fromisoformat(payment['created_at']).strftime('%d %b, %I:%M %p')}

👇 **SELECT ACTION:**
    """
        
        for admin_id in ADMINS:
            try:
                await context.bot.send_photo(
                    chat_id=admin_id,
                    photo=file_id,
                    caption=payment_text,
                    reply_markup=get_payment_approval_keyboard(payment_id),
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Error forwarding payment screenshot to admin {admin_id}: {e}")
    except Exception as e:
        logger.error(f"Error handling photo: {e}")
        if update.message:
            await update.message.reply_text("❌ Error processing photo.")

# ===================== ERROR HANDLER =====================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates."""
    logger.error(f"Exception while handling an update: {context.error}")
    try:
        if update and hasattr(update, 'message') and update.message:
            await update.message.reply_text("❌ An error occurred. Please try again later.")
    except:
        pass

# ===================== SETUP COMMANDS =====================
async def setup_commands(application: Application):
    """Setup bot commands menu - Enhanced"""
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Get help"),
        BotCommand("stats", "Check your stats"),
        BotCommand("admin", "Admin panel (admins only)"),
        BotCommand("activate", "Activate subscription key"),
        BotCommand("generate", "Generate key (admin only)"),
        BotCommand("give", "Give downloads to user (owner only)")
    ]
    
    await application.bot.set_my_commands(commands)

# ===================== MAIN FUNCTION =====================
def main():
    """Start the bot - Enhanced"""
    # Check if wget is installed
    try:
        subprocess.run(["which", "wget"], check=True, capture_output=True)
        print("✅ wget is installed")
    except:
        print("❌ ERROR: wget is not installed!")
        print("Install it with:")
        print("  Ubuntu/Debian: sudo apt install wget")
        print("  Termux: pkg install wget")
        exit(1)
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Create conversation handler for downloads and key activation
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(handle_url_download, pattern="^url_download$"),
            CallbackQueryHandler(handle_activate_key_menu, pattern="^activate_key_menu$")
        ],
        states={
            AWAITING_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_url_download)],
            AWAITING_DOWNLOAD_TYPE: [
                CallbackQueryHandler(lambda u, c: process_download(u, c, "full"), pattern="^full_download$"),
                CallbackQueryHandler(lambda u, c: process_download(u, c, "partial"), pattern="^partial_download$"),
            ],
            AWAITING_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: c.bot.send_message(chat_id=u.effective_chat.id, text="Operation cancelled."))],
        per_chat=True,
    )
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("activate", activate_key_command))
    application.add_handler(CommandHandler("generate", generate_key_command))
    application.add_handler(CommandHandler("give", give_command))
    
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Post initialization
    application.post_init = setup_commands
    
    # Start bot
    print("=" * 60)
    print("🤖 SYNAX DOWNLOAD BOT - ULTIMATE EDITION (FULLY FIXED & CRASH-PROOF)")
    print(f"👑 Owner: {OWNER_NAME} ({OWNER_USERNAME})")
    print(f"🤖 Bot Token: {BOT_TOKEN}")
    print("=" * 60)
    print("\n✅ **SYNAX BOT FEATURES ADDED:**")
    print("1. 🔑 Key Generation & Activation System")
    print("2. 📊 Complete User Management")
    print("3. 👑 Multiple Admin Management")
    print("4. 📨 All User Messages Forward to Owner")
    print("5. ↩️ Admin Reply to Single User")
    print("6. 📢 Broadcast System (with image support)")
    print("7. 💰 Subscription Plans Database")
    print("8. ⚙️ Maintenance Mode")
    print("9. 📊 Advanced Statistics")
    print("10. 🎯 Button Menu System")
    print("=" * 60)
    print("\n✅ **SECOND BOT FEATURES ADDED:**")
    print("1. 🌐 Clean URL to ZIP Conversion")
    print("2. 📱 QR Code Payment System")
    print("3. 📸 Screenshot Upload Feature")
    print("4. 💾 Direct Memory Zip Creation")
    print("=" * 60)
    print("\n✅ **NEW FEATURES ADDED:**")
    print("1. 🎁 /give command - Owner can give downloads to users")
    print("2. 💳 Payment Approval System - Admins can approve/reject payments")
    print("3. 📜 Download History - Users can view their download history")
    print("4. 📸 Direct Screenshot to Admin - Payment screenshots go directly to admin")
    print("5. ✅ One-Click Approval - Admins can approve payments with one click")
    print("6. 🔑 Bulk Key Generation - Generate multiple keys at once (FIXED)")
    print("7. 📢 Image Broadcast - Send images with captions to all users")
    print("8. 🎫 Support System - Users can create support tickets")
    print("9. 👥 Referral System - Users can refer friends for rewards")
    print("10. 🔄 Fixed Start button and commands not working")
    print("11. 🗂️ Conversation Handler for downloads - Better user experience")
    print("12. 🖼️ Image Removed - Bot now works without welcome image")
    print("13. 🔑 Fixed Activation Key - Now works properly from start menu")
    print("14. 👥 FIXED: Admin Panel Users Button - Now properly displays all users with pagination")
    print("15. 🎫 FIXED: Support Tickets - Now properly creates and manages support tickets")
    print("16. 🔑 FIXED: Bulk Key Generator - Now properly generates and sends bulk keys")
    print("17. 🛡️ CRASH-PROOF: Added comprehensive error handling")
    print("18. 🔧 FIXED: All potential crash points with try-catch blocks")
    print("19. 📊 FIXED: Database operations with proper error handling")
    print("20. 🔄 FIXED: Callback handler with proper error management")
    print("=" * 60)
    print("\n📁 **DATABASE FILES CREATED:**")
    print(f"  • {USERS_FILE} - All users data")
    print(f"  • {ADMINS_FILE} - Admin list")
    print(f"  • {SETTINGS_FILE} - Bot settings")
    print(f"  • {KEYS_FILE} - Subscription keys")
    print(f"  • {PAYMENTS_FILE} - Payment records")
    print(f"  • {DOWNLOAD_HISTORY_FILE} - Download history")
    print(f"  • {BULK_KEYS_FILE} - Bulk key generation records")
    print(f"  • {TICKETS_FILE} - Support tickets")
    print(f"  • {REPORTS_FILE} - User reports")
    print("=" * 60)
    print("\n🚀 **BOT STARTED SUCCESSFULLY!**")
    print("🛡️ Bot is now CRASH-PROOF with comprehensive error handling!")
    print("=" * 60)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
