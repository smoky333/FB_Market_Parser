# Facebook Marketplace Notification Bot

## Description
A Telegram bot that provides real-time notifications for new listings on Facebook Marketplace. Ideal for individuals and businesses, the bot offers advanced filtering options, multi-client support, and a user-friendly interface to track and manage Marketplace listings effectively.

## Features
- **Real-Time Notifications**: Get instant alerts for new Facebook Marketplace listings based on specified categories and locations.
- **Category Support**: Tracks items such as iPhones, MacBooks, Cars, Furniture, and more.
- **Location Filtering**: Monitor listings in specific cities or zip codes.
- **Multi-Client Support**: Manage multiple user groups with personalized filters for each client.
- **Data Export**: Save listings to a CSV file for further analysis and management.
- **Scalable and Robust**: Handles hundreds of clients and notifications simultaneously.

## Admin Features
- Add or manage filters and groups for multiple clients.
- Monitor bot activity and performance via simple commands.

## Technologies Used
- **Python**: Backend development with aiogram.
- **SQLite**: Lightweight database for storing filters and user data.
- **Selenium**: Web scraping for Facebook Marketplace.
- **BeautifulSoup**: HTML parsing for data extraction.
- **Telegram Bot API**: Enables seamless bot-to-user communication.

## Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repository/facebook-marketplace-bot.git
   ```
2. **Navigate to the project directory**:
   ```bash
   cd facebook-marketplace-bot
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set environment variables**:
   - Create a `.env` file in the root directory.
   - Add your Telegram Bot API token and other credentials:
     ```
     BOT_TOKEN=your_telegram_bot_token
     ```
5. **Run the bot**:
   ```bash
   python main.py
   ```

## How to Use
- **Start the bot**: Use the `/start` command to initialize the bot.
- **Add filters**: Use `/add_filter` to specify categories and locations for monitoring.
- **Manage filters**: Use `/list_filters`, `/remove_filter`, or `/clear_filters` to manage your preferences.
- **Set Facebook credentials**: Use `/set_facebook_credentials` to log in for personalized scraping.

## Contribution
Contributions are welcome! Fork the repository, create a new branch, and submit a pull request with your changes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contact
For questions or support, reach out to [your-email@example.com](mailto:your-email@example.com).
