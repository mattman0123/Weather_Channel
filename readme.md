# Weather Channel

**Weather Channel** is a web-based dashboard that provides users with up-to-date information on weather conditions, air quality, news, and stock market data. The application aggregates data from various JSON sources and presents it in an organized and user-friendly interface.

## Features

- **Weather Updates**: Displays current weather conditions sourced from `weather.json`.
- **Air Quality Alerts**: Presents air quality health index alerts from `aqhi_alerts.json`.
- **News Feed**: Showcases the latest news headlines retrieved from `news.json`.
- **Stock Market Data**: Provides real-time stock information from `stocks.json`.
- **Dynamic Interface**: Utilizes JavaScript and CSS to create an interactive and responsive user experience.

## Project Structure

```
Weather_Channel/
├── alerts.json              # Contains general alert information
├── aqhi_alerts.json         # Air Quality Health Index alerts
├── generate_weather_json.py # Script to generate weather data in JSON format
├── index.html               # Main HTML file for the dashboard
├── news.json                # Latest news headlines
├── script.js                # JavaScript for dynamic content rendering
├── stocks.json              # Stock market data
├── style.css                # Styling for the dashboard
├── weather.json             # Weather data
└── .gitignore               # Specifies files to ignore in the repository
```
## Demo
   https://weather.vinck.cloud

## Getting Started

To set up and run the Weather Channel dashboard locally:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mattman0123/Weather_Channel.git
   cd Weather_Channel
   ```

2. **Generate Weather Data**:
   Ensure you have Python installed. Run the following script to generate the `weather.json` file:
   ```bash
   python generate_weather_json.py
   ```

3. **Launch the Dashboard**:
   Open `index.html` in your preferred web browser to view the dashboard.

## Dependencies

- **Frontend**:
  - HTML5
  - CSS3
  - JavaScript (Vanilla)

- **Backend**:
  - Python 3.x (for data generation scripts)

## Contributing

Contributions are welcome! If you'd like to enhance the dashboard or add new features:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/YourFeatureName
   ```
3. Commit your changes:
   ```bash
   git commit -m 'Add your feature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/YourFeatureName
   ```
5. Open a pull request detailing your changes.

## License

This project is open-source and available under the [MIT License](LICENSE).
