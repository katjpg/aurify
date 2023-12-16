# Aurify - Spotify Visualizer 

**Author**: Kat L., University of California, Los Angeles (UCLA)

![Aurify Homepage](static/img/aurify-homepage.png)
![Aurify Profile](static/img/aurify-profile.png)

## ✦ Introduction 

Aurify is a web application that creates personalized “Aura” visualizations based on your Spotify listening habits. The creation of Aurify was heavily inspired by Spotify’s 2021 Wrapped. :^) 

## ✦ Description 

Aurify leverages real-time integration with Spotify to analyze your top tracks, identifying key musical attributes, and ultimately translating them into an “Aura.” An Aura contains two main elements: an outer color and core color. 

### Outer Color 
The outer color of your Aura is inspired by Scrabbin’s Circle of Fifths, a concept in music theory. This color reflects the most common musical key in your favorite songs, offering a glimpse into the mood and tone of your preferred music.

### Core Color 
The core color is derived from the Circumplex Model of Affect. This color represents the valence-arousal aspects of your music – basically, it's all about the emotions and energy your music embodies. The core color changes based on whether your music is more energetic or calming, and whether it carries a more positive or somber tone.

## ✦ Running Locally 

The following below are key steps to set up and run Aurify on your local machine.

### Prerequisites

- **Python**: Ensure Python is installed on your system. [Download Python](https://www.python.org/downloads/)
- **Node.js and npm**: Aurify uses TailwindCSS, which requires Node.js and npm (Node Package Manager). [Download Node.js](https://nodejs.org/en/download/)

### Clone the Repository

1. **Clone the Repository**: Clone Aurify to your local machine using:
   ```bash
   git clone https://github.com/katjpg/aurify.git
   cd aurify
   ```

### Set Up the Environment

1. **Create a Virtual Environment** (optional but recommended):
   - For Unix/macOS:
     ```bash
     python3 -m venv aurify-venv
     source aurify-venv/bin/activate
     ```
   - For Windows:
     ```bash
     python -m venv aurify-venv
     .\aurify-venv\Scripts\activate
     ```

2. **Install Python Dependencies**:
   - While in your virtual environment, install the required Python packages:
     ```bash
     pip install -r requirements.txt
     ```

### Set Up TailwindCSS

1. **Install Node.js Dependencies**:
   - Install the required Node.js packages (including TailwindCSS):
     ```bash
     npm install
     ```

2. **Build the TailwindCSS File**:
   - Generate the final CSS using:
     ```bash
     npm run buildcss
     ```

### Configure Environment Variables

1. **Create an `.env` File**:
   - Create a file named `.env` in the root directory of the project.
   - Add the following content, replacing the placeholders with your actual credentials:
     ```
     SPOTIFY_CLIENT_ID=your_spotify_client_id
     SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
     SESSION_TOKEN=SPOTIFY_AUTH_TOKEN
     FLASK_SECRET_KEY=your_secret_key
     ```
   - `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` can be obtained from your Spotify Developer Dashboard.
   - `FLASK_SECRET_KEY` should be a random, secure string.

### Run the Application

1. **Start the Flask App**:
   - Run the following command to start the Flask server:
     ```bash
     python app.py
     ```

2. **Access the App**:
   - Open your web browser and go to [http://localhost:5000](http://localhost:5000) to view the app.


## ✦ Repository Structure 

An overview of the main files and directories in Aurify:

```bash
aurify/
├── LICENSE               # The license file.
├── README.md             # The README file with project information.
├── app.py                # The main Python file to run the Flask application.
├── aura_visualization.py # Python script for aura visualization functionalities.
├── package.json          # Node.js package file for managing Node dependencies.
├── processing.py         # Python script for processing audio features.
├── requirements.txt      # Contains the list of Python packages required for the project.
├── static/               # Directory for static files like CSS, JavaScript, and images.
├── tailwind.config.js    # TailwindCSS configuration file.
└── templates/            # Directory containing Flask HTML templates.
```

