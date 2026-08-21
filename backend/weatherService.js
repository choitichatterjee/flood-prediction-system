// --------------------------------------------------
// WEATHER SERVICE
// --------------------------------------------------

// This module:
// 1. Fetches live weather data from Open-Meteo.
// 2. Calculates rainfall for the previous 6 hours.
// 3. Calculates rainfall for the previous 24 hours.
// 4. Calculates rainfall forecast for the next 6 hours.
// 5. Calculates rainfall forecast for the next 24 hours.
// 6. Converts the data into ML-ready inputs.

const { execFile } = require("child_process");


// --------------------------------------------------
// FETCH LIVE WEATHER DATA
// --------------------------------------------------

function getWeatherData(location) {

    return new Promise((resolve, reject) => {

        const latitude = location.latitude;
        const longitude = location.longitude;


        // --------------------------------------------------
        // OPEN-METEO API URL
        // --------------------------------------------------

        const url =
            `https://api.open-meteo.com/v1/forecast` +
            `?latitude=${latitude}` +
            `&longitude=${longitude}` +
            `&current=` +
            `temperature_2m,` +
            `relative_humidity_2m,` +
            `pressure_msl,` +
            `rain,` +
            `soil_moisture_0_to_7cm` +
            `&hourly=rain,precipitation` +
            `&forecast_days=2` +
            `&timezone=auto`;


        // --------------------------------------------------
        // FETCH USING POWERSHELL
        // --------------------------------------------------

        execFile(
            "powershell.exe",

            [
                "-NoProfile",
                "-Command",
                `Invoke-RestMethod -Uri '${url}' -Method GET | ConvertTo-Json -Compress`
            ],

            {
                timeout: 20000,
                maxBuffer: 1024 * 1024
            },

            (error, stdout, stderr) => {

                if (error) {

                    console.error(
                        "Open-Meteo PowerShell error:",
                        stderr || error.message
                    );

                    return reject(error);
                }


                // --------------------------------------------------
                // PARSE RESPONSE
                // --------------------------------------------------

                try {

                    const data = JSON.parse(stdout);

                    resolve(data);

                } catch (parseError) {

                    console.error(
                        "Unable to parse Open-Meteo response:",
                        parseError.message
                    );

                    reject(parseError);
                }
            }
        );
    });
}



// --------------------------------------------------
// PROCESS WEATHER DATA
// --------------------------------------------------

function processWeatherData(weatherData) {

    const current = weatherData.current;
    const hourly = weatherData.hourly;


    // --------------------------------------------------
    // CURRENT TIME
    // --------------------------------------------------

    const currentTime = new Date(current.time);


    // --------------------------------------------------
    // RAINFALL - LAST 6 HOURS
    // --------------------------------------------------

    let rainfallLast6Hours = 0;


    for (let i = 0; i < hourly.time.length; i++) {

        const hourTime = new Date(hourly.time[i]);

        const differenceHours =
            (currentTime - hourTime) / (1000 * 60 * 60);


        // Include rainfall from the previous 6 hours
        // and the current hour.

        if (
            differenceHours >= 0 &&
            differenceHours <= 6
        ) {

            rainfallLast6Hours +=
                hourly.precipitation[i] || 0;
        }
    }



    // --------------------------------------------------
    // RAINFALL - LAST 24 HOURS
    // --------------------------------------------------

    let rainfallLast24Hours = 0;


    for (let i = 0; i < hourly.time.length; i++) {

        const hourTime = new Date(hourly.time[i]);

        const differenceHours =
            (currentTime - hourTime) / (1000 * 60 * 60);


        // Include rainfall from the previous 24 hours
        // and the current hour.

        if (
            differenceHours >= 0 &&
            differenceHours <= 24
        ) {

            rainfallLast24Hours +=
                hourly.precipitation[i] || 0;
        }
    }



    // --------------------------------------------------
    // RAINFALL FORECAST - NEXT 6 HOURS
    // --------------------------------------------------

    let rainfallForecastNext6Hours = 0;


    for (let i = 0; i < hourly.time.length; i++) {

        const hourTime = new Date(hourly.time[i]);

        const differenceHours =
            (hourTime - currentTime) /
            (1000 * 60 * 60);


        // Only future values between 0 and 6 hours
        // are included.

        if (
            differenceHours > 0 &&
            differenceHours <= 6
        ) {

            rainfallForecastNext6Hours +=
                hourly.precipitation[i] || 0;
        }
    }



    // --------------------------------------------------
    // RAINFALL FORECAST - NEXT 24 HOURS
    // --------------------------------------------------

    let rainfallForecastNext24Hours = 0;


    for (let i = 0; i < hourly.time.length; i++) {

        const hourTime = new Date(hourly.time[i]);

        const differenceHours =
            (hourTime - currentTime) /
            (1000 * 60 * 60);


        // Only future values between 0 and 24 hours
        // are included.

        if (
            differenceHours > 0 &&
            differenceHours <= 24
        ) {

            rainfallForecastNext24Hours +=
                hourly.precipitation[i] || 0;
        }
    }



    // --------------------------------------------------
    // SOIL MOISTURE
    // --------------------------------------------------

    // Open-Meteo provides soil moisture as m³/m³.
    //
    // Example:
    // 0.382 → 38.2 %

    const soilMoisture =
        current.soil_moisture_0_to_7cm * 100;



    // --------------------------------------------------
    // ROUND FORECAST VALUES
    // --------------------------------------------------

    // Keep the response clean and avoid long
    // floating-point values.

    rainfallLast6Hours =
        Number(rainfallLast6Hours.toFixed(2));

    rainfallLast24Hours =
        Number(rainfallLast24Hours.toFixed(2));

    rainfallForecastNext6Hours =
        Number(rainfallForecastNext6Hours.toFixed(2));

    rainfallForecastNext24Hours =
        Number(rainfallForecastNext24Hours.toFixed(2));



    // --------------------------------------------------
    // RETURN ML-READY DATA
    // --------------------------------------------------

    return {

        // Current rainfall.
        rainfall:
            current.rain,


        // Historical rainfall.
        rainfallLast6Hours:
            rainfallLast6Hours,

        rainfallLast24Hours:
            rainfallLast24Hours,


        // Forecast rainfall.
        rainfallForecastNext6Hours:
            rainfallForecastNext6Hours,

        rainfallForecastNext24Hours:
            rainfallForecastNext24Hours,


        // Environmental conditions.
        soilMoisture:
            Number(soilMoisture.toFixed(2)),

        temperature:
            current.temperature_2m,

        humidity:
            current.relative_humidity_2m,

        atmosphericPressure:
            current.pressure_msl,


        // Location elevation.
        elevation:
            weatherData.elevation,


        // Timestamp.
        lastUpdated:
            current.time
    };
}



// --------------------------------------------------
// EXPORT FUNCTIONS
// --------------------------------------------------

module.exports = {
    getWeatherData,
    processWeatherData
};