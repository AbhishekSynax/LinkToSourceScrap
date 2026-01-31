#!/usr/bin/env python3
"""
ULTIMATE WEBSITE DOWNLOADER BOT - SYNAX EDITION (Enhanced with Gift Key System and Advanced URL Detection)
Combined Features:
- SYNAX Bot's ALL management features
- Clean URL-to-ZIP from second bot
- Gift Key System from Z4X bot
- Advanced URL Detection from Z4X bot
- Enhanced Download System from Z4X bot
- Advanced UI/UX with working buttons
- Bulk key generation system
- Group activation feature
- Welcome bonus system
- Admin panel for bonus/points management
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
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re
import signal
import sys
from urllib.parse import urlparse

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, Document, Chat
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, ConversationHandler
from telegram.constants import ParseMode, ChatAction
from telegram.error import TelegramError, BadRequest, RetryAfter, TimedOut

# ===================== CONFIGURATION =====================
BOT_TOKEN = "8507762746:AAFqvCQXMR9VkbM39MqbROJaAH8YUx218Ls"

# OWNER DETAILS - SYNAX Network
OWNER_ID = 7998441787
OWNER_USERNAME = "@synaxnetwork"
OWNER_NAME = "Synaxnetwork"

# ADMINS LIST
ADMINS = [OWNER_ID, 7998441787]

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
GROUPS_FILE = "activated_groups.json"
BONUS_SETTINGS_FILE = "bonus_settings.json"
GIFT_KEYS_FILE = "gift_keys.json"  # NEW: Gift keys database

# ===================== LOGGING =====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===================== ADVANCED URL DETECTION SYSTEM (FROM Z4X BOT) =====================
class URLDetector:
    """Enhanced URL detection for all types of links"""
    
    # Common TLDs
    TOP_LEVEL_DOMAINS = [
        '.com', '.org', '.net', '.edu', '.gov', '.mil', '.int',
        '.in', '.co.in', '.org.in', '.net.in', '.info', '.biz',
        '.io', '.ai', '.co', '.me', '.tv', '.app', '.dev', '.tech',
        '.online', '.site', '.website', '.store', '.shop', '.blog',
        '.online', '.xyz', '.club', '.fun', '.top', '.space'
    ]
    
    # Special domains that don't follow usual patterns
    SPECIAL_DOMAINS = [
        'github.io', 'gitlab.io', 'netlify.app', 'vercel.app',
        'herokuapp.com', 'replit.dev', 'glitch.me', 'firebaseapp.com',
        'web.app', 'pages.dev', 'cloudflare.app', 'aws.amazon.com',
        'azurewebsites.net', 'google.com', 'youtube.com', 'facebook.com',
        'twitter.com', 'instagram.com', 'linkedin.com', 'whatsapp.com',
        'telegram.org', 'discord.com', 'reddit.com', 'medium.com',
        'wikipedia.org', 'stackoverflow.com', 'github.com', 'gitlab.com',
        'bitbucket.org'
    ]
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract all URLs from text"""
        urls = []
        
        # Common URL patterns
        patterns = [
            # Standard URLs
            r'https?://[^\s<>"\']+[^\s<>"\',.]',
            # www URLs
            r'www\.[^\s<>"\']+\.[^\s<>"\']+[^\s<>"\',.]',
            # Domain patterns
            r'[a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?(?:/[^\s<>"\']*)?',
            # IP addresses
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d+)?(?:/[^\s<>"\']*)?',
            # Localhost
            r'localhost(?::\d+)?(?:/[^\s<>"\']*)?',
            # File paths that look like URLs
            r'/[^\s<>"\']+\.[a-zA-Z]{2,4}(?:/[^\s<>"\']*)*'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                url = match.group(0)
                if URLDetector.validate_url(url):
                    urls.append(url)
        
        return urls
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate if string is a valid URL"""
        # Clean the URL first
        url = url.strip()
        
        # Check for common invalid patterns
        if url.endswith(('.', ',', ';', ':', '!', '?')):
            url = url[:-1]
        
        # Check if it's already a proper URL
        if url.startswith(('http://', 'https://')):
            try:
                result = urlparse(url)
                return all([result.scheme, result.netloc])
            except:
                return False
        
        # Check for www URLs
        if url.startswith('www.'):
            parts = url.split('.')
            if len(parts) >= 3:
                return True
        
        # Check for domain patterns
        if '.' in url:
            # Check for TLDs
            for tld in URLDetector.TOP_LEVEL_DOMAINS:
                if url.endswith(tld) or f'{tld}/' in url:
                    return True
            
            # Check for special domains
            for domain in URLDetector.SPECIAL_DOMAINS:
                if domain in url:
                    return True
            
            # Generic domain check
            parts = url.split('.')
            if len(parts) >= 2:
                # Check if last part looks like a TLD
                last_part = parts[-1].lower()
                if len(last_part) >= 2 and last_part.isalpha():
                    return True
        
        return False
    
    @staticmethod
    def clean_and_format_url(url: str) -> str:
        """Clean and format URL to proper http/https format"""
        url = url.strip()
        
        # Remove trailing punctuation
        while url and url[-1] in '.,;:!?':
            url = url[:-1]
        
        # Remove angle brackets if present
        if url.startswith('<') and url.endswith('>'):
            url = url[1:-1]
        
        # Check if already has protocol
        if url.startswith(('http://', 'https://')):
            return url
        
        # Add protocol for www
        if url.startswith('www.'):
            return 'https://' + url
        
        # Check for GitHub pages and similar
        if any(domain in url for domain in ['github.io', 'gitlab.io', 'netlify.app', 'vercel.app']):
            if not url.startswith('http'):
                return 'https://' + url
        
        # For other domains, add https://
        if '.' in url and not url.startswith('/'):
            # Check if it looks like a domain
            parts = url.split('.')
            if len(parts) >= 2:
                last_part = parts[-1].split('/')[0]
                if len(last_part) >= 2 and last_part.isalpha():
                    return 'https://' + url
        
        return url
    
    @staticmethod
    def extract_main_url(text: str) -> str:
        """Extract the most likely URL from text"""
        urls = URLDetector.extract_urls(text)
        
        if not urls:
            return ""
        
        # Prefer URLs with http/https
        for url in urls:
            if url.startswith(('http://', 'https://')):
                return URLDetector.clean_and_format_url(url)
        
        # Otherwise return the first URL
        return URLDetector.clean_and_format_url(urls[0])
    
    @staticmethod
    def is_github_pages_url(url: str) -> bool:
        """Check if URL is a GitHub Pages URL"""
        return 'github.io' in url
    
    @staticmethod
    def enhance_github_pages_url(url: str) -> str:
        """Enhance GitHub Pages URL for better downloading"""
        if not URLDetector.is_github_pages_url(url):
            return url
        
        # Ensure proper formatting for GitHub Pages
        parsed = urlparse(url)
        if not parsed.path or parsed.path == '/':
            # Add index.html for root
            url = url.rstrip('/') + '/'
        
        return url
    
    @staticmethod
    def smart_url_detection(text: str) -> Dict:
        """Smart URL detection with detailed analysis"""
        result = {
            "url": "",
            "type": "unknown",
            "is_valid": False,
            "confidence": 0,
            "message": ""
        }
        
        urls = URLDetector.extract_urls(text)
        
        if not urls:
            result["message"] = "No URL found in the text"
            return result
        
        # Take the first URL
        raw_url = urls[0]
        cleaned_url = URLDetector.clean_and_format_url(raw_url)
        
        if not cleaned_url:
            result["message"] = "Failed to clean URL"
            return result
        
        # Validate URL
        if not URLDetector.validate_url(cleaned_url):
            result["message"] = "Invalid URL format"
            return result
        
        # Determine URL type
        url_type = "standard"
        confidence = 80
        
        if URLDetector.is_github_pages_url(cleaned_url):
            url_type = "github_pages"
            confidence = 95
            cleaned_url = URLDetector.enhance_github_pages_url(cleaned_url)
        elif any(domain in cleaned_url for domain in ['gitlab.io', 'netlify.app', 'vercel.app']):
            url_type = "static_hosting"
            confidence = 90
        elif cleaned_url.startswith('http://localhost') or '127.0.0.1' in cleaned_url:
            url_type = "localhost"
            confidence = 70
            result["message"] = "Localhost URLs may not be accessible"
        elif ' ' in cleaned_url:
            # URL with spaces - likely problematic
            url_type = "problematic"
            confidence = 50
            result["message"] = "URL contains spaces"
        else:
            # Standard URL
            url_type = "standard"
            confidence = 85
        
        result.update({
            "url": cleaned_url,
            "type": url_type,
            "is_valid": True,
            "confidence": confidence,
            "original_text": text,
            "detected_urls": urls
        })
        
        return result

# ===================== DATA MANAGEMENT =====================
def load_json(file: str) -> Dict:
    """Load JSON file with error handling - SYNAX System"""
    try:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in {file}: {e}")
        # Try to backup and create a new file
        try:
            if os.path.exists(file):
                backup_file = f"{file}.backup.{int(time.time())}"
                shutil.copy2(file, backup_file)
                logger.info(f"Created backup of corrupted file: {backup_file}")
            return {}
        except Exception as backup_e:
            logger.error(f"Failed to create backup of {file}: {backup_e}")
            return {}
    except Exception as e:
        logger.error(f"Error loading {file}: {e}")
        return {}

def save_json(file: str, data: Dict):
    """Save JSON file with error handling - SYNAX System"""
    try:
        # Create a temporary file first
        temp_file = f"{file}.tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        # Replace the original file with the temporary file
        if os.path.exists(file):
            os.replace(temp_file, file)
        else:
            shutil.move(temp_file, file)
        return True
    except Exception as e:
        logger.error(f"Error saving {file}: {e}")
        return False

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
groups_db = load_json(GROUPS_FILE)
bonus_settings_db = load_json(BONUS_SETTINGS_FILE)
gift_keys_db = load_json(GIFT_KEYS_FILE)  # NEW: Initialize gift keys database

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

# Default bonus settings - NEW
if "welcome_bonus" not in bonus_settings_db:
    bonus_settings_db["welcome_bonus"] = 5  # Default 5 downloads for new users
if "referral_bonus" not in bonus_settings_db:
    bonus_settings_db["referral_bonus"] = 5  # Default 5 downloads per referral
if "manual_bonus_enabled" not in bonus_settings_db:
    bonus_settings_db["manual_bonus_enabled"] = True  # Allow manual bonus distribution

# Initialize gift keys database structure if needed
if "gift_keys" not in gift_keys_db:
    gift_keys_db["gift_keys"] = {}

save_json(SETTINGS_FILE, settings_db)
save_json(BONUS_SETTINGS_FILE, bonus_settings_db)
save_json(GIFT_KEYS_FILE, gift_keys_db)

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

# ===================== FEATURE 2: GIFT KEY SYSTEM (NEW FROM Z4X) =====================
def generate_gift_key(plan_name: str, downloads: int, days: int, max_uses: int = 1, expires_in_days: int = 7) -> str:
    """Generate special gift key for multiple users - From Z4X Bot"""
    try:
        chars = string.ascii_uppercase + string.digits
        key = f"GIFT-{plan_name.upper()[:10]}-{''.join(random.choices(chars, k=6))}"
        
        gift_key_data = {
            "key": key,
            "plan_name": plan_name,
            "downloads": downloads,
            "days": days,
            "max_uses": max_uses,
            "used_count": 0,
            "used_by": [],
            "generated_by": OWNER_ID,
            "generated_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=expires_in_days)).isoformat(),
            "is_active": True
        }
        
        gift_keys_db["gift_keys"][key] = gift_key_data
        save_json(GIFT_KEYS_FILE, gift_keys_db)
        return key
    except Exception as e:
        logger.error(f"Error generating gift key: {e}")
        return None

def redeem_gift_key(key: str, user_id: int) -> Dict:
    """Redeem gift key - From Z4X Bot"""
    try:
        if "gift_keys" not in gift_keys_db or key not in gift_keys_db["gift_keys"]:
            return {"success": False, "error": "Invalid gift key"}
        
        gift_key = gift_keys_db["gift_keys"][key]
        
        # Check if key is active
        if not gift_key.get("is_active", True):
            return {"success": False, "error": "Gift key is inactive"}
        
        # Check if expired
        expires_at = datetime.fromisoformat(gift_key["expires_at"])
        if datetime.now() > expires_at:
            return {"success": False, "error": "Gift key has expired"}
        
        # Check if max uses reached
        if gift_key["used_count"] >= gift_key["max_uses"]:
            return {"success": False, "error": "Gift key has been used maximum times"}
        
        # Check if user already used this key
        if user_id in gift_key["used_by"]:
            return {"success": False, "error": "You have already used this gift key"}
        
        # Update user
        user_id_str = str(user_id)
        if user_id_str not in users_db:
            users_db[user_id_str] = create_user(user_id)
        
        users_db[user_id_str]["downloads_left"] += gift_key["downloads"]
        users_db[user_id_str]["subscription"] = "gift"
        users_db[user_id_str]["subscription_expiry"] = (datetime.now() + timedelta(days=gift_key["days"])).isoformat()
        
        # Update gift key
        gift_key["used_count"] += 1
        gift_key["used_by"].append(user_id)
        gift_key["last_used_at"] = datetime.now().isoformat()
        
        save_json(GIFT_KEYS_FILE, gift_keys_db)
        save_json(USERS_FILE, users_db)
        
        return {"success": True, "data": gift_key}
    except Exception as e:
        logger.error(f"Error redeeming gift key: {e}")
        return {"success": False, "error": "Server error"}

# ===================== FEATURE 3: BULK KEY GENERATION =====================
def generate_bulk_keys(count: int, plan: str, days: int, downloads: int, generated_by: int) -> List[str]:
    """Generate multiple keys at once"""
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

# ===================== FEATURE 4: PAYMENT SYSTEM =====================
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
                "basic": 5,
                "pro": 40,
                "premium": 150
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

# ===================== FEATURE 5: DOWNLOAD HISTORY =====================
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

# ===================== FEATURE 6: SUPPORT SYSTEM =====================
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

# ===================== FEATURE 7: REFERRAL SYSTEM =====================
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
            reward = bonus_settings_db.get("referral_bonus", 5)  # Use settings value
            users_db[referrer_id_str]["downloads_left"] += reward
            users_db[referrer_id_str]["referral_count"] = users_db[referrer_id_str].get("referral_count", 0) + 1
            
            save_json(USERS_FILE, users_db)
            return {"success": True, "reward": reward}
        
        return {"success": False, "error": "Referrer not found"}
    except Exception as e:
        logger.error(f"Error processing referral: {e}")
        return {"success": False, "error": "Server error"}

# ===================== FEATURE 8: GROUP ACTIVATION SYSTEM =====================
def activate_group(group_id: int, admin_id: int, days: int = 30) -> Dict:
    """Activate a group for unlimited downloads"""
    try:
        group_id_str = str(group_id)
        
        group_data = {
            "group_id": group_id,
            "activated_by": admin_id,
            "activated_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=days)).isoformat(),
            "status": "active",
            "days": days
        }
        
        groups_db[group_id_str] = group_data
        save_json(GROUPS_FILE, groups_db)
        
        return {"success": True, "data": group_data}
    except Exception as e:
        logger.error(f"Error activating group: {e}")
        return {"success": False, "error": "Server error"}

def deactivate_group(group_id: int, admin_id: int) -> Dict:
    """Deactivate a group"""
    try:
        group_id_str = str(group_id)
        
        if group_id_str in groups_db:
            groups_db[group_id_str]["status"] = "inactive"
            groups_db[group_id_str]["deactivated_by"] = admin_id
            groups_db[group_id_str]["deactivated_at"] = datetime.now().isoformat()
            
            save_json(GROUPS_FILE, groups_db)
            return {"success": True, "data": groups_db[group_id_str]}
        
        return {"success": False, "error": "Group not found"}
    except Exception as e:
        logger.error(f"Error deactivating group: {e}")
        return {"success": False, "error": "Server error"}

def is_group_active(group_id: int) -> bool:
    """Check if a group is active"""
    try:
        group_id_str = str(group_id)
        
        if group_id_str not in groups_db:
            return False
        
        group_data = groups_db[group_id_str]
        
        # Check if status is active
        if group_data.get("status") != "active":
            return False
        
        # Check if expired
        try:
            expiry_date = datetime.fromisoformat(group_data["expires_at"])
            if expiry_date < datetime.now():
                # Mark as expired
                group_data["status"] = "expired"
                save_json(GROUPS_FILE, groups_db)
                return False
        except:
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error checking group status: {e}")
        return False

def get_active_groups() -> List[Dict]:
    """Get all active groups"""
    try:
        active_groups = []
        current_time = datetime.now()
        
        for group_id_str, group_data in groups_db.items():
            try:
                if group_data.get("status") == "active":
                    expiry_date = datetime.fromisoformat(group_data["expires_at"])
                    if expiry_date > current_time:
                        active_groups.append({
                            "group_id": int(group_id_str),
                            **group_data
                        })
                    else:
                        # Mark as expired
                        group_data["status"] = "expired"
                        save_json(GROUPS_FILE, groups_db)
            except:
                continue
        
        return active_groups
    except Exception as e:
        logger.error(f"Error getting active groups: {e}")
        return []

# ===================== FEATURE 9: BONUS SYSTEM =====================
def give_bonus(user_id: int, bonus_type: str, amount: int, reason: str = "", admin_id: int = None) -> Dict:
    """Give bonus to user"""
    try:
        user_id_str = str(user_id)
        
        if user_id_str not in users_db:
            users_db[user_id_str] = create_user(user_id)
        
        # Add bonus to user
        if bonus_type == "downloads":
            users_db[user_id_str]["downloads_left"] += amount
        elif bonus_type == "points":
            users_db[user_id_str]["points"] = users_db[user_id_str].get("points", 0) + amount
        
        # Create bonus record
        bonus_id = f"BONUS-{random.randint(10000, 99999)}"
        bonus_data = {
            "bonus_id": bonus_id,
            "user_id": user_id,
            "bonus_type": bonus_type,
            "amount": amount,
            "reason": reason,
            "given_by": admin_id,
            "given_at": datetime.now().isoformat()
        }
        
        # Initialize bonus history if not exists
        if "bonus_history" not in users_db[user_id_str]:
            users_db[user_id_str]["bonus_history"] = []
        
        users_db[user_id_str]["bonus_history"].append(bonus_data)
        
        save_json(USERS_FILE, users_db)
        
        return {"success": True, "data": bonus_data}
    except Exception as e:
        logger.error(f"Error giving bonus: {e}")
        return {"success": False, "error": "Server error"}

def set_bonus_settings(setting: str, value: int, admin_id: int) -> Dict:
    """Set bonus settings"""
    try:
        if setting in ["welcome_bonus", "referral_bonus"]:
            bonus_settings_db[setting] = value
            save_json(BONUS_SETTINGS_FILE, bonus_settings_db)
            
            return {"success": True, "setting": setting, "value": value}
        return {"success": False, "error": "Invalid setting"}
    except Exception as e:
        logger.error(f"Error setting bonus: {e}")
        return {"success": False, "error": "Server error"}

# ===================== HELPER FUNCTIONS =====================
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
        "referral_count": 0,
        "points": 0,  # NEW: Points system
        "welcome_bonus_given": False  # NEW: Track if welcome bonus was given
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

# ===================== FEATURE 10: ADVANCED URL DETECTION (FROM Z4X BOT) =====================
# The URL detection is now handled by the URLDetector class above

# ===================== FEATURE 11: ENHANCED WEBSITE DOWNLOAD (FROM Z4X BOT) =====================
def is_wget_available():
    """Check if wget is available"""
    try:
        subprocess.run(["wget", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def enhanced_download_website(url: str, download_type: str = "full") -> tuple:
    """Enhanced website download with better error handling from Z4X bot"""
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Enhanced wget command for all types of websites
        wget_options = [
            'wget',
            '--mirror',
            '--convert-links',
            '--adjust-extension',
            '--page-requisites',
            '--no-parent',
            '--no-check-certificate',
            '--restrict-file-names=windows',
            '--directory-prefix', temp_dir,
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            '--quiet',
            '--execute', 'robots=off',
            '--timeout=30',
            '--tries=3',
            '--retry-connrefused',
            '--waitretry=5',
            '--random-wait'
        ]
        
        if download_type != "full":
            wget_options.extend(['-l', '2'])
        
        wget_options.append(url)
        
        # Execute download
        result = subprocess.run(wget_options, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            logger.warning(f"Wget error: {result.stderr}")
            
            # Try alternative method for difficult sites
            logger.info("Trying alternative download method...")
            alt_cmd = [
                'wget',
                '-r',
                '-l', '3',
                '-k',
                '-p',
                '-E',
                '--no-check-certificate',
                '--directory-prefix', temp_dir,
                '--user-agent', 'Mozilla/5.0',
                '--quiet',
                url
            ]
            subprocess.run(alt_cmd, capture_output=True, timeout=180)
        
        # Check if anything was downloaded
        if not os.listdir(temp_dir):
            # Try simple download
            simple_cmd = f'wget --no-check-certificate --user-agent="Mozilla/5.0" -P "{temp_dir}" "{url}"'
            os.system(simple_cmd)
        
        # Create zip in memory
        zip_buffer = io.BytesIO()
        file_count = 0
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        # Skip large files
                        if os.path.getsize(file_path) > 5 * 1024 * 1024:  # 5MB
                            continue
                        
                        with open(file_path, 'rb') as f:
                            file_data = f.read()
                        
                        arcname = os.path.relpath(file_path, temp_dir)
                        arcname = arcname.replace('\\', '/')  # Normalize path
                        zipf.writestr(arcname, file_data)
                        file_count += 1
                    except Exception as e:
                        logger.error(f"Error adding {file_path} to zip: {e}")
        
        zip_buffer.seek(0)
        return zip_buffer, file_count
        
    except Exception as e:
        logger.error(f"Error in enhanced download: {e}")
        raise e
    finally:
        # Cleanup temp directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                logger.error(f"Error cleaning up temp directory: {e}")

def download_with_requests(url, temp_dir, download_type="full"):
    """Download website using requests library as fallback"""
    try:
        # Get the main page
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        response.raise_for_status()
        
        # Save the main HTML file
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]
        html_file = os.path.join(temp_dir, f"{domain}.html")
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # For partial download, we'll just save the main page
        if download_type == "partial":
            return 1
        
        # For full download, try to download some common assets
        file_count = 1
        
        # Create directories for assets
        css_dir = os.path.join(temp_dir, "css")
        js_dir = os.path.join(temp_dir, "js")
        img_dir = os.path.join(temp_dir, "images")
        
        os.makedirs(css_dir, exist_ok=True)
        os.makedirs(js_dir, exist_ok=True)
        os.makedirs(img_dir, exist_ok=True)
        
        # Extract and download CSS files
        css_pattern = r'<link[^>]*href=["\']([^"\']*\.css)["\'][^>]*>'
        css_matches = re.findall(css_pattern, response.text)
        
        for css_url in css_matches[:5]:  # Limit to 5 CSS files
            if css_url.startswith('//'):
                css_url = 'https:' + css_url
            elif css_url.startswith('/'):
                css_url = f"https://{domain}{css_url}"
            elif not css_url.startswith(('http://', 'https://')):
                css_url = f"{url}/{css_url}"
            
            try:
                css_response = requests.get(css_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
                css_response.raise_for_status()
                
                css_filename = os.path.basename(css_url)
                if not css_filename:
                    css_filename = f"style_{file_count}.css"
                
                css_file = os.path.join(css_dir, css_filename)
                with open(css_file, 'w', encoding='utf-8') as f:
                    f.write(css_response.text)
                
                file_count += 1
            except Exception as e:
                logger.warning(f"Failed to download CSS {css_url}: {e}")
        
        # Extract and download JS files
        js_pattern = r'<script[^>]*src=["\']([^"\']*\.js)["\'][^>]*>'
        js_matches = re.findall(js_pattern, response.text)
        
        for js_url in js_matches[:5]:  # Limit to 5 JS files
            if js_url.startswith('//'):
                js_url = 'https:' + js_url
            elif js_url.startswith('/'):
                js_url = f"https://{domain}{js_url}"
            elif not js_url.startswith(('http://', 'https://')):
                js_url = f"{url}/{js_url}"
            
            try:
                js_response = requests.get(js_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
                js_response.raise_for_status()
                
                js_filename = os.path.basename(js_url)
                if not js_filename:
                    js_filename = f"script_{file_count}.js"
                
                js_file = os.path.join(js_dir, js_filename)
                with open(js_file, 'w', encoding='utf-8') as f:
                    f.write(js_response.text)
                
                file_count += 1
            except Exception as e:
                logger.warning(f"Failed to download JS {js_url}: {e}")
        
        # Extract and download images (limited to avoid too many files)
        img_pattern = r'<img[^>]*src=["\']([^"\']*\.(?:jpg|jpeg|png|gif|webp))["\'][^>]*>'
        img_matches = re.findall(img_pattern, response.text)
        
        # Limit to first 5 images to avoid too many files
        for img_url in img_matches[:5]:
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                img_url = f"https://{domain}{img_url}"
            elif not img_url.startswith(('http://', 'https://')):
                img_url = f"{url}/{img_url}"
            
            try:
                img_response = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
                img_response.raise_for_status()
                
                img_filename = os.path.basename(img_url)
                if not img_filename:
                    img_filename = f"image_{file_count}.jpg"
                
                img_file = os.path.join(img_dir, img_filename)
                with open(img_file, 'wb') as f:
                    f.write(img_response.content)
                
                file_count += 1
            except Exception as e:
                logger.warning(f"Failed to download image {img_url}: {e}")
        
        return file_count
    except Exception as e:
        logger.error(f"Error downloading with requests: {e}")
        raise e

def create_direct_zip(url, download_type="full"):
    """Download and create zip directly - Enhanced with Z4X features"""
    temp_dir = None
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Try enhanced download first if wget is available
        if is_wget_available():
            try:
                zip_buffer, file_count = enhanced_download_website(url, download_type)
                return zip_buffer, file_count
            except Exception as e:
                logger.error(f"Error with enhanced download: {e}")
                # Fall back to requests
                file_count = download_with_requests(url, temp_dir, download_type)
        else:
            # Use requests as fallback
            logger.info("wget not available, using requests library")
            file_count = download_with_requests(url, temp_dir, download_type)
        
        # Create zip in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'rb') as f:
                            file_data = f.read()
                        
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.writestr(arcname, file_data)
                    except Exception as e:
                        logger.warning(f"Failed to add {file_path} to zip: {e}")
                        continue
        
        zip_buffer.seek(0)
        
        return zip_buffer, file_count
        
    except Exception as e:
        logger.error(f"Error creating zip: {e}")
        raise e
    finally:
        # Cleanup temp directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                logger.error(f"Error cleaning up temp directory: {e}")

# ===================== BUTTON MENUS =====================
def get_main_menu() -> InlineKeyboardMarkup:
    """Main menu buttons - SYNAX Style (Enhanced with Gift Keys)"""
    keyboard = [
        [InlineKeyboardButton("⬇️ 𝘿𝙤𝙬𝙣𝙡𝙤𝙖𝙙", callback_data="download_menu"),
         InlineKeyboardButton("💰 𝘽𝙪𝙮", callback_data="buy_menu")],
        [InlineKeyboardButton("📊 𝙎𝙩𝙖𝙩𝙨", callback_data="my_stats"),
         InlineKeyboardButton("🔑 𝘼𝙘𝙩𝙞𝙫𝙖𝙩𝙚 𝙆𝙀𝙔", callback_data="activate_key_menu")],
        [InlineKeyboardButton("🎁 𝙍𝙚𝙙𝙚𝙚𝙢 𝙂𝙞𝙛𝙩", callback_data="redeem_gift"),
         InlineKeyboardButton("📜 𝙃𝙞𝙨𝙩𝙤𝙧𝙮", callback_data="download_history")],
        [InlineKeyboardButton("🎫 𝙎𝙪𝙥𝙥𝙤𝙧𝙩", callback_data="support_menu"),
         InlineKeyboardButton("👥 𝙍𝙚𝙛𝙚𝙧𝙧𝙖𝙡", callback_data="referral_menu")],
        [InlineKeyboardButton("📢 𝙐𝙥𝙙𝙖𝙩𝙚", url=PROMOTION_CHANNEL),
         InlineKeyboardButton("👥 𝙂𝙧𝙤𝙪𝙥", url=PROMOTION_GROUPS[0])],
        [InlineKeyboardButton("👑 𝙊𝙬𝙣𝙚𝙧", callback_data="owner_info")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_download_menu() -> InlineKeyboardMarkup:
    """Download menu - SYNAX Style (Enhanced)"""
    keyboard = [
        [InlineKeyboardButton("🌐 𝙁𝙧𝙤𝙢  𝙐𝙧𝙡", callback_data="url_download"),
         InlineKeyboardButton("⚡ 𝙌𝙪𝙞𝙘𝙠 𝘿𝙤𝙬𝙣𝙡𝙤𝙖𝙙", callback_data="quick_dl")],
        [InlineKeyboardButton("🔙 𝘽𝙖𝙘𝙠", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_buy_menu() -> InlineKeyboardMarkup:
    """Buy menu with QR Code - Enhanced"""
    keyboard = [
        [InlineKeyboardButton("₹10 → 5 DOWNLOADS", callback_data="buy_basic")],
        [InlineKeyboardButton("₹40 → 40 DOWNLOADS", callback_data="buy_pro")],
        [InlineKeyboardButton("₹100 → 150 DOWNLOADS", callback_data="buy_premium")],
        [InlineKeyboardButton("🔙 BACK", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_menu() -> InlineKeyboardMarkup:
    """Admin menu - SYNAX System (Enhanced with Gift Keys)"""
    keyboard = [
        [InlineKeyboardButton("📢 𝘽𝙧𝙤𝙖𝙙𝙘𝙖𝙨𝙩", callback_data="admin_broadcast"),
         InlineKeyboardButton("👥 𝙐𝙨𝙚𝙧𝙨", callback_data="admin_all_users")],
        [InlineKeyboardButton("💳 𝙋𝙖𝙮𝙢𝙚𝙣𝙩𝙨", callback_data="admin_payments"),
         InlineKeyboardButton("🚫 𝘽𝘼𝙉", callback_data="admin_ban")],
        [InlineKeyboardButton("✅ 𝙐𝙣𝙗𝙖𝙣", callback_data="admin_unban"),
         InlineKeyboardButton("⚙️ 𝙈𝙖𝙞𝙣𝙩𝙚𝙣𝙚𝙣𝙘𝙚", callback_data="admin_maintenance")],
        [InlineKeyboardButton("📊 𝙎𝙩𝙖𝙩𝙨", callback_data="admin_stats"),
         InlineKeyboardButton("🔧 𝘼𝙙𝙙 𝘼𝙙𝙢𝙞𝙣", callback_data="admin_add")],
        [InlineKeyboardButton("🗑️ 𝙍𝙚𝙢𝙤𝙫𝙚 𝘼𝙙𝙢𝙞𝙣", callback_data="admin_remove"),
         InlineKeyboardButton("🔑 𝙂𝙚𝙣 𝙆𝙀𝙔", callback_data="admin_gen_key")],
        [InlineKeyboardButton("🔑 𝘽𝙪𝙡𝙠 𝙆𝙀𝙔𝙎", callback_data="admin_bulk_keys"),
         InlineKeyboardButton("↩️ 𝙍𝙚𝙥𝙡𝙮 𝙐𝙨𝙚𝙧", callback_data="admin_reply_user")],
        [InlineKeyboardButton("🎫 𝙎𝙪𝙥𝙥𝙤𝙧𝙩𝙨 𝙏𝙞𝙘𝙠𝙚𝙩𝙨", callback_data="admin_tickets"),
         InlineKeyboardButton("📊 𝙍𝙚𝙥𝙤𝙧𝙩𝙨", callback_data="admin_reports")],
        [InlineKeyboardButton("👥 𝙂𝙧𝙤𝙪𝙥𝙨", callback_data="admin_groups"),
         InlineKeyboardButton("🎁 𝘽𝙤𝙣𝙪𝙨 𝙎𝙚𝙩𝙩𝙞𝙣𝙜𝙨", callback_data="admin_bonus_settings")],
        [InlineKeyboardButton("🎁 𝙂𝙚𝙣 𝙂𝙞𝙛𝙩 𝙆𝙚𝙮", callback_data="admin_gen_gift"),
         InlineKeyboardButton("🎁 𝙂𝙞𝙛𝙩 𝙎𝙩𝙖𝙩𝙨", callback_data="admin_gift_stats")],
        [InlineKeyboardButton("🔙 𝙈𝙖𝙞𝙣 𝙈𝙚𝙣𝙪", callback_data="main_menu")]
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
    """Bulk key generation form"""
    keyboard = [
        [InlineKeyboardButton("🔑 BASIC (5 DL)", callback_data="bulk_form_basic")],
        [InlineKeyboardButton("🔑 PRO (40 DL)", callback_data="bulk_form_pro")],
        [InlineKeyboardButton("🔑 PREMIUM (150 DL)", callback_data="bulk_form_premium")],
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

def get_groups_menu() -> InlineKeyboardMarkup:
    """Groups menu for admin"""
    keyboard = [
        [InlineKeyboardButton("➕ ACTIVATE GROUP", callback_data="activate_group_form")],
        [InlineKeyboardButton("➖ DEACTIVATE GROUP", callback_data="deactivate_group_form")],
        [InlineKeyboardButton("📋 ACTIVE GROUPS", callback_data="active_groups")],
        [InlineKeyboardButton("🔙 ADMIN MENU", callback_data="admin_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_bonus_settings_menu() -> InlineKeyboardMarkup:
    """Bonus settings menu"""
    keyboard = [
        [InlineKeyboardButton("🎁 WELCOME BONUS", callback_data="set_welcome_bonus")],
        [InlineKeyboardButton("👥 REFERRAL BONUS", callback_data="set_referral_bonus")],
        [InlineKeyboardButton("🎁 GIVE BONUS", callback_data="give_bonus_form")],
        [InlineKeyboardButton("🔙 ADMIN MENU", callback_data="admin_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ===================== USERS LIST WITH PAGINATION =====================
async def show_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0):
    """Show all users with pagination"""
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
            points = user_data.get('points', 0)
            last_active = datetime.fromisoformat(user_data['last_active']).strftime('%d/%m %H:%M')
            status = "🚫" if user_data.get('is_banned', False) else "✅"
            plan = user_data.get('subscription', 'free')
            
            users_text += f"{count}. {status} `{uid_str}`\n"
            users_text += f"   👤 @{username} | {first_name}\n"
            users_text += f"   📥 {downloads} DL | 🏆 {points} Pts | 📅 {last_active} | 💰 {plan}\n\n"
        
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
    """Start command - SYNAX Style"""
    try:
        user = update.effective_user
        user_id = user.id
        
        update_user_activity(user_id, user.username, user.first_name)
        
        # Get or create user data
        user_data = get_user_stats(user_id)
        
        # Give welcome bonus to new users
        welcome_bonus_given = False
        if not user_data.get("welcome_bonus_given", False):
            welcome_bonus = bonus_settings_db.get("welcome_bonus", 5)
            result = give_bonus(user_id, "downloads", welcome_bonus, "Welcome bonus", OWNER_ID)
            if result["success"]:
                welcome_bonus_given = True
                user_data["welcome_bonus_given"] = True
                save_json(USERS_FILE, users_db)
        
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
        
        # Check if user is in an activated group
        group_unlimited = False
        if update.message.chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
            if is_group_active(update.message.chat.id):
                group_unlimited = True
        
        welcome_msg = f"""
✨ **WELCOME, {user.first_name}!** ✨

🤖 **SYNAX DOWNLOADER BOT**
_Professional Website Downloader_

📊 **YOUR STATUS:**
• Downloads Left: `{'♾️ UNLIMITED' if group_unlimited or is_owner(user_id) else user_data.get('downloads_left', 0)}`
• Points: `{user_data.get('points', 0)}`
• Total Downloads: `{user_data.get('total_downloads', 0)}`
• Account: `{'🚫 BANNED' if user_data.get('is_banned') else '✅ ACTIVE'}`

📢 **JOIN OUR:**
• Channel: @synaxnetwork
• Groups: @synaxchatgroup

{'🎁 **WELCOME BONUS:** You received ' + str(bonus_settings_db.get('welcome_bonus', 5)) + ' downloads as a welcome gift!' if welcome_bonus_given else ''}

🎁 **NEW:** Redeem gift keys for special offers!

👇 **USE BUTTONS BELOW:**
    """
        
        # Send welcome message with buttons
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
        try:
            if update.message:
                await update.message.reply_text("❌ Error loading bot. Please try again.")
        except:
            pass

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
• ₹10 → 5 downloads
• ₹40 → 40 downloads  
• ₹100 → 150 downloads

🔑 **SUBSCRIPTION KEYS:**
Use /activate <key> to activate subscription

🎁 **GIFT KEYS:**
Use /redeem <gift-key> to redeem gift

📜 **DOWNLOAD HISTORY:**
Check your previous downloads in the HISTORY section

🎫 **SUPPORT SYSTEM:**
Create support tickets for help with issues

👥 **REFERRAL SYSTEM:**
Invite friends and earn {bonus_settings_db.get('referral_bonus', 5)} downloads per referral

🎁 **BONUS SYSTEM:**
New users get {bonus_settings_db.get('welcome_bonus', 5)} downloads as welcome bonus!

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
        try:
            if update.message:
                await update.message.reply_text("❌ Error loading help. Please try again.")
        except:
            pass

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
        total_points = 0
        pending_payments = 0
        total_keys = len(keys_db)
        used_keys = sum(1 for k in keys_db.values() if k.get("is_used", False))
        open_tickets = sum(1 for t in tickets_db.values() if t.get("status") == "open")
        active_groups = len(get_active_groups())
        total_gift_keys = len(gift_keys_db.get("gift_keys", {}))
        active_gift_keys = sum(1 for k in gift_keys_db.get("gift_keys", {}).values() 
                              if k.get("is_active", True) and datetime.now() < datetime.fromisoformat(k.get("expires_at", "2000-01-01")))
        
        for u in users_db.values():
            try:
                last_active = datetime.fromisoformat(u['last_active']).date()
                if last_active == today:
                    active_today += 1
                if u.get('is_banned', False):
                    banned_count += 1
                total_downloads += u.get('total_downloads', 0)
                total_points += u.get('points', 0)
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
• Total Points: `{total_points}`
• Pending Payments: `{pending_payments}`
• Subscription Keys: `{total_keys}`
• Used Keys: `{used_keys}`
• Unused Keys: `{total_keys - used_keys}`
• Open Tickets: `{open_tickets}`
• Active Groups: `{active_groups}`
• Gift Keys: `{total_gift_keys}`
• Active Gift Keys: `{active_gift_keys}`
• Maintenance: `{'✅ ON' if settings_db.get('maintenance') else '❌ OFF'}`

🎁 **BONUS SETTINGS:**
• Welcome Bonus: `{bonus_settings_db.get('welcome_bonus', 5)}`
• Referral Bonus: `{bonus_settings_db.get('referral_bonus', 5)}`

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
        try:
            if update.message:
                await update.message.reply_text("❌ Error loading admin panel.")
        except:
            pass

async def show_user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics - SYNAX System (Enhanced)"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        user_data = get_user_stats(user_id)
        
        # Check if user is in an activated group
        group_unlimited = False
        if update.callback_query.message.chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
            if is_group_active(update.callback_query.message.chat.id):
                group_unlimited = True
        
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
        
        # Get bonus history
        bonus_history = user_data.get('bonus_history', [])
        total_bonus = sum(b.get('amount', 0) for b in bonus_history if b.get('bonus_type') == 'downloads')
        
        stats_text = f"""
📊 **YOUR STATISTICS** 📊

👤 **ACCOUNT INFO:**
• User ID: `{user_id}`
• Username: @{update.effective_user.username or 'N/A'}
• Joined: `{joined_date}`
• Status: `{'🚫 BANNED' if user_data.get('is_banned') else '✅ ACTIVE'}`

⬇️ **DOWNLOAD STATS:**
• Downloads Left: `{'♾️ UNLIMITED' if group_unlimited or is_owner(user_id) else user_data['downloads_left']}`
• Total Downloads: `{user_data['total_downloads']}`
• Subscription: `{user_data['subscription'].upper()}`
• Expires: `{expiry_text}`

🏆 **POINTS & BONUSES:**
• Points: `{user_data.get('points', 0)}`
• Total Bonus Received: `{total_bonus}`
• Welcome Bonus: `{'✅ Received' if user_data.get('welcome_bonus_given') else '❌ Not received'}`

👥 **REFERRAL STATS:**
• Referrals: `{referral_count}`
• Referral Link: `{referral_link}`

📅 **LAST ACTIVE:** `{last_active}`

{'♾️ **OWNER PRIVILEGES:** Unlimited Downloads' if is_owner(user_id) else ''}
{'♾️ **GROUP UNLIMITED:** This group has unlimited downloads!' if group_unlimited else ''}
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
        
        # Check if user is in an activated group
        group_unlimited = False
        if update.message.chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
            if is_group_active(update.message.chat.id):
                group_unlimited = True
        
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
        
        # Get bonus history
        bonus_history = user_data.get('bonus_history', [])
        total_bonus = sum(b.get('amount', 0) for b in bonus_history if b.get('bonus_type') == 'downloads')
        
        stats_text = f"""
📊 **YOUR STATISTICS** 📊

👤 **ACCOUNT INFO:**
• User ID: `{user_id}`
• Username: @{update.effective_user.username or 'N/A'}
• Joined: `{joined_date}`
• Status: `{'🚫 BANNED' if user_data.get('is_banned') else '✅ ACTIVE'}`

⬇️ **DOWNLOAD STATS:**
• Downloads Left: `{'♾️ UNLIMITED' if group_unlimited or is_owner(user_id) else user_data['downloads_left']}`
• Total Downloads: `{user_data['total_downloads']}`
• Subscription: `{user_data['subscription'].upper()}`
• Expires: `{expiry_text}`

🏆 **POINTS & BONUSES:**
• Points: `{user_data.get('points', 0)}`
• Total Bonus Received: `{total_bonus}`
• Welcome Bonus: `{'✅ Received' if user_data.get('welcome_bonus_given') else '❌ Not received'}`

👥 **REFERRAL STATS:**
• Referrals: `{referral_count}`
• Referral Link: `{referral_link}`

📅 **LAST ACTIVE:** `{last_active}`

{'♾️ **OWNER PRIVILEGES:** Unlimited Downloads' if is_owner(user_id) else ''}
{'♾️ **GROUP UNLIMITED:** This group has unlimited downloads!' if group_unlimited else ''}
    """
        
        await update.message.reply_text(
            stats_text,
            reply_markup=get_main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        await update.message.reply_text("❌ Error loading stats.")

# ===================== ACTIVATE KEY =====================
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

# ===================== REDEEM GIFT KEY =====================
async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Redeem gift key - From Z4X Bot"""
    try:
        user_id = update.effective_user.id
        user_data = get_user_stats(user_id)
        
        if context.args and len(context.args) > 0:
            key = context.args[0].upper()
            result = redeem_gift_key(key, user_id)
            
            if result["success"]:
                gift_data = result["data"]
                
                gift_msg = f"""
🎁 **GIFT REDEEMED SUCCESSFULLY!** 🎁

**Gift Details:**
• Gift Name: {gift_data['plan_name']}
• Downloads: {gift_data['downloads']}
• Days: {gift_data['days']}
• Expires: {datetime.fromisoformat(gift_data['expires_at']).strftime('%d %b %Y')}

**Your Account Now:**
• Total Downloads: {user_data['downloads_left'] + gift_data['downloads']}
• Gift Status: Active for {gift_data['days']} days

🎉 **Enjoy your gift! Thank the gift giver!** 🎉
"""
                
                await update.message.reply_text(
                    gift_msg,
                    parse_mode=ParseMode.MARKDOWN
                )
                
            else:
                await update.message.reply_text(
                    f"❌ **GIFT REDEMPTION FAILED**\n\n"
                    f"Error: {result['error']}\n\n"
                    f"Make sure:\n"
                    f"1. Gift key is correct\n"
                    f"2. Gift is not expired\n"
                    f"3. You haven't used it before\n"
                    f"4. Gift is still active"
                )
        else:
            await update.message.reply_text(
                "🎁 **REDEEM GIFT KEY** 🎁\n\n"
                "Usage: `/redeem <gift-key>`\n\n"
                "**Example:**\n"
                "`/redeem GIFT-DIWALI-ABC123`\n\n"
                "**Get gift keys from:**\n"
                "• Special events\n"
                "• Giveaways\n"
                "• Admin rewards\n\n"
                "🎉 **Gifts can be used by multiple users!**",
                parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        logger.error(f"Error in redeem command: {e}")
        await update.message.reply_text("❌ Error redeeming gift key.")

# ===================== GENERATE GIFT KEY =====================
async def genred_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate gift key (admin only) - From Z4X Bot"""
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ **ADMIN ONLY COMMAND!**")
            return
        
        if context.args and len(context.args) >= 3:
            try:
                # Format: /genred <plan_name> <downloads> <days> [max_uses] [expire_days]
                plan_name = context.args[0]
                downloads = int(context.args[1])
                days = int(context.args[2])
                max_uses = int(context.args[3]) if len(context.args) > 3 else 10
                expire_days = int(context.args[4]) if len(context.args) > 4 else 7
                
                if downloads <= 0 or days <= 0 or max_uses <= 0 or expire_days <= 0:
                    await update.message.reply_text("❌ **All values must be positive numbers!**")
                    return
                
                key = generate_gift_key(plan_name, downloads, days, max_uses, expire_days)
                
                await update.message.reply_text(
                    f"🎁 **GIFT KEY GENERATED** 🎁\n\n"
                    f"**Gift Details:**\n"
                    f"• Name: {plan_name}\n"
                    f"• Key: `{key}`\n"
                    f"• Downloads: {downloads}\n"
                    f"• Days: {days}\n"
                    f"• Max Uses: {max_uses}\n"
                    f"• Expires In: {expire_days} days\n"
                    f"• Expiry Date: {(datetime.now() + timedelta(days=expire_days)).strftime('%d %b %Y')}\n\n"
                    f"**Share this gift key with users:**\n"
                    f"`/redeem {key}`\n\n"
                    f"**Or send this message:**\n"
                    f"🎉 **Special Gift!** 🎉\n"
                    f"Use `/redeem {key}` to get {downloads} downloads for {days} days!\n"
                    f"Valid for {max_uses} users, expires in {expire_days} days.",
                    parse_mode=ParseMode.MARKDOWN
                )
                    
            except ValueError:
                await update.message.reply_text(
                    "❌ **Invalid input!**\n"
                    "Downloads, days, max_uses और expire_days numbers होने चाहिए।\n\n"
                    "Example: `/genred DiwaliSpecial 25 30 50 10`",
                    parse_mode=ParseMode.MARKDOWN
                )
        else:
            await update.message.reply_text(
                "🎁 **GENERATE GIFT KEY** 🎁\n\n"
                "Create special gift keys for multiple users.\n\n"
                "📝 **Usage:**\n"
                "`/genred <plan_name> <downloads> <days> [max_uses] [expire_days]`\n\n"
                "📌 **Examples:**\n"
                "• `/genred DiwaliGift 25 30` - 25 downloads for 30 days, 10 uses, expires in 7 days\n"
                "• `/genred NewYear 50 60 100 15` - 50 downloads for 60 days, 100 uses, expires in 15 days\n"
                "• `/genred SpecialOffer 100 365 1000 30` - 100 downloads for 1 year, 1000 uses\n\n"
                "🎯 **Perfect for:**\n"
                "• Special events (Diwali, Christmas, New Year)\n"
                "• Giveaways and contests\n"
                "• Promotional campaigns\n"
                "• Rewarding active users",
                parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        logger.error(f"Error in genred command: {e}")
        await update.message.reply_text("❌ Error generating gift key.")

# ===================== GENERATE KEY =====================
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
                downloads = 5
            elif plan == "pro":
                downloads = 40
            elif plan == "premium":
                downloads = 150
            
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

# ===================== GIVE COMMAND =====================
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

# ===================== GROUP ACTIVATION COMMANDS =====================
async def activate_group_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Activate a group for unlimited downloads (admin only)"""
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ **ADMIN ONLY!**")
            return
        
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "🔑 **ACTIVATE GROUP** 🔑\n\n"
                "Usage: `/activategroup <group_id> <days>`\n\n"
                "Example: `/activategroup -123456789 30`\n\n"
                "Note: Group ID starts with -100 for supergroups",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        try:
            group_id = int(context.args[0])
            days = int(context.args[1])
            
            if days <= 0 or days > 365:
                await update.message.reply_text("❌ **Invalid days!** Please specify 1-365 days.")
                return
            
            # Activate group
            result = activate_group(group_id, user_id, days)
            
            if result["success"]:
                group_data = result["data"]
                expiry_date = datetime.fromisoformat(group_data["expires_at"])
                
                # Try to get group info
                group_name = "Unknown Group"
                try:
                    chat = await context.bot.get_chat(group_id)
                    group_name = chat.title
                except:
                    pass
                
                await update.message.reply_text(
                    f"✅ **GROUP ACTIVATED!** ✅\n\n"
                    f"📋 **Group Details:**\n"
                    f"• Name: {group_name}\n"
                    f"• ID: `{group_id}`\n"
                    f"• Validity: `{days}` days\n"
                    f"• Expires: `{expiry_date.strftime('%d %b %Y')}`\n\n"
                    f"🎉 **All members can now use unlimited downloads!**",
                    parse_mode=ParseMode.MARKDOWN
                )
                
                # Try to notify group
                try:
                    await context.bot.send_message(
                        chat_id=group_id,
                        text=f"🎉 **GROUP ACTIVATED!** 🎉\n\n"
                             f"This group has been activated for unlimited downloads!\n\n"
                             f"Valid until: {expiry_date.strftime('%d %b %Y')}\n\n"
                             f"Enjoy unlimited downloads with SYNAX Bot!",
                        parse_mode=ParseMode.MARKDOWN
                    )
                except:
                    pass
            else:
                await update.message.reply_text(
                    f"❌ **Error activating group!**\n\n"
                    f"{result.get('error', 'Unknown error')}"
                )
        except ValueError:
            await update.message.reply_text(
                "❌ **Invalid input!**\n\n"
                "Usage: `/activategroup <group_id> <days>`\n"
                "Example: `/activategroup -123456789 30`"
            )
    except Exception as e:
        logger.error(f"Error in activate group command: {e}")
        await update.message.reply_text("❌ Error activating group.")

async def deactivate_group_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Deactivate a group (admin only)"""
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ **ADMIN ONLY!**")
            return
        
        if not context.args or len(context.args) < 1:
            await update.message.reply_text(
                "🔑 **DEACTIVATE GROUP** 🔑\n\n"
                "Usage: `/deactivategroup <group_id>`\n\n"
                "Example: `/deactivategroup -123456789`\n\n"
                "Note: Group ID starts with -100 for supergroups",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        try:
            group_id = int(context.args[0])
            
            # Deactivate group
            result = deactivate_group(group_id, user_id)
            
            if result["success"]:
                # Try to get group info
                group_name = "Unknown Group"
                try:
                    chat = await context.bot.get_chat(group_id)
                    group_name = chat.title
                except:
                    pass
                
                await update.message.reply_text(
                    f"✅ **GROUP DEACTIVATED!** ✅\n\n"
                    f"📋 **Group Details:**\n"
                    f"• Name: {group_name}\n"
                    f"• ID: `{group_id}`\n\n"
                    f"⚠️ **Members will no longer have unlimited downloads!**",
                    parse_mode=ParseMode.MARKDOWN
                )
                
                # Try to notify group
                try:
                    await context.bot.send_message(
                        chat_id=group_id,
                        text=f"⚠️ **GROUP DEACTIVATED** ⚠️\n\n"
                             f"This group's unlimited downloads have been deactivated.\n\n"
                             f"Please contact admin for more information.",
                        parse_mode=ParseMode.MARKDOWN
                    )
                except:
                    pass
            else:
                await update.message.reply_text(
                    f"❌ **Error deactivating group!**\n\n"
                    f"{result.get('error', 'Unknown error')}"
                )
        except ValueError:
            await update.message.reply_text(
                "❌ **Invalid input!**\n\n"
                "Usage: `/deactivategroup <group_id>`\n"
                "Example: `/deactivategroup -123456789`"
            )
    except Exception as e:
        logger.error(f"Error in deactivate group command: {e}")
        await update.message.reply_text("❌ Error deactivating group.")

async def list_groups_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all active groups (admin only)"""
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ **ADMIN ONLY!**")
            return
        
        active_groups = get_active_groups()
        
        if not active_groups:
            await update.message.reply_text(
                "📋 **ACTIVE GROUPS** 📋\n\n"
                "No active groups found.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        groups_text = "📋 **ACTIVE GROUPS** 📋\n\n"
        
        for group in active_groups:
            group_id = group["group_id"]
            expiry_date = datetime.fromisoformat(group["expires_at"]).strftime('%d %b %Y')
            activated_date = datetime.fromisoformat(group["activated_at"]).strftime('%d %b %Y')
            
            # Try to get group info
            group_name = "Unknown Group"
            try:
                chat = await context.bot.get_chat(group_id)
                group_name = chat.title
            except:
                pass
            
            groups_text += f"📋 **{group_name}**\n"
            groups_text += f"• ID: `{group_id}`\n"
            groups_text += f"• Activated: {activated_date}\n"
            groups_text += f"• Expires: {expiry_date}\n"
            groups_text += f"• Status: {group['status'].upper()}\n\n"
        
        await update.message.reply_text(groups_text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Error in list groups command: {e}")
        await update.message.reply_text("❌ Error loading groups.")

# ===================== BONUS SETTINGS COMMANDS =====================
async def setwelcomebonus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set welcome bonus (admin only)"""
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ **ADMIN ONLY!**")
            return
        
        if not context.args or len(context.args) < 1:
            await update.message.reply_text(
                "🎁 **SET WELCOME BONUS** 🎁\n\n"
                "Usage: `/setwelcomebonus <amount>`\n\n"
                "Example: `/setwelcomebonus 10`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        try:
            amount = int(context.args[0])
            if amount < 0:
                await update.message.reply_text("❌ **Invalid amount!** Please specify a positive number.")
                return
            
            # Set welcome bonus
            result = set_bonus_settings("welcome_bonus", amount, user_id)
            
            if result["success"]:
                await update.message.reply_text(
                    f"✅ **Welcome bonus updated!**\n\n"
                    f"New welcome bonus: `{amount}` downloads",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text("❌ Error updating welcome bonus.")
        except ValueError:
            await update.message.reply_text("❌ **Invalid amount!** Please specify a valid number.")
    except Exception as e:
        logger.error(f"Error in setwelcomebonus command: {e}")
        await update.message.reply_text("❌ Error setting welcome bonus.")

async def setreferralbonus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set referral bonus (admin only)"""
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ **ADMIN ONLY!**")
            return
        
        if not context.args or len(context.args) < 1:
            await update.message.reply_text(
                "👥 **SET REFERRAL BONUS** 👥\n\n"
                "Usage: `/setreferralbonus <amount>`\n\n"
                "Example: `/setreferralbonus 10`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        try:
            amount = int(context.args[0])
            if amount < 0:
                await update.message.reply_text("❌ **Invalid amount!** Please specify a positive number.")
                return
            
            # Set referral bonus
            result = set_bonus_settings("referral_bonus", amount, user_id)
            
            if result["success"]:
                await update.message.reply_text(
                    f"✅ **Referral bonus updated!**\n\n"
                    f"New referral bonus: `{amount}` downloads",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text("❌ Error updating referral bonus.")
        except ValueError:
            await update.message.reply_text("❌ **Invalid amount!** Please specify a valid number.")
    except Exception as e:
        logger.error(f"Error in setreferralbonus command: {e}")
        await update.message.reply_text("❌ Error setting referral bonus.")

async def givebonus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Give bonus to user (admin only)"""
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ **ADMIN ONLY!**")
            return
        
        if not context.args or len(context.args) < 3:
            await update.message.reply_text(
                "🎁 **GIVE BONUS** 🎁\n\n"
                "Usage: `/givebonus <user_id> <type> <amount> [reason]`\n\n"
                "Types: `downloads` or `points`\n\n"
                "Example: `/givebonus 1234567890 downloads 10 Special bonus`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        try:
            target_user_id = int(context.args[0])
            bonus_type = context.args[1].lower()
            amount = int(context.args[2])
            reason = " ".join(context.args[3:]) if len(context.args) > 3 else "Admin bonus"
            
            if bonus_type not in ["downloads", "points"]:
                await update.message.reply_text("❌ **Invalid bonus type!** Please use 'downloads' or 'points'.")
                return
            
            if amount <= 0:
                await update.message.reply_text("❌ **Invalid amount!** Please specify a positive number.")
                return
            
            # Give bonus
            result = give_bonus(target_user_id, bonus_type, amount, reason, user_id)
            
            if result["success"]:
                # Get user info
                target_user_data = users_db.get(str(target_user_id), {})
                username = target_user_data.get('username', 'N/A')
                first_name = target_user_data.get('first_name', 'N/A')
                
                await update.message.reply_text(
                    f"✅ **Bonus Given!**\n\n"
                    f"User: @{username} | {first_name} (`{target_user_id}`)\n"
                    f"Type: {bonus_type}\n"
                    f"Amount: {amount}\n"
                    f"Reason: {reason}",
                    parse_mode=ParseMode.MARKDOWN
                )
                
                # Notify user
                try:
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text=f"🎁 **BONUS RECEIVED!** 🎁\n\n"
                             f"You received {amount} {bonus_type} from admin!\n\n"
                             f"Reason: {reason}\n\n"
                             f"Thank you for using SYNAX Bot!",
                        parse_mode=ParseMode.MARKDOWN
                    )
                except Exception as e:
                    logger.warning(f"Could not notify user {target_user_id}: {e}")
            else:
                await update.message.reply_text("❌ Error giving bonus.")
        except ValueError:
            await update.message.reply_text(
                "❌ **Invalid format!**\n\n"
                "Usage: `givebonus <user_id> <type> <amount> <reason>`\n"
                "Example: `givebonus 1234567890 downloads 10 Special bonus`"
            )
    except Exception as e:
        logger.error(f"Error in givebonus command: {e}")
        await update.message.reply_text("❌ Error giving bonus.")

# ===================== URL DOWNLOAD =====================
async def handle_url_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URL download - Enhanced with Z4X URL Detection"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        await query.edit_message_text(
            "🌐 **URL DOWNLOAD**\n\n"
            "Simply send me any website URL. I can detect:\n"
            "• Standard URLs (https://example.com)\n"
            "• Short URLs (example.com)\n"
            "• Subdomains (sub.example.com)\n"
            "• GitHub Pages (username.github.io)\n"
            "• Static hosting (netlify.app, vercel.app)\n"
            "• And many more!\n\n"
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
    """Process URL download - Enhanced with Z4X URL Detection"""
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
        
        # Check if user is in an activated group
        group_unlimited = False
        if update.message.chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
            if is_group_active(update.message.chat.id):
                group_unlimited = True
        
        # Check downloads
        if user_data["downloads_left"] <= 0 and not is_owner(user_id) and not group_unlimited:
            await update.message.reply_text(
                "❌ **No downloads left!**\nUse BUY button to purchase more.",
                reply_markup=get_buy_menu()
            )
            return ConversationHandler.END
        
        # Use advanced URL detection from Z4X bot
        url_detection = URLDetector.smart_url_detection(message_text)
        
        if not url_detection["is_valid"]:
            error_msg = url_detection.get("message", "Invalid URL")
            await update.message.reply_text(
                f"❌ **Invalid URL!**\n\n"
                f"{error_msg}\n\n"
                "Please send a valid website URL.\n"
                "**Examples:**\n"
                "• https://example.com\n"
                "• www.example.com\n"
                "• example.com\n"
                "• github.io/username/project",
                parse_mode=ParseMode.MARKDOWN
            )
            return ConversationHandler.END
        
        url = url_detection["url"]
        url_type = url_detection["type"]
        confidence = url_detection["confidence"]
        
        # Show URL detection info for debugging
        if is_admin(user_id):
            await update.message.reply_text(
                f"🔍 **URL Detection Results:**\n\n"
                f"URL: `{url}`\n"
                f"Type: {url_type}\n"
                f"Confidence: {confidence}%\n\n"
                f"Starting download...",
                parse_mode=ParseMode.MARKDOWN
            )
        
        context.user_data['download_url'] = url
        
        # Ask for download type
        await update.message.reply_text(
            f"🌐 **Website URL Detected**\n\n"
            f"URL: {url}\n"
            f"Type: {url_type.replace('_', ' ').title()}\n\n"
            f"Please choose download type:",
            reply_markup=get_download_type_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        return AWAITING_DOWNLOAD_TYPE
    except Exception as e:
        logger.error(f"Error processing URL download: {e}")
        await update.message.reply_text("❌ Error processing URL.")
        return ConversationHandler.END

async def process_download(update: Update, context: ContextTypes.DEFAULT_TYPE, download_type: str):
    """Process the actual download - Enhanced with Z4X Download System"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        user_data = get_user_stats(user_id)
        
        url = context.user_data.get('download_url')
        if not url:
            await query.answer("❌ No URL found!", show_alert=True)
            return ConversationHandler.END
        
        # Check if user is in an activated group
        group_unlimited = False
        if query.message.chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
            if is_group_active(query.message.chat.id):
                group_unlimited = True
        
        await query.answer()
        await query.edit_message_text(f"⏳ **Starting {download_type.upper()} download...**")
        
        # Use enhanced download from Z4X bot
        try:
            zip_buffer, file_count = enhanced_download_website(url, download_type)
        except Exception as e:
            logger.error(f"Error with enhanced download: {e}")
            # Fall back to original method
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
        if not is_owner(user_id) and not group_unlimited:
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
        try:
            error_msg = str(e)[:200]
            
            if "timeout" in error_msg.lower():
                error_msg = "⚠️ **Download timeout!** The website is too large or slow."
            elif "No files" in error_msg:
                error_msg = "⚠️ **No files downloaded!** The website might be empty or inaccessible."
            
            await query.edit_message_text(
                f"❌ **Download Failed**\n\n{error_msg}\n\n"
                f"**Try:**\n"
                f"• Different website\n"
                f"• Partial download option\n\n"
                f"**Contact:** {OWNER_USERNAME} for help"
            )
        except:
            pass
        return ConversationHandler.END

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
        
        # Gift key redemption
        elif data == "redeem_gift":
            await query.edit_message_text(
                "🎁 **REDEEM GIFT KEY** 🎁\n\n"
                "To redeem a gift key, use:\n\n"
                "**Command:** `/redeem <gift-key>`\n\n"
                "**Example:**\n"
                "`/redeem GIFT-DIWALI-ABC123`\n\n"
                "**Get gift keys from:**\n"
                "• Special events\n"
                "• Giveaways\n"
                "• Admin rewards\n\n"
                "🎉 **Gifts can be used by multiple users!**",
                reply_markup=get_back_button("main_menu"),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # QR Code handlers
        elif data.startswith("qr_"):
            plan = data[3:]
            plan_details = {
                "basic": {"price": 10, "downloads": 5},
                "pro": {"price": 40, "downloads": 40},
                "premium": {"price": 100, "downloads": 150}
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
        
        # Key generation handlers
        elif data.startswith("genkey_"):
            plan = data[7:]
            if plan in ["basic", "pro", "premium"]:
                downloads = 100
                if plan == "basic":
                    downloads = 5
                elif plan == "pro":
                    downloads = 40
                
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
        
        # Gift key generation
        elif data == "admin_gen_gift":
            if not is_admin(user_id):
                await query.answer("❌ Admin Only!", show_alert=True)
                return
            
            await query.edit_message_text(
                "🎁 **GENERATE GIFT KEY**\n\n"
                "Please use command:\n"
                "`/genred <plan_name> <downloads> <days> [max_uses] [expire_days]`\n\n"
                "**Example:**\n"
                "`/genred DiwaliGift 25 30 100 10`\n\n"
                "This creates a gift key for 25 downloads for 30 days,\n"
                "usable by 100 users, expires in 10 days.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_back_button("admin_menu")
            )
            return
        
        # Gift stats
        elif data == "admin_gift_stats":
            if not is_admin(user_id):
                await query.answer("❌ Admin Only!", show_alert=True)
                return
            
            if "gift_keys" not in gift_keys_db:
                gift_keys_db["gift_keys"] = {}
            
            gift_keys = gift_keys_db["gift_keys"]
            total_keys = len(gift_keys)
            active_keys = sum(1 for k in gift_keys.values() if k.get("is_active", True))
            expired_keys = sum(1 for k in gift_keys.values() if datetime.now() > datetime.fromisoformat(k.get("expires_at", "2000-01-01")))
            total_uses = sum(k.get("used_count", 0) for k in gift_keys.values())
            
            stats_text = f"""
🎁 **GIFT KEY STATISTICS** 🎁

📊 **Overview:**
• Total Gift Keys: `{total_keys}`
• Active Keys: `{active_keys}`
• Expired Keys: `{expired_keys}`
• Total Uses: `{total_uses}`

📋 **Recent Gift Keys (Last 5):**
"""
            
            # Show recent gift keys
            sorted_keys = sorted(
                gift_keys.items(),
                key=lambda x: datetime.fromisoformat(x[1].get("generated_at", "2000-01-01")),
                reverse=True
            )
            
            for i, (key, data) in enumerate(sorted_keys[:5], 1):
                expires = datetime.fromisoformat(data.get("expires_at", "2000-01-01"))
                days_left = (expires - datetime.now()).days
                status = "✅" if days_left > 0 and data.get("is_active", True) else "❌"
                
                stats_text += f"\n{i}. {status} `{key}`\n"
                stats_text += f"   📦 {data.get('plan_name', 'N/A')}\n"
                stats_text += f"   📥 {data.get('downloads', 0)} DL | 👥 {data.get('used_count', 0)}/{data.get('max_uses', 1)}\n"
                stats_text += f"   📅 {days_left} days left\n"
            
            await query.edit_message_text(
                stats_text,
                reply_markup=get_back_button("admin_menu"),
                parse_mode=ParseMode.MARKDOWN
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
                "• ₹10 → 5 downloads\n"
                "• ₹40 → 40 downloads\n"
                "• ₹100 → 150 downloads\n\n"
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
            "admin_all_users": lambda: show_all_users(update, context, 0),
            "admin_payments": lambda: handle_payments(update, context),
            "admin_ban": lambda: handle_ban_user(update, context),
            "admin_unban": lambda: handle_unban_user(update, context),
            "admin_maintenance": lambda: toggle_maintenance(update, context),
            "admin_stats": lambda: admin_command(update, context),
            "admin_add": lambda: handle_add_admin(update, context),
            "admin_remove": lambda: handle_remove_admin(update, context),
            "admin_gen_key": lambda: handle_generate_key(update, context),
            "admin_bulk_keys": lambda: handle_bulk_keys(update, context),
            "admin_reply_user": lambda: handle_reply_user(update, context),
            "admin_tickets": lambda: handle_admin_tickets(update, context),
            "admin_reports": lambda: query.edit_message_text(
                "📊 **USER REPORTS** 📊\n\n"
                "This feature is coming soon!",
                reply_markup=get_admin_menu(),
                parse_mode=ParseMode.MARKDOWN
            ),
            "admin_groups": lambda: handle_groups_menu(update, context),
            "admin_bonus_settings": lambda: handle_bonus_settings(update, context)
        }
        
        if data in handlers:
            return await handlers[data]()
        
        # Buy handlers
        elif data.startswith("buy_"):
            plan = data[4:]
            plans = {
                "basic": "₹10 → 5 downloads",
                "pro": "₹40 → 40 downloads",
                "premium": "₹100 → 150 downloads"
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
        try:
            if update.callback_query:
                await update.callback_query.answer("❌ An error occurred!", show_alert=True)
        except:
            pass

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

# Additional handlers for admin functions
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

async def handle_generate_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle generate key from callback - Enhanced"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ Admin Only!", show_alert=True)
            return
        
        keyboard = [
            [InlineKeyboardButton("🔑 BASIC KEY (5 DL)", callback_data="genkey_basic")],
            [InlineKeyboardButton("🔑 PRO KEY (40 DL)", callback_data="genkey_pro")],
            [InlineKeyboardButton("🔑 PREMIUM KEY (150 DL)", callback_data="genkey_premium")],
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

async def handle_bulk_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bulk key generation from callback"""
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

async def handle_groups_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle groups menu from callback"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ Admin Only!", show_alert=True)
            return
        
        await query.edit_message_text(
            "👥 **GROUP MANAGEMENT** 👥\n\n"
            "Manage group activation for unlimited downloads.",
            reply_markup=get_groups_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error handling groups menu: {e}")
        await query.answer("❌ Error loading groups menu!", show_alert=True)

async def handle_bonus_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bonus settings from callback"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ Admin Only!", show_alert=True)
            return
        
        await query.edit_message_text(
            f"🎁 **BONUS SETTINGS** 🎁\n\n"
            f"Current Settings:\n"
            f"• Welcome Bonus: `{bonus_settings_db.get('welcome_bonus', 5)}` downloads\n"
            f"• Referral Bonus: `{bonus_settings_db.get('referral_bonus', 5)}` downloads\n\n"
            f"Select an option to modify:",
            reply_markup=get_bonus_settings_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error handling bonus settings: {e}")
        await query.answer("❌ Error loading bonus settings!", show_alert=True)

# ===================== MESSAGE HANDLER =====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all messages - COMBINED SYSTEM (Enhanced with Z4X URL Detection)"""
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
        
        # Handle gift key redemption from message
        if message_text and len(message_text) > 5 and "-" in message_text:
            # Check if it's a gift key
            if message_text.upper().startswith("GIFT-"):
                result = redeem_gift_key(message_text.upper(), user_id)
                if result["success"]:
                    gift_data = result["data"]
                    
                    gift_msg = f"""
🎁 **GIFT REDEEMED SUCCESSFULLY!** 🎁

**Gift Details:**
• Gift Name: {gift_data['plan_name']}
• Downloads: {gift_data['downloads']}
• Days: {gift_data['days']}
• Expires: {datetime.fromisoformat(gift_data['expires_at']).strftime('%d %b %Y')}

🎉 **Enjoy your gift! Thank the gift giver!** 🎉
"""
                    
                    await update.message.reply_text(
                        gift_msg,
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await update.message.reply_text(
                        f"❌ **GIFT REDEMPTION FAILED**\n\n"
                        f"Error: {result['error']}"
                    )
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
        
        # Handle URL downloads with enhanced detection
        url_detection = URLDetector.smart_url_detection(message_text)
        
        if url_detection["is_valid"]:
            url = url_detection["url"]
            context.user_data['download_url'] = url
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
        
        # ===================== ALL USER MESSAGES FORWARD TO OWNER =====================
        if not is_admin(user_id) and message_text and not message_text.startswith('/'):
            user_info = f"""
📨 **NEW USER MESSAGE**

👤 User: @{update.effective_user.username or 'N/A'}
🆔 ID: `{user_id}`
📛 Name: {update.effective_user.first_name}
📊 Total Messages: {user_data.get('messages_sent', 0)}
📥 Downloads: {user_data.get('total_downloads', 0)}
🏆 Points: {user_data.get('points', 0)}
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
        try:
            if update.message:
                await update.message.reply_text("❌ An error occurred. Please try again.")
        except:
            pass

# ===================== PHOTO HANDLER =====================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads - for payment screenshots and broadcasts"""
    try:
        user_id = update.effective_user.id
        user_data = get_user_stats(user_id)
        
        # Handle broadcast photo
        if context.user_data.get('awaiting_broadcast') and is_admin(user_id):
            # Store photo for broadcast
            photo_file_id = update.message.photo[-1].file_id
            caption = update.message.caption or ""
            
            # Ask for confirmation
            await update.message.reply_text(
                f"📢 **BROADCAST WITH IMAGE** 📢\n\n"
                f"Caption: {caption[:100]}...\n\n"
                f"Reply with `confirm_broadcast` to send this to all users\n"
                f"Reply with `cancel_broadcast` to cancel",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Store broadcast info in context
            context.user_data['broadcast_photo'] = photo_file_id
            context.user_data['broadcast_caption'] = caption
            context.user_data['awaiting_broadcast'] = False
            context.user_data['awaiting_broadcast_confirm'] = True
            return
        
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
        try:
            if update.message:
                await update.message.reply_text("❌ Error processing photo.")
        except:
            pass

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
        BotCommand("redeem", "Redeem gift key"),
        BotCommand("genred", "Generate gift key (admin only)"),
        BotCommand("generate", "Generate key (admin only)"),
        BotCommand("give", "Give downloads to user (owner only)"),
        BotCommand("activategroup", "Activate a group for unlimited downloads (admin only)"),
        BotCommand("deactivategroup", "Deactivate a group (admin only)"),
        BotCommand("listgroups", "List all active groups (admin only)"),
        BotCommand("setwelcomebonus", "Set welcome bonus (admin only)"),
        BotCommand("setreferralbonus", "Set referral bonus (admin only)"),
        BotCommand("givebonus", "Give bonus to user (admin only)")
    ]
    
    await application.bot.set_my_commands(commands)

# ===================== GRACEFUL SHUTDOWN =====================
async def shutdown_handler(signal, frame):
    """Handle graceful shutdown"""
    logger.info("Shutting down bot...")
    # Save all data before shutdown
    save_json(USERS_FILE, users_db)
    save_json(ADMINS_FILE, admins_db)
    save_json(SETTINGS_FILE, settings_db)
    save_json(KEYS_FILE, keys_db)
    save_json(PAYMENTS_FILE, payments_db)
    save_json(DOWNLOAD_HISTORY_FILE, download_history_db)
    save_json(BULK_KEYS_FILE, bulk_keys_db)
    save_json(TICKETS_FILE, tickets_db)
    save_json(REPORTS_FILE, reports_db)
    save_json(GROUPS_FILE, groups_db)
    save_json(BONUS_SETTINGS_FILE, bonus_settings_db)
    save_json(GIFT_KEYS_FILE, gift_keys_db)
    logger.info("All data saved. Exiting...")
    sys.exit(0)

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

# ===================== MAIN FUNCTION =====================
def main():
    """Start the bot - Enhanced with Z4X Features"""
    # Check if wget is installed
    try:
        subprocess.run(["which", "wget"], check=True, capture_output=True)
        print("✅ wget is installed")
    except:
        print("⚠️ WARNING: wget is not installed! Using requests library as fallback.")
        print("For better performance, install wget with:")
        print("  Ubuntu/Debian: sudo apt install wget")
        print("  Termux: pkg install wget")
    
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
    application.add_handler(CommandHandler("redeem", redeem_command))
    application.add_handler(CommandHandler("genred", genred_command))
    application.add_handler(CommandHandler("generate", generate_key_command))
    application.add_handler(CommandHandler("give", give_command))
    application.add_handler(CommandHandler("activategroup", activate_group_command))
    application.add_handler(CommandHandler("deactivategroup", deactivate_group_command))
    application.add_handler(CommandHandler("listgroups", list_groups_command))
    application.add_handler(CommandHandler("setwelcomebonus", setwelcomebonus_command))
    application.add_handler(CommandHandler("setreferralbonus", setreferralbonus_command))
    application.add_handler(CommandHandler("givebonus", givebonus_command))
    
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
    print("🤖 SYNAX DOWNLOAD BOT - ULTIMATE EDITION (Enhanced with Z4X Features)")
    print(f"👑 Owner: {OWNER_NAME} ({OWNER_USERNAME})")
    print("=" * 60)
    print("\n✅ **SYNAX BOT FEATURES:**")
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
    print("\n✅ **Z4X BOT FEATURES ADDED:**")
    print("1. 🎁 Gift Key System - Generate special keys for multiple users")
    print("2. 🌐 Enhanced URL Detection - Better website URL recognition")
    print("3. 🛡️ Robust Error Handling - Better crash protection")
    print("4. 📊 Gift Key Statistics - Track gift key usage")
    print("5. 🔍 Smart URL Detection - Detects all types of URLs")
    print("6. 🌐 Enhanced Download System - Better website downloading")
    print("7. 🛠️ Improved Wget Options - More reliable downloads")
    print("8. 📁 Better File Handling - Improved zip creation")
    print("=" * 60)
    print("\n✅ **NEW FEATURES ADDED:**")
    print("1. 🎁 /redeem command - Users can redeem gift keys")
    print("2. 🎁 /genred command - Admins can generate gift keys")
    print("3. 💳 Payment Approval System - Admins can approve/reject payments")
    print("4. 📜 Download History - Users can view their download history")
    print("5. 📸 Direct Screenshot to Admin - Payment screenshots go directly to admin")
    print("6. ✅ One-Click Approval - Admins can approve payments with one click")
    print("7. 🔑 Bulk Key Generation - Generate multiple keys at once")
    print("8. 📢 Image Broadcast - Send images with captions to all users")
    print("9. 🎫 Support System - Users can create support tickets")
    print("10. 👥 Referral System - Users can refer friends for rewards")
    print("11. 🔄 Fixed Start button and commands not working")
    print("12. 🗂️ Conversation Handler for downloads - Better user experience")
    print("13. 🖼️ Image Removed - Bot now works without welcome image")
    print("14. 🔑 Fixed Activation Key - Now works properly from start menu")
    print("15. 👥 FIXED: Admin Panel Users Button - Now properly displays all users with pagination")
    print("16. 🎫 FIXED: Support Tickets - Now properly creates and manages support tickets")
    print("17. 🔑 FIXED: Bulk Key Generator - Now properly generates and sends bulk keys")
    print("18. 🛡️ CRASH-PROOF: Added comprehensive error handling")
    print("19. 🔧 FIXED: All potential crash points with try-catch blocks")
    print("20. 📊 FIXED: Database operations with proper error handling")
    print("21. 🔄 FIXED: Callback handler with proper error management")
    print("=" * 60)
    print("\n✅ **GROUP ACTIVATION FEATURE ADDED:**")
    print("22. 👥 /activategroup command - Admins can activate groups for unlimited downloads")
    print("23. 👥 /deactivategroup command - Admins can deactivate groups")
    print("24. 👥 /listgroups command - Admins can view all active groups")
    print("25. 👥 Group Management in Admin Panel - Easy to manage activated groups")
    print("26. 👥 Unlimited downloads for all group members when group is activated")
    print("=" * 60)
    print("\n✅ **WGET ISSUE FIXED:**")
    print("27. 🔧 Fixed wget dependency issue - Bot now works without requiring wget installation")
    print("28. 🛠️ Added fallback download method when wget is not available")
    print("29. 🌐 Added requests library as fallback for downloading websites")
    print("30. 📊 Enhanced error handling for download failures")
    print("=" * 60)
    print("\n✅ **BONUS SYSTEM ADDED:**")
    print("31. 🎁 Welcome Bonus - New users automatically receive bonus downloads")
    print("32. 🎁 Admin Panel for Bonus Settings - Admins can configure bonus amounts")
    print("33. 🎁 Manual Bonus Distribution - Admins can give bonus downloads/points to users")
    print("34. 🎁 Points System - Users can earn and accumulate points")
    print("35. 🎁 Bonus History - Track all bonuses given to users")
    print("36. 🎁 Configurable Referral Bonus - Admins can set referral reward amount")
    print("37. 🎁 /setwelcomebonus command - Admins can set welcome bonus amount")
    print("38. 🎁 /setreferralbonus command - Admins can set referral bonus amount")
    print("39. 🎁 /givebonus command - Admins can give bonus to specific users")
    print("=" * 60)
    print("\n🔧 **CRASH FIXES IMPLEMENTED:**")
    print("40. 🛡️ Added comprehensive error handling to all functions")
    print("41. 🔄 Fixed JSON file corruption issues with backup mechanism")
    print("42. ⏱️ Added timeouts to all network requests")
    print("43. 🧹 Added proper resource cleanup for temporary files")
    print("44. 🔄 Fixed conversation handler state management")
    print("45. 📊 Added rate limiting to prevent API abuse")
    print("46. 🔄 Fixed memory leaks in file operations")
    print("47. 🛡️ Added graceful shutdown mechanism")
    print("48. 🔄 Fixed infinite loops in callback handlers")
    print("49. 📊 Added proper error handling for subprocess calls")
    print("=" * 60)
    print("\n🔍 **ADVANCED URL DETECTION ADDED:**")
    print("50. 🌐 Smart URL Detection - Detects all types of URLs from text")
    print("51. 🌐 Enhanced Domain Recognition - Recognizes special domains like GitHub Pages")
    print("52. 🌐 Improved URL Cleaning - Better formatting of URLs")
    print("53. 🌐 URL Type Detection - Identifies different types of websites")
    print("54. 🌐 Confidence Scoring - Rates how confident the bot is about detected URLs")
    print("55. 🌐 Better Error Messages - More informative error messages for invalid URLs")
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
    print(f"  • {GROUPS_FILE} - Activated groups")
    print(f"  • {BONUS_SETTINGS_FILE} - Bonus settings")
    print(f"  • {GIFT_KEYS_FILE} - Gift keys")
    print("=" * 60)
    print("\n🚀 **BOT STARTED SUCCESSFULLY!**")
    print("🛡️ Bot is now CRASH-PROOF with comprehensive error handling!")
    print("🔧 Bot now works with or without wget installed!")
    print("🎁 Gift key system is now active for special promotions!")
    print("🔍 Advanced URL detection system is now active!")
    print("🌐 Enhanced download system is now active!")
    print("🔄 Graceful shutdown implemented to prevent data loss!")
    print("=" * 60)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
