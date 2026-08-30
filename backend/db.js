console.log("DB HOST:", process.env.DB_HOST);
console.log("DB PORT:", process.env.DB_PORT);
console.log("CA FILE:", path.join(__dirname, "ca.pem"));
console.log("CA EXISTS:", fs.existsSync(path.join(__dirname, "ca.pem")));
const mysql = require("mysql2/promise");
const path = require("path");
const fs = require("fs");

require("dotenv").config({
    path: path.join(__dirname, ".env")
});

const pool = mysql.createPool({
    host: process.env.DB_HOST,
    port: process.env.DB_PORT,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME,

    // Use Aiven's CA certificate for secure SSL connection
    ssl: {
        ca: fs.readFileSync(path.join(__dirname, "ca.pem"))
    },

    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

module.exports = pool;