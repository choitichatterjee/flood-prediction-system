// ======================================================
// FLOOD PREDICTION BACKEND - SERVER
// ======================================================

const express = require("express");
const cors = require("cors");
const { spawn } = require("child_process");
const path = require("path");

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
// LIVE ENVIRONMENTAL DATA + LSTM PREDICTION
// ======================================================

app.get("/api/data", async (req, res) => {

    try {

        // ==================================================
        // GET LOCATION ID
        // ==================================================

        const locationId = req.query.location;


        if (!locationId) {

            return res.status(400).json({

                error:
                    "Location parameter is required."

            });

        }


        // ==================================================
        // FIND LOCATION
        // ==================================================

        const location = locations.find(
            item => item.id === locationId
        );


        if (!location) {

            return res.status(404).json({

                error:
                    `Location '${locationId}' not found.`

            });

        }


        console.log("");
        console.log(
            `Fetching live data for ${location.name}...`
        );


        // ==================================================
        // FETCH LIVE OPEN-METEO DATA
        // ==================================================

        const rawWeatherData =
            await getWeatherData(location);


        // ==================================================
        // PROCESS WEATHER DATA
        // ==================================================

        const weather =
            processWeatherData(rawWeatherData);


        console.log(
            "Live weather data received."
        );


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
        // FETCH RIVER DATA
        // ==================================================

        if (riverService) {

            try {

                if (
                    typeof riverService.getRiverData ===
                    "function"
                ) {

                    const result =
                        await riverService.getRiverData(
                            location.id
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

                else if (
                    typeof riverService.getRiverLevel ===
                    "function"
                ) {

                    const result =
                        await riverService.getRiverLevel(
                            location.id
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

            }

        }


        // ==================================================
        // PREPARE WATER LEVEL FOR ML
        // ==================================================
        //
        // The current training dataset has no usable
        // water-level values.
        //
        // Therefore, when live water level is unavailable,
        // use 0.0 for the ML input.
        //
        // The API response still correctly reports
        // waterLevel as null.
        //
        // ==================================================

        const waterLevelForML =
            riverData.waterLevel === null ||
            riverData.waterLevel === undefined
                ? 0.0
                : Number(riverData.waterLevel);


        console.log(
            `Water level used for ML: ${waterLevelForML}`
        );


        // ==================================================
        // LSTM FLOOD PREDICTION
        // ==================================================

        let floodPrediction = null;


        try {

            // --------------------------------------------------
            // CREATE MODEL INPUT
            // --------------------------------------------------

            const predictionInput = {

                rainfall_1h_mm:
                    weather.rainfall,

                rainfall_6h_mm:
                    weather.rainfallLast6Hours,

                rainfall_24h_mm:
                    weather.rainfallLast24Hours,

                soil_moisture_pct:
                    weather.soilMoisture,

                temperature_c:
                    weather.temperature,

                humidity_pct:
                    weather.humidity,

                pressure_hpa:
                    weather.atmosphericPressure,

                water_level_m:
                    waterLevelForML,

                elevation_m:
                    weather.elevation

            };


            console.log(
                "Sending live data to LSTM..."
            );

            console.log(
                "LSTM input:",
                predictionInput
            );


            // --------------------------------------------------
            // PYTHON SCRIPT PATH
            // --------------------------------------------------

            const projectRoot =
                path.join(__dirname, "..");


            const scriptPath =
                path.join(
                    projectRoot,
                    "ml",
                    "predict_lstm_api.py"
                );


            console.log(
                "Python script:",
                scriptPath
            );

            console.log(
                "Python working directory:",
                projectRoot
            );


            // --------------------------------------------------
            // START PYTHON
            // --------------------------------------------------

            const pythonProcess = spawn(
                "python",
                [scriptPath],
                {
                    cwd: projectRoot
                }
            );


            let output = "";
            let errorOutput = "";


            // --------------------------------------------------
            // SEND DATA TO PYTHON
            // --------------------------------------------------

            pythonProcess.stdin.write(
                JSON.stringify(predictionInput)
            );

            pythonProcess.stdin.end();


            console.log(
                "Waiting for LSTM Python response..."
            );


            // --------------------------------------------------
            // RECEIVE PYTHON STDOUT
            // --------------------------------------------------

            pythonProcess.stdout.on(
                "data",
                (data) => {

                    output += data.toString();

                }
            );


            // --------------------------------------------------
            // RECEIVE PYTHON STDERR
            // --------------------------------------------------

            pythonProcess.stderr.on(
                "data",
                (data) => {

                    errorOutput += data.toString();

                }
            );


            // --------------------------------------------------
            // WAIT FOR PYTHON TO FINISH
            // --------------------------------------------------

            await new Promise((resolve) => {

                pythonProcess.on(
                    "close",
                    (code) => {

                        console.log(
                            "Python process closed with code:",
                            code
                        );


                        console.log(
                            "Python stdout:",
                            output
                        );


                        console.log(
                            "Python stderr:",
                            errorOutput
                        );


                        // ------------------------------------------
                        // SUCCESS
                        // ------------------------------------------

                        if (code === 0) {

                            try {

                                floodPrediction =
                                    JSON.parse(
                                        output.trim()
                                    );


                                console.log(
                                    "LSTM prediction:",
                                    floodPrediction
                                );

                            }

                            catch (parseError) {

                                console.error(
                                    "Unable to parse LSTM response:",
                                    parseError
                                );

                                console.error(
                                    "Raw Python output:",
                                    output
                                );

                            }

                        }

                        // ------------------------------------------
                        // PYTHON ERROR
                        // ------------------------------------------

                        else {

                            console.error(
                                "LSTM prediction failed."
                            );

                            console.error(
                                "Python exit code:",
                                code
                            );

                            console.error(
                                "Python error:",
                                errorOutput
                            );

                        }


                        resolve();

                    }

                );

            });

        }

        catch (predictionError) {

            console.error(
                "Live LSTM prediction error:",
                predictionError
            );

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
                // LSTM FLOOD PREDICTION
                // ==========================================

                floodPrediction:
                    floodPrediction,


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
// LSTM FLOOD PREDICTION ROUTE
// ======================================================

app.post("/api/predict", async (req, res) => {

    try {

        const inputData = req.body;


        // ==================================================
        // WATER LEVEL DEFAULT
        // ==================================================

        if (
            inputData.water_level_m === null ||
            inputData.water_level_m === undefined
        ) {

            inputData.water_level_m = 0.0;

        }


        // ==================================================
        // REQUIRED MODEL INPUTS
        // ==================================================

        const requiredFields = [

            "rainfall_1h_mm",
            "rainfall_6h_mm",
            "rainfall_24h_mm",
            "soil_moisture_pct",
            "temperature_c",
            "humidity_pct",
            "pressure_hpa",
            "water_level_m",
            "elevation_m"

        ];


        // ==================================================
        // CHECK INPUTS
        // ==================================================

        for (const field of requiredFields) {

            if (
                inputData[field] === undefined ||
                inputData[field] === null
            ) {

                return res.status(400).json({

                    error:
                        `Missing required field: ${field}`

                });

            }

        }


        console.log(
            "Received prediction request:"
        );

        console.log(
            inputData
        );


        // ==================================================
        // PYTHON SCRIPT PATH
        // ==================================================

        const projectRoot =
            path.join(__dirname, "..");


        const scriptPath =
            path.join(
                projectRoot,
                "ml",
                "predict_lstm_api.py"
            );


        // ==================================================
        // START PYTHON
        // ==================================================

        const pythonProcess = spawn(
            "python",
            [scriptPath],
            {
                cwd: projectRoot
            }
        );


        let output = "";
        let errorOutput = "";


        // ==================================================
        // SEND DATA TO PYTHON
        // ==================================================

        pythonProcess.stdin.write(
            JSON.stringify(inputData)
        );

        pythonProcess.stdin.end();


        // ==================================================
        // RECEIVE OUTPUT
        // ==================================================

        pythonProcess.stdout.on(
            "data",
            (data) => {

                output += data.toString();

            }
        );


        // ==================================================
        // RECEIVE ERRORS
        // ==================================================

        pythonProcess.stderr.on(
            "data",
            (data) => {

                errorOutput += data.toString();

            }
        );


        // ==================================================
        // PYTHON FINISHED
        // ==================================================

        pythonProcess.on(
            "close",
            (code) => {

                console.log(
                    "Prediction Python process closed:",
                    code
                );


                console.log(
                    "Prediction stdout:",
                    output
                );


                console.log(
                    "Prediction stderr:",
                    errorOutput
                );


                if (code !== 0) {

                    console.error(
                        "Python prediction error:",
                        errorOutput
                    );


                    return res.status(500).json({

                        error:
                            "LSTM prediction failed.",

                        details:
                            errorOutput

                    });

                }


                try {

                    const prediction =
                        JSON.parse(
                            output.trim()
                        );


                    console.log(
                        "LSTM prediction:",
                        prediction
                    );


                    res.json({

                        success: true,

                        prediction:
                            prediction

                    });

                }

                catch (parseError) {

                    console.error(
                        "Prediction JSON error:",
                        parseError
                    );


                    console.error(
                        "Python output:",
                        output
                    );


                    res.status(500).json({

                        error:
                            "Invalid prediction response."

                    });

                }

            }

        );

    }

    catch (error) {

        console.error(
            "Prediction API error:",
            error
        );


        res.status(500).json({

            error:
                "Unable to run flood prediction.",

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
        "       FLOOD PREDICTION BACKEND"
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