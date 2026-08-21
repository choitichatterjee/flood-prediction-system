// --------------------------------------------------
// WEST BENGAL FLOOD PREDICTION LOCATIONS
// --------------------------------------------------

// This file contains the five geographical regions
// supported by our flash-flood prediction prototype.
//
// Each location contains:
// - A unique ID
// - Display name
// - District name
// - Weather station name
// - Latitude and longitude
//
// The coordinates will later be used to retrieve
// live environmental data from Open-Meteo.

const locations = [

    // --------------------------------------------------
    // 1. JALPAIGURI
    // --------------------------------------------------

    {
        id: "jalpaiguri",
        name: "Jalpaiguri",
        district: "Jalpaiguri",
        weatherStation: "IMD Jalpaiguri",
        latitude: 26.5167,
        longitude: 88.7333
    },


    // --------------------------------------------------
    // 2. COOCH BEHAR
    // --------------------------------------------------

    {
        id: "cooch-behar",
        name: "Cooch Behar",
        district: "Cooch Behar",
        weatherStation: "IMD Cooch Behar",
        latitude: 26.3452,
        longitude: 89.4482
    },


    // --------------------------------------------------
    // 3. ALIPURDUAR
    // --------------------------------------------------

    {
        id: "alipurduar",
        name: "Alipurduar",
        district: "Alipurduar",
        weatherStation: "IMD Alipurduar",
        latitude: 26.4919,
        longitude: 89.5271
    },


    // --------------------------------------------------
    // 4. KALIMPONG
    // --------------------------------------------------

    {
        id: "kalimpong",
        name: "Kalimpong",
        district: "Kalimpong",
        weatherStation: "IMD Kalimpong",
        latitude: 27.0667,
        longitude: 88.4667
    },


    // --------------------------------------------------
    // 5. MALDA
    // --------------------------------------------------

    {
        id: "malda",
        name: "Malda",
        district: "Malda",
        weatherStation: "IMD Malda",
        latitude: 25.0108,
        longitude: 88.1411
    }
];


// --------------------------------------------------
// EXPORT LOCATIONS
// --------------------------------------------------

// Make the location list available to other backend
// modules such as server.js and weatherService.js.

module.exports = locations;