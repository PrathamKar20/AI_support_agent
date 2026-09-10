import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from app.config import DATA_DIR, TARGET_BRAND

# Path to local sample seed file
SAMPLE_SEED_PATH = DATA_DIR / "apple_support_resolutions.json"

# Representative corpus of @AppleSupport customer queries and historical resolutions
DEFAULT_HISTORICAL_CORPUS: List[Dict[str, str]] = [
    # Battery & Power
    {
        "intent": "Battery & Power",
        "customer_query": "@AppleSupport My iPhone battery is draining extremely fast after updating to iOS 17. Down from 100% to 20% in 3 hours!",
        "brand_resolution": "@AppleSupport We understand how important battery life is. Try checking Settings > Battery to see which apps are consuming power. Also check Battery Health & Charging. If Peak Performance Capability is degraded, send us a DM.",
        "tweet_id": "apple_bat_101"
    },
    {
        "intent": "Battery & Power",
        "customer_query": "@AppleSupport my iphone 13 won't charge past 80% when plugged in overnight. Is my battery broken?",
        "brand_resolution": "@AppleSupport That sounds like Optimized Battery Charging in action! Go to Settings > Battery > Battery Health & Charging and check if Optimized Battery Charging is turned on. It delays charging past 80% to protect battery lifespan.",
        "tweet_id": "apple_bat_102"
    },
    {
        "intent": "Battery & Power",
        "customer_query": "@AppleSupport My phone gets super hot while charging and turns off automatically.",
        "brand_resolution": "@AppleSupport We take safety very seriously. Please unplug your device immediately. Check if your phone is in direct sunlight or a hot environment. DM us your iOS version and serial number for urgent hardware diagnosis.",
        "tweet_id": "apple_bat_103"
    },
    
    # iOS & System Updates
    {
        "intent": "iOS & System Updates",
        "customer_query": "@AppleSupport My screen freezes on the Apple logo during the iOS update. How do I fix this?",
        "brand_resolution": "@AppleSupport We're here to help get your device back up! Force restart your iPhone while connected to a Mac/PC, then use Recovery Mode via Finder/iTunes to Update without erasing data. Check details here: apple.co/RecoveryMode",
        "tweet_id": "apple_ios_201"
    },
    {
        "intent": "iOS & System Updates",
        "customer_query": "@AppleSupport keyboard lag on typing after updating my iPad today. It stutters so badly.",
        "brand_resolution": "@AppleSupport Thanks for reaching out. Try resetting your keyboard dictionary by navigating to Settings > General > Transfer or Reset iPad > Reset > Reset Keyboard Dictionary. Let us know if the issue persists in DM.",
        "tweet_id": "apple_ios_202"
    },
    {
        "intent": "iOS & System Updates",
        "customer_query": "@AppleSupport Wi-Fi keeps disconnecting every 5 minutes since updating to the latest software release.",
        "brand_resolution": "@AppleSupport Let's troubleshoot Wi-Fi together. Go to Settings > General > Transfer or Reset > Reset > Reset Network Settings. Note: this resets saved Wi-Fi passwords. DM us if you need step-by-step assistance.",
        "tweet_id": "apple_ios_203"
    },

    # Apple ID & Account Security
    {
        "intent": "Apple ID & Account Security",
        "customer_query": "@AppleSupport I got locked out of my Apple ID because I forgot my password and changed my phone number!",
        "brand_resolution": "@AppleSupport Account security is essential. You can initiate Account Recovery at iforgot.apple.com to regain access securely. For safety reasons, Apple Support agents cannot manually reset passwords over chat.",
        "tweet_id": "apple_id_301"
    },
    {
        "intent": "Apple ID & Account Security",
        "customer_query": "@AppleSupport Received an email saying my Apple ID was logged into from Russia. I didn't log in! Help!",
        "brand_resolution": "@AppleSupport Please do not click any links in suspicious emails. Go directly to appleid.apple.com, sign in securely, change your password immediately, and ensure Two-Factor Authentication is enabled. Send us a DM if you see unrecognized charges.",
        "tweet_id": "apple_id_302"
    },
    {
        "intent": "Apple ID & Account Security",
        "customer_query": "@AppleSupport Two-factor authentication code is not arriving on my trusted device.",
        "brand_resolution": "@AppleSupport We can help with verification. Ensure your device has an active cellular/Wi-Fi connection. If you still don't receive it, tap 'Didn't get a verification code?' on the sign-in screen to select an SMS backup.",
        "tweet_id": "apple_id_303"
    },

    # App Store & Subscriptions
    {
        "intent": "App Store & Subscriptions",
        "customer_query": "@AppleSupport I was charged $14.99 for an app subscription I canceled 2 weeks ago! I want a full refund.",
        "brand_resolution": "@AppleSupport We understand billing concerns. You can request a refund directly by visiting reportaproblem.apple.com. Log in with your Apple ID, select 'Request a refund', and state the cancellation reason. DM us if you encounter errors.",
        "tweet_id": "apple_sub_401"
    },
    {
        "intent": "App Store & Subscriptions",
        "customer_query": "@AppleSupport App Store says 'Your Payment Method Was Declined' when I try to update free apps.",
        "brand_resolution": "@AppleSupport Even for free app updates, an active payment method on file must be verified. Go to Settings > [Your Name] > Payment & Shipping, update your card details or add a valid payment method, then retry.",
        "tweet_id": "apple_sub_402"
    },
    {
        "intent": "App Store & Subscriptions",
        "customer_query": "@AppleSupport How do I cancel my Apple Music individual subscription before the free trial ends?",
        "brand_resolution": "@AppleSupport Easy steps! Open Settings > tap [Your Name] > Subscriptions > Apple Music > Cancel Subscription. Make sure to cancel at least 24 hours before the trial renewal date.",
        "tweet_id": "apple_sub_403"
    },

    # Hardware & Screen Repair
    {
        "intent": "Hardware & Screen Repair",
        "customer_query": "@AppleSupport I dropped my iPhone 14 Pro and the back glass completely shattered. How much does repair cost under AppleCare+?",
        "brand_resolution": "@AppleSupport We're sorry to hear about the drop. Under AppleCare+ with Theft and Loss or AppleCare+, back glass damage repair is $29 service fee. You can check estimate costs and schedule a service appointment at support.apple.com/repair.",
        "tweet_id": "apple_hwd_501"
    },
    {
        "intent": "Hardware & Screen Repair",
        "customer_query": "@AppleSupport My MacBook Air M2 screen has black vertical lines across the display. Is this covered under warranty?",
        "brand_resolution": "@AppleSupport Display artifacts should be examined by a technician. If your Mac is within the 1-year Limited Warranty and shows no accidental liquid/physical damage, repair is covered. DM us your serial number so we can check warranty status.",
        "tweet_id": "apple_hwd_502"
    },
    {
        "intent": "Hardware & Screen Repair",
        "customer_query": "@AppleSupport Speaker on my iPhone sounds crackly and muffled during calls.",
        "brand_resolution": "@AppleSupport Let's check the speakers. Clean any debris from receiver or speaker grilles with a soft brush. Go to Settings > Sounds & Haptics and slide Ringer and Alerts volume back and forth. If still crackly, DM us for hardware diagnostics.",
        "tweet_id": "apple_hwd_503"
    },

    # Audio & Bluetooth Connectivity
    {
        "intent": "Audio & Bluetooth Connectivity",
        "customer_query": "@AppleSupport My AirPods Pro (2nd gen) won't pair with my iPhone. The light flashes amber.",
        "brand_resolution": "@AppleSupport Flashing amber indicates AirPods need to be reset. Place AirPods in case, close lid for 30s. Open lid, hold setup button on back until light flashes amber then white. Then hold near iPhone to re-pair.",
        "tweet_id": "apple_aud_601"
    },
    {
        "intent": "Audio & Bluetooth Connectivity",
        "customer_query": "@AppleSupport Left AirPod is completely silent while right AirPod plays fine.",
        "brand_resolution": "@AppleSupport Let's check balance settings! Go to Settings > Accessibility > Audio/Visual and ensure the Balance slider is centered. If balance is fine, try resetting your AirPods case or DM us to check replacement options.",
        "tweet_id": "apple_aud_602"
    },

    # General Inquiry & Support
    {
        "intent": "General Inquiry & Support",
        "customer_query": "@AppleSupport What is the trade-in value for an iPhone 12 128GB in good condition towards iPhone 15?",
        "brand_resolution": "@AppleSupport Trade-in values vary based on device condition and model. You can get an instant estimated trade-in quote at apple.com/shop/trade-in by entering your device serial number. DM us if you need help with trade-in shipping!",
        "tweet_id": "apple_gen_701"
    },
    {
        "intent": "General Inquiry & Support",
        "customer_query": "@AppleSupport How do I transfer all my photos and contacts from an Android phone to new iPhone?",
        "brand_resolution": "@AppleSupport Welcome to iPhone! Download the 'Move to iOS' app from the Google Play Store on your Android phone. During initial setup on your iPhone, select 'Move Data from Android' and follow the on-screen code prompt.",
        "tweet_id": "apple_gen_702"
    }
]


def load_dataset() -> List[Dict[str, str]]:
    """
    Loads historical customer support resolution pairs.
    Saves to seed file if it doesn't exist, guaranteeing fast offline reproduction.
    """
    if not SAMPLE_SEED_PATH.exists():
        with open(SAMPLE_SEED_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_HISTORICAL_CORPUS, f, indent=2)
        return DEFAULT_HISTORICAL_CORPUS
    
    try:
        with open(SAMPLE_SEED_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_HISTORICAL_CORPUS
