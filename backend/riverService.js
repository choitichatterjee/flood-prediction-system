```javascript
// --------------------------------------------------
// RIVER SERVICE
// --------------------------------------------------
//
// This module is responsible for river water-level data.
//
// At the moment, the official CWC live API endpoint for
// our selected stations has not yet been connected.
//
// Therefore this service:
// - Keeps the original five project locations.
// - Keeps the relevant river/station mapping.
// - Does NOT generate fake water-level values.
// - Returns null when live river data is unavailable.
//
// The weather system continues to work independently.
//
// --------------------------------------------------


// --------------------------------------------------
// RIVER STATION MAPPING
// --------------------------------------------------

const riverStations = {

    // Jalpaiguri
    jalpaiguri: {
        station: "Domohani",
        river: "Teesta"
    },

    // Cooch Behar
    "cooch-behar": {
        station: "Ghughumari",
        river: "Torsa"
    },

    // Alipurduar
    alipurduar: {
        station: "Hasimara",
        river: "Torsa"
    },

    // Kalimpong
    kalimpong: {
        station: "Teesta",
        river: "Teesta"
    },

    // Malda
    malda: {
        station: "Malda",
        river: "Mahananda"
    }

};


// --------------------------------------------------
// GET RIVER DATA
// --------------------------------------------------

async function getRiverData(locationId) {

    const station =
        riverStations[locationId];


    // --------------------------------------------------
    // LOCATION NOT FOUND
    // --------------------------------------------------

    if (!station) {

        return {

            waterLevel: null,

            waterLevelStation: null,

            waterLevelRiver: null,

            waterLevelTimestamp: null,

            waterLevelSource: null,

            waterLevelAvailable: false

        };

    }


    // --------------------------------------------------
    // LIVE CWC DATA NOT CONNECTED YET
    // --------------------------------------------------
    //
    // We deliberately return null here rather than
    // inventing a water-level value.
    //

    return {

        waterLevel: null,

        waterLevelStation:
            station.station,

        waterLevelRiver:
            station.river,

        waterLevelTimestamp:
            null,

        waterLevelSource:
            "Central Water Commission",

        waterLevelAvailable:
            false

    };

}


// --------------------------------------------------
// EXPORT
// --------------------------------------------------

module.exports = {

    getRiverData

};
```
