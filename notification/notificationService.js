const fs = require("fs");
const path = require("path");
const nodemailer = require("nodemailer");
require("dotenv").config({ path: path.join(__dirname, ".env") });

const USERS_FILE = path.join(__dirname, "users.json");

function getUsers() {
    try {
        return JSON.parse(fs.readFileSync(USERS_FILE, "utf8"));
    } catch (error) {
        console.error("Unable to read notification users:", error.message);
        return [];
    }
}

async function sendHighRiskAlert(district, prediction) {
    // Send emails only for HIGH risk.
    if (!prediction || String(prediction.riskLevel).toUpperCase() !== "HIGH") {
        return;
    }

    const users = getUsers().filter(
        user => String(user.district).trim().toLowerCase() === String(district).trim().toLowerCase()
    );

    if (users.length === 0) {
        console.log(`No registered users found for ${district}.`);
        return;
    }

    if (!process.env.EMAIL_USER || !process.env.EMAIL_PASS) {
        console.error("EMAIL_USER and EMAIL_PASS are not configured.");
        return;
    }

    const transporter = nodemailer.createTransport({
        service: "gmail",
        auth: {
            user: process.env.EMAIL_USER,
            pass: process.env.EMAIL_PASS
        }
    });

    const probability = Number(prediction.floodProbability || 0) * 100;

    for (const user of users) {
        try {
            await transporter.sendMail({
                from: process.env.EMAIL_USER,
                to: user.email,
                subject: `🚨 HIGH Flood Risk Alert - ${district}`,
                text:
                    `Hello ${user.name || "User"},\n\n` +
                    `A HIGH flood risk has been predicted for ${district}.\n\n` +
                    `Flood probability: ${probability.toFixed(2)}%\n` +
                    `Risk level: HIGH\n\n` +
                    `Please take appropriate precautions and follow local authorities' instructions.\n\n` +
                    `FloodGuard AI`
            });

            console.log(`HIGH-risk alert sent to ${user.email} for ${district}.`);
        } catch (error) {
            console.error(`Unable to send alert to ${user.email}:`, error.message);
        }
    }
}

module.exports = { sendHighRiskAlert };
