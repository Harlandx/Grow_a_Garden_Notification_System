- 🌱 Fetches real-time seeds data from GAGAPI
- 📊 Displays seeds information in a formatted terminal output
- 🔄 Interactive refresh functionality
- 🎨 Beautiful terminal formatting with emojis
- ⚡ Error handling and retry mechanisms
- 👀 Stock monitoring - Watch specific seeds for availability
- 📢 Discord notifications - Get alerts when watched seeds come in stock
- 📋 Customizable watchlist - Easy to configure which seeds to monitor

**The program monitors ALL categories from the GAGAPI:**
**Seeds** - Plant seeds like Carrot, Bamboo, Strawberry, etc.
**Gear** - Tools like Trowel, Watering Can, Cleaning Spray, etc.
**Eggs** - Various egg types
**Cosmetics** - Decorative items like Beach Crate, Sign Crate, etc.
**Event Shop** - Special event items like Gnome Crates

**Prerequisites**
- Python 3.7 or higher
- Internet connection to access the GAGAPI
- Install the required dependencies

**Configure your watchlist** (optional):
- Edit `watchlist.txt` to add seed names you want to monitor
- One seed name per line

**Configure Discord notifications** (optional):
- Edit `discord_webhook.txt` and replace the URL with your Discord webhook

**Run the program**
python gag_seeds_client.py

**This program uses the [GAGAPI](https://github.com/Liriosha/GAGAPI) which provides:**
- Real-time data from the Roblox game "Grow A Garden"
- REST API endpoints for game data
- Rate limiting (5 requests/minute per IP)
- CORS enabled
