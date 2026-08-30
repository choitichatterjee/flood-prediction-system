const nodemailer = require("nodemailer");
const pool = require("../backend/db");
require("dotenv").config({ path: path.join(__dirname, "../backend/.env") });

/*
 * Get all users registered in MySQL for a particular district.
 */
async function getUsersByDistrict(district) {
    try {
        const [users] = await pool.execute(
            `
            SELECT name, email, district
            FROM users
            WHERE LOWER(TRIM(district)) = LOWER(TRIM(?))
            `,
            [district]
        );

        return users;

    } catch (error) {
        console.error(
            "Unable to read users from MySQL:",
            error.message
        );

        return [];
    }
}

/*
 * Send email alerts only when the predicted risk is HIGH.
 */
async function sendHighRiskAlert(district, prediction) {

    // Only send notifications for HIGH flood risk.
    if (
        !prediction ||
        String(prediction.riskLevel).toUpperCase() !== "HIGH"
    ) {
        return;
    }

    // Get registered users directly from MySQL.
    const users = await getUsersByDistrict(district);

    if (users.length === 0) {
        console.log(`No registered users found for ${district}.`);
        return;
    }

    // Check email configuration.
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

    const probability =
        Number(prediction.floodProbability || 0) * 100;

    // Send the alert to every registered user in the affected district.
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

            console.log(
                `HIGH-risk alert sent to ${user.email} for ${district}.`
            );

        } catch (error) {

            console.error(
                `Unable to send alert to ${user.email}:`,
                error.message
            );
        }
    }
}

module.exports = { sendHighRiskAlert };