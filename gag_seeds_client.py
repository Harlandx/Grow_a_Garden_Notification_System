#!/usr/bin/env python3

import requests
import json
import time
from datetime import datetime
import sys
import os
import threading
import msvcrt

class GAGItemsMonitor:
    def __init__(self):
        self.base_url = "https://gagapi.onrender.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GAGBot/1.0 (Python Client)',
            'Accept': 'application/json'
        })
        self.watchlist = self.load_watchlist()
        self.discord_webhook = self.load_discord_webhook()
        self.previous_stock = {}  # Track previous stock levels
        self.categories = ['seeds', 'gear', 'eggs', 'cosmetics', 'eventshop']
        self.auto_refresh = False
        self.auto_refresh_interval = 60  # seconds
        self.last_refresh_time = time.time()
        self.running = True
    
    def load_watchlist(self):
        """Load the watchlist from watchlist.txt file"""
        watchlist = []
        watchlist_file = "watchlist.txt"
        
        if os.path.exists(watchlist_file):
            try:
                with open(watchlist_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            watchlist.append(line)
                print(f"📋 Loaded {len(watchlist)} items to watch: {', '.join(watchlist)}")
            except Exception as e:
                print(f"⚠️ Warning: Could not load watchlist: {e}")
        else:
            print("⚠️ Warning: watchlist.txt not found. No items will be monitored.")
        
        return watchlist
    
    def load_discord_webhook(self):
        """Load Discord webhook URL from discord_webhook.txt file"""
        webhook_file = "discord_webhook.txt"
        
        if os.path.exists(webhook_file):
            try:
                with open(webhook_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and line.startswith('https://discord.com/api/webhooks/'):
                            print("🔗 Discord webhook loaded successfully")
                            return line
                print("⚠️ Warning: No valid Discord webhook found in discord_webhook.txt")
            except Exception as e:
                print(f"⚠️ Warning: Could not load Discord webhook: {e}")
        else:
            print("⚠️ Warning: discord_webhook.txt not found. Discord notifications disabled.")
        
        return None
    
    def send_discord_notification(self, item_name, category, quantity, previous_quantity):
        """Send Discord notification when item stock changes"""
        if not self.discord_webhook:
            return
        
        try:
            embed = {
                "title": "🎉 Item Stock Alert!",
                "description": f"**{item_name}** is now in stock!",
                "color": 0x00ff00,  # Green color
                "fields": [
                    {
                        "name": "Category",
                        "value": f"**{category.title()}**",
                        "inline": True
                    },
                    {
                        "name": "Current Stock",
                        "value": f"**{quantity}** available",
                        "inline": True
                    },
                    {
                        "name": "Previous Stock",
                        "value": f"**{previous_quantity}** available",
                        "inline": True
                    }
                ],
                "timestamp": datetime.now().isoformat(),
                "footer": {
                    "text": "GAG Items Monitor"
                }
            }
            
            payload = {
                "embeds": [embed]
            }
            
            response = requests.post(self.discord_webhook, json=payload)
            if response.status_code == 204:
                print(f"📢 Discord notification sent for {item_name} ({category})!")
            else:
                print(f"❌ Failed to send Discord notification: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error sending Discord notification: {e}")
    
    def check_stock_changes(self, all_items_data):
        """Check for stock changes in watched items across all categories"""
        if not self.watchlist:
            return
        
        current_stock = {}
        
        # Build current stock dictionary from all categories
        for category, items in all_items_data.items():
            for item in items:
                item_name = item.get('name', '').lower()
                quantity = item.get('quantity', 0)
                # Store with category info
                current_stock[item_name] = {'quantity': quantity, 'category': category}
        
        # Check for changes in watched items
        for watched_item in self.watchlist:
            watched_item_lower = watched_item.lower()
            current_data = current_stock.get(watched_item_lower, {'quantity': 0, 'category': 'unknown'})
            current_quantity = current_data['quantity']
            category = current_data['category']
            
            # Get previous quantity (without category info)
            previous_quantity = self.previous_stock.get(watched_item_lower, 0)
            
            # Send notification for every refresh if item is in stock
            if current_quantity > 0:
                print(f"🎉 ALERT: {watched_item} is in stock! ({current_quantity} available in {category})")
                self.send_discord_notification(watched_item, category, current_quantity, previous_quantity)
            
            # Update previous stock
            self.previous_stock[watched_item_lower] = current_quantity
    
    def get_all_items_data(self):
        """Fetch all items data from the GAGAPI"""
        all_data = {}
        
        for category in self.categories:
            try:
                print(f"📦 Fetching {category} data from GAGAPI...")
                response = self.session.get(f"{self.base_url}/{category}")
                
                if response.status_code == 200:
                    all_data[category] = response.json()
                else:
                    print(f"❌ Error fetching {category}: HTTP {response.status_code}")
                    all_data[category] = []
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Network error fetching {category}: {e}")
                all_data[category] = []
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error for {category}: {e}")
                all_data[category] = []
        
        return all_data
    
    def display_all_items(self, all_items_data):
        """Display all items data in a formatted way"""
        print("\n" + "="*60)
        print("🎮 GROW A GARDEN - ALL ITEMS DATA")
        print("="*60)
        print(f"📅 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show auto-refresh status
        if self.auto_refresh:
            time_since_refresh = int(time.time() - self.last_refresh_time)
            time_until_next = self.auto_refresh_interval - time_since_refresh
            print(f"⏰ Auto-refresh: ENABLED ({time_until_next}s until next refresh)")
        else:
            print("⏰ Auto-refresh: DISABLED")
        
        # Show watchlist status
        if self.watchlist:
            print(f"📋 Watching: {', '.join(self.watchlist)}")
        if self.discord_webhook:
            print("🔗 Discord notifications: Enabled")
        else:
            print("🔗 Discord notifications: Disabled")
        
        print("="*60)
        
        total_items = 0
        watched_items_found = []
        
        for category, items in all_items_data.items():
            if not items:
                continue
                
            print(f"\n📦 {category.upper()} ({len(items)} items)")
            print("-" * 40)
            
            for i, item in enumerate(items, 1):
                item_name = item.get('name', 'Unknown')
                quantity = item.get('quantity', 0)
                total_items += 1
                
                # Check if this item is being watched
                is_watched = item_name.lower() in [s.lower() for s in self.watchlist]
                if is_watched:
                    watched_items_found.append(f"{item_name} ({category})")
                
                watch_indicator = "👀 " if is_watched else "📦 "
                
                print(f"{watch_indicator}{item_name}: {quantity}")
                
                # Highlight if watched item is in stock
                if is_watched and quantity > 0:
                    print(f"   ✅ IN STOCK!")
                elif is_watched and quantity == 0:
                    print(f"   ❌ OUT OF STOCK")
        
        print("\n" + "="*60)
        print(f"📊 Total Items Available: {total_items}")
        
        if watched_items_found:
            print(f"👀 Watched Items Found: {', '.join(watched_items_found)}")
        else:
            print("👀 No watched items currently available")
        
        print("="*60)
    
    def keyboard_input_handler(self):
        """Handle keyboard input in a separate thread"""
        print("\n⌨️  Keyboard Controls:")
        print("• Press 'M' to toggle 60-second auto-refresh")
        print("• Press 'R' to refresh manually")
        print("• Press 'Q' to quit")
        print("• Press Enter to refresh manually")
        
        while self.running:
            try:
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8').upper()
                    
                    if key == 'M':
                        self.auto_refresh = not self.auto_refresh
                        if self.auto_refresh:
                            print(f"\n⏰ Auto-refresh ENABLED - refreshing every {self.auto_refresh_interval} seconds")
                            self.last_refresh_time = time.time()
                        else:
                            print("\n⏰ Auto-refresh DISABLED")
                    
                    elif key == 'R':
                        print("\n🔄 Manual refresh triggered")
                        self.last_refresh_time = time.time()
                    
                    elif key == 'Q':
                        print("\n👋 Quitting...")
                        self.running = False
                        break
                        
            except Exception as e:
                print(f"❌ Keyboard input error: {e}")
                break
    
    def run(self):
        """Main execution method"""
        print("🚀 Starting GAG Items Monitor...")
        print(f"🔗 API Base URL: {self.base_url}")
        
        # Start keyboard input handler in a separate thread
        keyboard_thread = threading.Thread(target=self.keyboard_input_handler, daemon=True)
        keyboard_thread.start()
        
        while self.running:
            try:
                # Fetch all items data
                all_items_data = self.get_all_items_data()
                
                # Check for stock changes in watched items
                self.check_stock_changes(all_items_data)
                
                # Display the data
                self.display_all_items(all_items_data)
                
                # Handle auto-refresh or manual input
                if self.auto_refresh:
                    # Auto-refresh mode
                    time_since_refresh = time.time() - self.last_refresh_time
                    if time_since_refresh >= self.auto_refresh_interval:
                        print(f"\n⏰ Auto-refreshing after {self.auto_refresh_interval} seconds...")
                        self.last_refresh_time = time.time()
                    else:
                        # Show countdown
                        remaining = self.auto_refresh_interval - int(time_since_refresh)
                        print(f"\n⏰ Next auto-refresh in {remaining} seconds... (Press 'M' to disable)")
                        
                        # Wait for either auto-refresh time or manual input
                        for _ in range(remaining):
                            if not self.running:
                                break
                            time.sleep(1)
                else:
                    # Manual mode - ask user for input
                    print("\n🔄 Options:")
                    print("1. Refresh data (press Enter)")
                    print("2. Enable 60s auto-refresh (type 'r')")
                    print("3. Exit (type 'quit' or 'exit')")
                    
                    user_input = input("\nEnter your choice: ").strip().lower()
                    
                    if user_input in ['quit', 'exit', 'q']:
                        print("👋 Goodbye!")
                        self.running = False
                        break
                    elif user_input == 'r':
                        self.auto_refresh = True
                        self.last_refresh_time = time.time()
                        print(f"⏰ Auto-refresh ENABLED - refreshing every {self.auto_refresh_interval} seconds")
                        continue
                    elif user_input == '':
                        print("🔄 Refreshing data...")
                        time.sleep(1)
                        continue
                    else:
                        print("🔄 Refreshing data...")
                        time.sleep(1)
                        continue
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                self.running = False
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                print("🔄 Retrying in 5 seconds...")
                time.sleep(5)

def main():
    """Main function"""
    print("🎮 Welcome to GAG Items Monitor!")
    print("This program monitors all items from the Grow A Garden API")
    print("="*60)
    
    monitor = GAGItemsMonitor()
    monitor.run()

if __name__ == "__main__":
    main() 