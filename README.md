# 🎵 SoundChat - Your Musical Companion 🎵

Welcome to **SoundChat**! Transform your emotions into music with this AI-based intelligent playlist generator. Whether you're feeling joyful, melancholic, or in need of motivation, SoundChat creates personalized playlists that match your mood. Let's dive into the world of music and emotions!

A deployed version of SoundChat is available at [bit.ly/soundchatai](https://bit.ly/soundchatai).
To use this application, you'll need to be added as a user on the Spotify Developer Dashboard. This is because I am currently using Spotify's development API, which has usage limits.

## 🌟 Features

- **Emotion-Based Playlists**: Generate playlists based on your current mood.
- **Spotify Integration**: Connect your Spotify account and enjoy your custom playlists directly.
- **User-Friendly Interface**: Simple and intuitive design for a seamless experience.
- **Support for Multiple Moods**: From dancing vibes to workout tunes, find the perfect playlist for every occasion.
- **AI-Powered Recommendations**: Leverage OpenAI's GPT-3 to generate personalized playlist names.

## 🚀 Installation

Follow these steps to get SoundChat up and running on your local machine:

1. **Clone the repository**:
    ```sh
    git clone https://github.com/hrialan/soundchat.git
    cd soundchat
    ```

2. **Set up the virtual environment**:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Configure environment variables**:
    Create a `.env` file in the root directory and add the following:
    ```env
    FLASK_SESSION_DIR='./.flask_session/'
    SPOTIPY_CLIENT_ID="your_spotify_client_id"
    SPOTIPY_CLIENT_SECRET="your_spotify_client_secret"
    SPOTIPY_REDIRECT_URI='http://127.0.0.1:8080'
    OPENAI_API_KEY="your_openai_api_key"
    GOOGLE_CLOUD_PROJECT="your_google_cloud_project"
    FIRESTORE_DATABASE="your_firestore_database"
    ENCRYPTION_KEY="Fernet key used for encryption of sensitive data in Firestore"
    ```

5. **Run the application**:
    ```sh
    python run.py
    ```

## 🎉 Usage

1. **Visit the homepage**: Open your browser and go to `http://127.0.0.1:8080`.
2. **Connect to Spotify**: Click on the "Connect to Spotify" button to authorize SoundChat.
3. **Generate a Playlist**: Enter your mood or activity in the textbox and click "Generate Playlist".
4. **Enjoy your music**: Your personalized playlist will be created on your Spotify account.

## ⚙️ Configuration

- **Spotify Client ID and Secret**: Obtain these from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications).
- **OpenAI API Key**: Get your API key from [OpenAI](https://beta.openai.com/signup/).
- **Google Cloud Project**: Set up a project on [Google Cloud](https://console.cloud.google.com/).

## 🛠 Development

1. **Pre-commit Hooks**: Ensure code quality by setting up pre-commit hooks:
    ```sh
    pre-commit install
    ```

2. **Run Tests**: Execute tests to verify your changes:
    ```sh
    pytest
    ```

3. **Linting**: Use `flake8` and `black` for linting and formatting:
    ```sh
    flake8 .
    black .
    ```

## 📦 Deployment

In the folder 'iac' you can find the Terraform scripts to deploy the application on Google Cloud Platform. The scripts create a Cloud Run service and a Firestore database.

## 🤝 Contributing

Interested in contributing to SoundChat? Here's how you can help improve the project:

1. **Fork the repository**.
2. **Create a new branch**:
    ```sh
    git checkout -b feature/your-feature-name
    ```
3. **Make your changes**.
4. **Commit your changes**:
    ```sh
    git commit -m "Add your message"
    ```
5. **Push to the branch**:
    ```sh
    git push origin feature/your-feature-name
    ```
6. **Create a Pull Request**.

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Thank you for checking out SoundChat! Enjoy creating and listening to your personalized playlists. If you have any questions or feedback, feel free to reach out. Happy listening! 🎧
