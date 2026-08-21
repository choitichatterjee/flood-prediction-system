// ======================================================
// FLOOD PREDICTION BACKEND - SERVER
// ======================================================

const express = require("express");
const cors = require("cors");

const locations = require("./locations");

const {
    getWeatherData,
    processWeatherData
} = require("./weatherService");

const app = express();

const PORT = 5000;


// ======================================================
// RIVER SERVICE
// ======================================================

let riverService = null;

try {

    riverService = require("./riverService");

    console.log("River service loaded successfully.");

} catch (error) {

    console.warn(
        "River service not available. Weather data will continue normally."
    );

}


// ======================================================
// MIDDLEWARE
// ======================================================

app.use(cors());

app.use(express.json());


// ======================================================
// ROOT ROUTE
// ======================================================

app.get("/", (req, res) => {

    res.json({

        message: "Flood Prediction Backend is running",

        status: "OK"

    });

});


// ======================================================
// LOCATIONS ROUTE
// ======================================================

app.get("/api/locations", (req, res) => {

    try {

        res.json({

            locations: locations

        });

    }

    catch (error) {

        console.error(
            "Locations API error:",
            error
        );

        res.status(500).json({

            error: "Unable to fetch locations."

        });

    }

});


// ======================================================
// LIVE ENVIRONMENTAL DATA ROUTE
// ======================================================

app.get("/api/data", async (req, res) => {

    try {

        // --------------------------------------------------
        // GET LOCATION ID
        // --------------------------------------------------

        const locationId = req.query.location;


        if (!locationId) {

            return res.status(400).json({

                error:
                    "Location parameter is required."

            });

        }


        // --------------------------------------------------
        // FIND LOCATION
        // --------------------------------------------------

        const location = locations.find(

            item =>
                item.id === locationId

        );


        if (!location) {

            return res.status(404).json({

                error:
                    `Location '${locationId}' not found.`

            });

        }


        console.log(
            `Fetching live data for ${location.name}...`
        );


        // ==================================================
        // FETCH LIVE OPEN-METEO DATA
        // ==================================================

        // IMPORTANT:
        // weatherService.js expects the COMPLETE
        // location object, not latitude and longitude
        // separately.

        const rawWeatherData =
            await getWeatherData(location);


        // ==================================================
        // PROCESS WEATHER DATA
        // ==================================================

        const weather =
            processWeatherData(rawWeatherData);


        // ==================================================
        // DEFAULT RIVER DATA
        // ==================================================

        let riverData = {

            waterLevel: null,

            waterLevelStation: null,

            waterLevelRiver: null,

            waterLevelTimestamp: null,

            waterLevelSource: null,

            waterLevelAvailable: false

        };


        // ==================================================
        // FETCH RIVER DATA IF SERVICE EXISTS
        // ==================================================

        if (riverService) {

            try {

                // ------------------------------------------
                // getRiverData()
                // ------------------------------------------

                if (
                    typeof riverService.getRiverData ===
                    "function"
                ) {

                    const result =
                        await riverService.getRiverData(
                            location
                        );


                    if (result) {

                        riverData = {

                            waterLevel:
                                result.waterLevel ?? null,

                            waterLevelStation:
                                result.waterLevelStation ?? null,

                            waterLevelRiver:
                                result.waterLevelRiver ?? null,

                            waterLevelTimestamp:
                                result.waterLevelTimestamp ?? null,

                            waterLevelSource:
                                result.waterLevelSource ?? null,

                            waterLevelAvailable:
                                result.waterLevelAvailable ??
                                false

                        };

                    }

                }


                // ------------------------------------------
                // getRiverLevel()
                // ------------------------------------------

                else if (
                    typeof riverService.getRiverLevel ===
                    "function"
                ) {

                    const result =
                        await riverService.getRiverLevel(
                            location
                        );


                    if (result) {

                        riverData = {

                            waterLevel:
                                result.waterLevel ?? null,

                            waterLevelStation:
                                result.waterLevelStation ?? null,

                            waterLevelRiver:
                                result.waterLevelRiver ?? null,

                            waterLevelTimestamp:
                                result.waterLevelTimestamp ?? null,

                            waterLevelSource:
                                result.waterLevelSource ?? null,

                            waterLevelAvailable:
                                result.waterLevelAvailable ??
                                false

                        };

                    }

                }

            }

            catch (riverError) {

                console.error(
                    "River data error:",
                    riverError
                );

                // Do NOT stop the weather API if
                // river data is unavailable.

            }

        }


        // ==================================================
        // RETURN COMPLETE RESPONSE
        // ==================================================

        res.json({

            location: {

                id:
                    location.id,

                name:
                    location.name,

                district:
                    location.district,

                weatherStation:
                    location.weatherStation,

                latitude:
                    location.latitude,

                longitude:
                    location.longitude

            },


            environmentalData: {

                // ==========================================
                // CURRENT RAINFALL
                // ==========================================

                rainfall:
                    weather.rainfall,


                // ==========================================
                // HISTORICAL RAINFALL
                // ==========================================

                rainfallLast6Hours:
                    weather.rainfallLast6Hours,

                rainfallLast24Hours:
                    weather.rainfallLast24Hours,


                // ==========================================
                // RAINFALL FORECAST
                // ==========================================

                rainfallForecastNext6Hours:
                    weather.rainfallForecastNext6Hours,

                rainfallForecastNext24Hours:
                    weather.rainfallForecastNext24Hours,


                // ==========================================
                // ENVIRONMENTAL CONDITIONS
                // ==========================================

                soilMoisture:
                    weather.soilMoisture,

                temperature:
                    weather.temperature,

                humidity:
                    weather.humidity,

                atmosphericPressure:
                    weather.atmosphericPressure,

                elevation:
                    weather.elevation,


                // ==========================================
                // RIVER / WATER LEVEL
                // ==========================================

                waterLevel:
                    riverData.waterLevel,

                waterLevelStation:
                    riverData.waterLevelStation,

                waterLevelRiver:
                    riverData.waterLevelRiver,

                waterLevelTimestamp:
                    riverData.waterLevelTimestamp,

                waterLevelSource:
                    riverData.waterLevelSource,

                waterLevelAvailable:
                    riverData.waterLevelAvailable,


                // ==========================================
                // UPDATE TIME
                // ==========================================

                lastUpdated:
                    weather.lastUpdated

            }

        });


        console.log(
            `Live data successfully returned for ${location.name}.`
        );

    }


    // ==================================================
    // ERROR HANDLING
    // ==================================================

    catch (error) {

        console.error(
            "Environmental data error:",
            error
        );


        res.status(500).json({

            error:
                "Unable to fetch live environmental data.",

            details:
                error.message

        });

    }

});


// ======================================================
// 404 ROUTE
// ======================================================

app.use((req, res) => {

    res.status(404).json({

        error:
            "Route not found."

    });

});


// ======================================================
// START SERVER
// ======================================================

app.listen(PORT, () => {

    console.log("");

    console.log(
        "=========================================="
    );

    console.log(
        "   FLOOD PREDICTION BACKEND"
    );

    console.log(
        "=========================================="
    );

    console.log(
        `Server running at http://localhost:${PORT}`
    );

    console.log(
        `Locations: http://localhost:${PORT}/api/locations`
    );

    console.log(
        `Data: http://localhost:${PORT}/api/data?location=jalpaiguri`
    );

    console.log(
        "=========================================="
    );

    console.log("");

});