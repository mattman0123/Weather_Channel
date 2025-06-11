let weatherSlides = [];
let newsSlides = [];
let stockSlides = [];
let allSlides = [];
let currentSlide = 0;
let currentText = '';
let currentCharIndex = 0;
let currentType = 'weather';

const weatherBox = document.getElementById("weather-box");

function typeNextChar() {
    if (currentCharIndex <= currentText.length) {
        weatherBox.innerHTML = currentText.substring(0, currentCharIndex);
        currentCharIndex++;
        setTimeout(typeNextChar, 150);
    } else {
        setTimeout(showNextSlide, 2500);
    }
}

function showNextSlide() {
    currentSlide = (currentSlide + 1) % allSlides.length;
    currentType = allSlides[currentSlide].type;
    currentText = allSlides[currentSlide].text;
    currentCharIndex = 0;
    typeNextChar();
}

async function fetchSlides() {
    try {
        const [weatherRes, newsRes, stockRes, alertRes] = await Promise.all([
            fetch("weather.json"),
            fetch("news.json"),
            fetch("stocks.json"),
        ]);

        const weatherData = await weatherRes.json();
        const newsData = await newsRes.json();
        const stockData = await stockRes.json();

        weatherSlides = formatWeather(weatherData);
        newsSlides = formatNews(newsData);
        stockSlides = formatStocks(stockData);
        interleaveSlides();
        currentText = allSlides[0].text;
        typeNextChar();
    } catch (error) {
        console.error("❌ Error loading JSON files:", error);
        weatherBox.innerHTML = "⚠️ Error loading data.";
    }
}

async function loadAQHITicker() {
  try {
    const response = await fetch('aqhi_alerts.json');
    const alerts = await response.json(); 

    if (Array.isArray(alerts) && alerts.length > 0) {
        const ticker = document.getElementById('ticker-content');
        const ticker_bar = document.getElementById('ticker-bar');
        ticker.innerText = alerts.join('      ••••      ');      
        ticker_bar.style.display = 'block';

    }else{
        const ticker = document.getElementById('ticker-bar');
        ticker.style.display = 'none';
    }
  } catch (error) {
        console.error('Failed to load AQHI ticker:', error);
        const ticker = document.getElementById('ticker-bar');
        ticker.style.display = 'none';
  }
}

async function loadAlertTicker() {
  try {
    const response = await fetch('alerts.json');
    const alerts = await response.json(); 

    if (Array.isArray(alerts) && alerts.length > 0) {
        const ticker = document.getElementById('alert-ticker-content');
        const ticker_bar = document.getElementById('alert-ticker-bar');
        ticker.innerText = alerts.join('      ••••      ');      
        ticker_bar.style.display = 'block';

    }else{
        const ticker = document.getElementById('alert-ticker-bar');
        ticker.style.display = 'none';
    }
  } catch (error) {
        console.error('Failed to load AQHI ticker:', error);
        const ticker = document.getElementById('alert-ticker-bar');
        ticker.style.display = 'none';
  }
}

function formatWeather(data) {
    if (!Array.isArray(data)) return [{ type: "weather", text: "⚠️ Weather data error." }];
    return data.map(text => ({ type: "weather", text }));
}
function formatAlerts(data) {
    return data.map(text => ({ type: "alert", text }));
}
function formatNews(data) {
    if (!Array.isArray(data)) return [{ type: "news", text: "⚠️ News data error." }];
    return data.map((item, index) => ({
        type: "news",
        text: `${item.headline}\n${item.summary}\nREAD MORE: ${item.link}`
    }));
}

function formatStocks(data) {
    return Object.entries(data).map(([symbol, info]) => {
        const changeStr = info.change >= 0 ? `+${info.change}` : `${info.change}`;
        const percentStr = info.percent >= 0 ? `(+${info.percent}%)` : `(${info.percent}%)`;
        return {
            type: "stock",
            text: `STOCK UPDATE: ${info.name}:${symbol} - $${info.price} ${percentStr}`
        };
    });
}

function interleaveSlides() {
    allSlides = [];

    // Always group all weather slides together
    allSlides.push(...weatherSlides);

    // Combine news and stock slides
    const mixedSlides = [...newsSlides, ...stockSlides];

    // Shuffle the combined slides
    for (let i = mixedSlides.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [mixedSlides[i], mixedSlides[j]] = [mixedSlides[j], mixedSlides[i]];
    }

    // Add the shuffled news/stock slides after weather
    allSlides.push(...mixedSlides);

}

function updateDateTime() {
    const now = new Date();
    const dateTimeStr = now.toLocaleString("en-CA", { timeZone: "America/Winnipeg" });
    document.getElementById("datetime").textContent = dateTimeStr;
}

(async function loadTrackerIfExists() {
    try {
        const res = await fetch('tracking.html');
        if (!res.ok) {
            console.log('📭 tracking.html not found. Skipping analytics.');
            return;
        }
        const html = await res.text();
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        const scriptTag = tempDiv.querySelector('script');
        if (scriptTag) {
            const newScript = document.createElement('script');
            newScript.src = scriptTag.src;
            newScript.defer = true;
            for (const attr of scriptTag.attributes) {
                if (attr.name !== "src") {
                    newScript.setAttribute(attr.name, attr.value);
                }
            }
            document.head.appendChild(newScript);
            console.log('✅ Tracker loaded successfully.');
        }
    } catch (err) {
        console.error('⚠️ Failed to load tracker:', err);
    }
})();

window.addEventListener('DOMContentLoaded', loadAlertTicker);
window.addEventListener('DOMContentLoaded', loadAQHITicker);
setInterval(updateDateTime, 1000);
setInterval(loadAQHITicker, 60000);
setInterval(loadAlertTicker, 30000);
updateDateTime();
fetchSlides();
setInterval(fetchSlides, 900 * 1000); // Refresh data every 5 minutes