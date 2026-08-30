// --------------------------------------------------
// WEATHER SERVICE
// --------------------------------------------------
//
// This module:
// 1. Fetches live weather data from Open-Meteo.
// 2. Calculates rainfall for the previous 6 hours.
// 3. Calculates rainfall for the previous 24 hours.
// 4. Calculates rainfall forecast for the next 6 hours.
// 5. Calculates rainfall forecast for the next 24 hours.
// 6. Creates 6-hour rainfall intervals.
// 7. Returns environmental parameters for ML prediction.
//
// --------------------------------------------------

const axios = require("axios");

// --------------------------------------------------
// FETCH LIVE WEATHER DATA
// --------------------------------------------------

function getWeatherData(location) {

    return new Promise((resolve, reject) => {

        // --------------------------------------------------
        // VALIDATE LOCATION
        // --------------------------------------------------

        if (!location) {

            return reject(
                new Error("Location is required.")
            );

        }

        const latitude = location.latitude;
        const longitude = location.longitude;


        if (
            latitude === undefined ||
            longitude === undefined
        ) {

            return reject(
                new Error(
                    "Location latitude or longitude is missing."
                )
            );

        }


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
            `&past_days=1` +
            `&timezone=auto`;


        console.log(
            `Fetching Open-Meteo data for coordinates: ${latitude}, ${longitude}`
        );


        // --------------------------------------------------
        // FETCH USING POWERSHELL
        // --------------------------------------------------

        // --------------------------------------------------
        // FETCH USING AXIOS
        // --------------------------------------------------
        // Axios works on both Windows and Linux/Render.
    // This avoids depending on PowerShell.
    // --------------------------------------------------

        axios.get(url, {
            timeout: 20000
            })
        .then(response => {

            console.log("Open-Meteo data received successfully.");

            resolve(response.data);

        })
        .catch(error => {

            console.error(
                "Open-Meteo request error:",
                error.message
            );

            reject(error);

}       );

    });

}



// --------------------------------------------------
// HELPER: SAFE NUMBER
// --------------------------------------------------

function safeNumber(value) {

    if (
        value === null ||
        value === undefined ||
        Number.isNaN(Number(value))
    ) {

        return 0;

    }

    return Number(value);

}



// --------------------------------------------------
// HELPER: ROUND TO 2 DECIMAL PLACES
// --------------------------------------------------

function round(value) {

    return Number(
        safeNumber(value).toFixed(2)
    );

}



// --------------------------------------------------
// PROCESS WEATHER DATA
// --------------------------------------------------

function processWeatherData(weatherData) {

    // --------------------------------------------------
    // VALIDATE RESPONSE
    // --------------------------------------------------

    if (!weatherData) {

        throw new Error(
            "Empty response received from Open-Meteo."
        );

    }


    if (
        !weatherData.current ||
        !weatherData.hourly
    ) {

        throw new Error(
            "Invalid Open-Meteo response."
        );

    }


    const current = weatherData.current;
    const hourly = weatherData.hourly;


    // --------------------------------------------------
    // CURRENT TIME
    // --------------------------------------------------

    const currentTime =
        new Date(current.time);


    // --------------------------------------------------
    // HOURLY ARRAYS
    // --------------------------------------------------

    const hourlyTimes =
        hourly.time || [];

    const hourlyPrecipitation =
        hourly.precipitation || [];



    // ==================================================
    // RAINFALL - LAST 6 HOURS
    // ==================================================

    let rainfallLast6Hours = 0;


    for (
        let i = 0;
        i < hourlyTimes.length;
        i++
    ) {

        const hourTime =
            new Date(hourlyTimes[i]);


        const differenceHours =
            (
                currentTime - hourTime
            ) /
            (1000 * 60 * 60);


        if (
            differenceHours >= 0 &&
            differenceHours <= 6
        ) {

            rainfallLast6Hours +=
                safeNumber(
                    hourlyPrecipitation[i]
                );

        }

    }



    // ==================================================
    // RAINFALL - LAST 24 HOURS
    // ==================================================

    let rainfallLast24Hours = 0;


    for (
        let i = 0;
        i < hourlyTimes.length;
        i++
    ) {

        const hourTime =
            new Date(hourlyTimes[i]);


        const differenceHours =
            (
                currentTime - hourTime
            ) /
            (1000 * 60 * 60);


        if (
            differenceHours >= 0 &&
            differenceHours <= 24
        ) {

            rainfallLast24Hours +=
                safeNumber(
                    hourlyPrecipitation[i]
                );

        }

    }



    // ==================================================
    // RAINFALL FORECAST - NEXT 6 HOURS
    // ==================================================

    let rainfallForecastNext6Hours = 0;


    for (
        let i = 0;
        i < hourlyTimes.length;
        i++
    ) {

        const hourTime =
            new Date(hourlyTimes[i]);


        const differenceHours =
            (
                hourTime - currentTime
            ) /
            (1000 * 60 * 60);


        if (
            differenceHours > 0 &&
            differenceHours <= 6
        ) {

            rainfallForecastNext6Hours +=
                safeNumber(
                    hourlyPrecipitation[i]
                );

        }

    }



    // ==================================================
    // RAINFALL FORECAST - NEXT 24 HOURS
    // ==================================================

    let rainfallForecastNext24Hours = 0;


    for (
        let i = 0;
        i < hourlyTimes.length;
        i++
    ) {

        const hourTime =
            new Date(hourlyTimes[i]);


        const differenceHours =
            (
                hourTime - currentTime
            ) /
            (1000 * 60 * 60);


        if (
            differenceHours > 0 &&
            differenceHours <= 24
        ) {

            rainfallForecastNext24Hours +=
                safeNumber(
                    hourlyPrecipitation[i]
                );

        }

    }



    // ==================================================
    // 6-HOUR RAINFALL INTERVALS
    // ==================================================
    //
    // The hourly precipitation data is grouped into
    // consecutive 6-hour periods.
    //
    // Example:
    //
    // 00:00 - 06:00
    // 06:00 - 12:00
    // 12:00 - 18:00
    // 18:00 - 00:00
    //
    // These intervals are important because the ML
    // training data should use the same time structure.
    //
    // ==================================================

    const rainfall6HourIntervals = [];

    let intervalStart = null;
    let intervalEnd = null;
    let intervalRainfall = 0;


    for (
        let i = 0;
        i < hourlyTimes.length;
        i++
    ) {

        const hourTime =
            new Date(hourlyTimes[i]);


        // --------------------------------------------------
        // Determine the beginning of the 6-hour block
        // --------------------------------------------------

        const blockHour =
            Math.floor(
                hourTime.getHours() / 6
            ) * 6;


        const blockStart =
            new Date(hourTime);

        blockStart.setHours(
            blockHour,
            0,
            0,
            0
        );


        const blockEnd =
            new Date(blockStart);

        blockEnd.setHours(
            blockStart.getHours() + 6
        );


        // --------------------------------------------------
        // Start first interval
        // --------------------------------------------------

        if (intervalStart === null) {

            intervalStart =
                blockStart;

            intervalEnd =
                blockEnd;

            intervalRainfall = 0;

        }


        // --------------------------------------------------
        // New 6-hour interval
        // --------------------------------------------------

        if (
            blockStart.getTime() !==
            intervalStart.getTime()
        ) {

            rainfall6HourIntervals.push({

                start:
                    intervalStart.toISOString(),

                end:
                    intervalEnd.toISOString(),

                rainfall:
                    round(intervalRainfall)

            });


            intervalStart =
                blockStart;

            intervalEnd =
                blockEnd;

            intervalRainfall = 0;

        }


        // --------------------------------------------------
        // Add hourly rainfall
        // --------------------------------------------------

        intervalRainfall +=
            safeNumber(
                hourlyPrecipitation[i]
            );

    }


    // --------------------------------------------------
    // ADD FINAL INTERVAL
    // --------------------------------------------------

    if (intervalStart !== null) {

        rainfall6HourIntervals.push({

            start:
                intervalStart.toISOString(),

            end:
                intervalEnd.toISOString(),

            rainfall:
                round(intervalRainfall)

        });

    }



    // ==================================================
    // SOIL MOISTURE
    // ==================================================

    let soilMoisture = null;


    if (
        current.soil_moisture_0_to_7cm !==
        undefined
    ) {

        soilMoisture =
            safeNumber(
                current.soil_moisture_0_to_7cm
            ) * 100;

    }



    // ==================================================
    // CURRENT RAINFALL
    // ==================================================

    const rainfall =
        safeNumber(
            current.rain
        );



    // ==================================================
    // RETURN ML-READY DATA
    // ==================================================

    return {

        // --------------------------------------------------
        // CURRENT RAINFALL
        // --------------------------------------------------

        rainfall:
            round(rainfall),


        // --------------------------------------------------
        // HISTORICAL RAINFALL
        // --------------------------------------------------

        rainfallLast6Hours:
            round(rainfallLast6Hours),

        rainfallLast24Hours:
            round(rainfallLast24Hours),


        // --------------------------------------------------
        // FORECAST RAINFALL
        // --------------------------------------------------

        rainfallForecastNext6Hours:
            round(
                rainfallForecastNext6Hours
            ),

        rainfallForecastNext24Hours:
            round(
                rainfallForecastNext24Hours
            ),


        // --------------------------------------------------
        // 6-HOUR INTERVAL DATA
        // --------------------------------------------------

        rainfall6HourIntervals:
            rainfall6HourIntervals,


        // --------------------------------------------------
        // ENVIRONMENTAL PARAMETERS
        // --------------------------------------------------

        soilMoisture:
            soilMoisture === null
                ? null
                : round(soilMoisture),

        temperature:
            safeNumber(
                current.temperature_2m
            ),

        humidity:
            safeNumber(
                current.relative_humidity_2m
            ),

        atmosphericPressure:
            safeNumber(
                current.pressure_msl
            ),


        // --------------------------------------------------
        // LOCATION ELEVATION
        // --------------------------------------------------

        elevation:
            safeNumber(
                weatherData.elevation
            ),


        // --------------------------------------------------
        // TIMESTAMP
        // --------------------------------------------------

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