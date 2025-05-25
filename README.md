# TikTok Live Game Bot 🎮

A Python-based bot that interacts with TikTok Live streams, featuring game mechanics and interactive elements.

## 🚀 Features

- Real-time interaction with TikTok Live streams
- Game mechanics for stream engagement
- Customizable responses and actions
- Easy-to-use interface

## 📋 Prerequisites

- Python 3.8+
- Google Colab account
- Google Drive account
- TikTok account

## 🛠️ Setup Instructions

1. **Clone to Google Drive**
   ```bash
   # In Google Colab
   from google.colab import drive
   drive.mount('/content/drive')
   
   # Clone the repository
   !git clone https://github.com/OasisFang/tiktok_live_game.git /content/drive/MyDrive/tiktok_live_game
   ```

2. **Open in Colab**
   - Open [爬虫_Oasis.ipynb](https://colab.research.google.com/github/OasisFang/tiktok_live_game/blob/main/爬虫_Oasis.ipynb) in Google Colab
   - Or create a new notebook and upload the .ipynb file

3. **Install Dependencies**
   ```python
   !pip install -r requirements.txt
   ```

4. **Configure Settings**
   - Update the configuration in the notebook
   - Set your TikTok credentials

## 🎮 Usage

1. Run the notebook cells in sequence
2. Enter the TikTok Live room ID when prompted
3. The bot will start interacting with the live stream

## 📁 Project Structure

```
tiktok_live_game/
├── tiktok_live_bot_Oasis.ipynb      # Main notebook
├── final.py             # Core functionality
├── roominfo.py          # Room information handler
├── test.py             # Testing utilities
├── draft.py            # Development version
├── templates/          # HTML templates
├── static/            # Static assets
└── anime/             # Anime-related resources
```

## ⚠️ Important Notes

- The bot must be run in Google Colab for optimal performance
- Ensure you have sufficient Google Drive storage
- Keep your TikTok credentials secure

## 🔒 Security

- Never share your TikTok credentials
- Use environment variables for sensitive information
- Regularly update your dependencies

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Author

- OasisFang

## 🙏 Acknowledgments

- TikTok Live API
- Python community
- Open source contributors
