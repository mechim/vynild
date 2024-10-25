const express = require('express');
const axios = require('axios');
const redis = require('redis');

const app = express();
// Middleware to parse JSON body
app.use(express.json());

// Load environment variables
require('dotenv').config();

const PORT = process.env.PORT;
const SERV_REST_PORT = process.env.SERV_REST_PORT;
const SERVER_TIMEOUT_MS = process.env.SERV_TIMEOUT_MS;
const MAX_CONCURRENT_REQUESTS = process.env.MAX_CONCURRENT_REQUESTS;
const USER_SERVICE_URL = process.env.USER_SERVICE_URL;
const REVIEW_SERVICE_URL = process.env.REVIEW_SERVICE_URL;
const SERVICE_METADATA_URL = process.env.SERVICE_METADATA_URL; // Redis URL storing metadata
const ROUND_ROBIN = true;

const FAIL_COUNT_KEY = "fail_count:"; // circuit breaker
const CURRENT_LOAD_KEY = "current_load:";// health
const CONCURRENT_REQUESTS_KEY = "concurrent_requests:"; //

//Redis client setup
const redisClient = redis.createClient({ url: SERVICE_METADATA_URL });
redisClient.connect();

//task limiter
async function limitTasks(ip){
    const newKey = CONCURRENT_REQUESTS_KEY + ip;
    let concurrent = await redisClient.get(newKey, 0);
    concurrent = concurrent ? parseInt(concurrent, 10) : 0;

    if (concurrent === 0){
        await redisClient.set(newKey, 1,'EX', 1);
    } else {
        await redisClient.incr(newKey);
    }

    if (concurrent >= MAX_CONCURRENT_REQUESTS){
        return (new Error(`TASK LIMITER LIMITED THE TASKS`));
    }
}

//health monitoring
async function writeCurrentLoad(ip){
    const newKey = CURRENT_LOAD_KEY + ip;
    let concurrent = await redisClient.get(newKey);
    concurrent = concurrent ? parseInt(concurrent, 10) : 0;

    if (concurrent === 0){
        await redisClient.set(newKey, 1,'EX', 1);
    } else {
        await redisClient.incr(newKey);
    }
    //magic number 2
    if (concurrent >= 2){
        console.log(`ALERT!!! ${ip} HAS TOO MANY TASKS PER MINUTE IM SCARED`);
    }
}

//circuit breaker
async function circuitBreak(ip, serviceType){
    const newKey = FAIL_COUNT_KEY + ip;
    let concurrent = await redisClient.get(newKey);
    concurrent = concurrent ? parseInt(concurrent, 10) : 0;
    
    if (concurrent === 0){
        await redisClient.set(newKey, 1,'EX', 1);
    } else {
        await redisClient.incr(newKey);
    }
    //magic number 3
    if (concurrent >= 0){
        console.log(`${ip} ETA HUYNA ZAFEYLILASY BOLSHE 3 RAZ`);
        const redisKey = `service:${serviceType}`;
        redisClient.lRem(redisKey, 0, ip);
    }

}

async function shutdown(signal) {
    console.log(`Received ${signal}. Closing Redis and HTTP server...`);
    await redisClient.quit();
    server.close(() => {
        console.log('Express server closed.');
        process.exit(0);
    });
}

['SIGINT', 'SIGTERM'].forEach(signal => process.on(signal, () => shutdown(signal)));

app.use(express.json());

// Status endpoint
app.get('/ping', (req, res) => {
    res.status(200).json({ message: `API Gateway running at http://127.0.0.1:${PORT} is alive!` });
});

let usersIndex = 0;
let reviewsIndex = 0;

async function getServiceIps(serviceType){
    const redisKey = `service:${serviceType}`;
    const ipArray = await redisClient.lRange(redisKey, 0, -1);
    return ipArray;
} 

// Route to User Service
app.use('/user-service', async (req, res, next) => {
    let ip;
    try {
       const ips = await getServiceIps('user');
        
        if (ips.length === 0){
            return res.status(503).json({detail: "No available services ^^"});
        }
        if (ROUND_ROBIN){
             // round robin
            usersIndex = (usersIndex + 1) % ips.length;
        } else {
            // service load
            let minLoad = MAX_CONCURRENT_REQUESTS+1;
            let minIp;
            for(let i = 0; i < ips.length; i++){
                // console.log(`ip ${ips[i]}`);
                const newKey = CONCURRENT_REQUESTS_KEY + ips[i];
                // console.log(`new key ${newKey}`);
                let concurrent = await redisClient.get(newKey);
                concurrent = concurrent ? parseInt(concurrent, 10) : 0;
                // console.log(`CONCURRENT: ${concurrent} MIN LOAD ${minLoad}`);
                if (concurrent < minLoad){
                    minLoad = concurrent;
                    minIp = i;
                }
            }
            usersIndex = minIp;
            // console.log(`MIN IP ${minIp}`)
            // end service load
        }
       
        ip = ips[usersIndex];

        await limitTasks(ip);
        await writeCurrentLoad(ip);
        
        const serviceUrl = `http://${ip}:${SERV_REST_PORT}/${req.url.slice(1)}`;
        const response = await axios({
            method: req.method,
            url: serviceUrl,
            data: req.body,
            headers: req.headers,
            timeout: SERVER_TIMEOUT_MS,
        });

        res.status(response.status).send(response.data);

    } catch (error) {
        if (error.code === 'ECONNABORTED') {
            await circuitBreak(ip, 'user');
            res.status(504).json({ detail: "Request timed out." });
        } else if (error.message === "TASK LIMITER LIMITED THE TASKS"){
            res.status(503).json({detail: error.message})
        }
         else {
            // Extract details from the error response if it exists
            const errorResponse = error.response?.data || { detail: error.message };

            // Forward the status code and error details from the service
            res.status(error.response?.status || 500).json(errorResponse);
        }
    } finally{
        if (ip){
            await redisClient.decr(CONCURRENT_REQUESTS_KEY+ip);
        }
    }
});

// Route to Review Service
app.use('/review-service', async (req, res, next) => {
    let ip;
    try {
        const ips = await getServiceIps('review');
        
        if (ips.length === 0){
            return res.status(503).json({detail: "No available services ^^"});
        }

        if (ROUND_ROBIN){
            // round robin
            reviewsIndex = (reviewsIndex + 1) % ips.length
        } else {
            // service load
            let minLoad = Infinity;
            let minIp;
            for(i in ips){
                let newKey = CONCURRENT_REQUESTS_KEY + i;
                let concurrent = await redisClient.get(newKey);
                concurrent = concurrent ? parseInt(concurrent, 10) : 0;
                console.log(`CONCURRENT: ${concurrent} MIN LOAD ${minLoad}`)
                if (concurrent < minLoad){
                    minLoad = concurrent;
                    minIp = i;
                }
            }
            usersIndex = minIp;
            // console.log(`MIN IP ${minIp}`)
            // end service load
        }

        ip = ips[reviewsIndex];

        await limitTasks(ip);
        await writeCurrentLoad(ip)
        
        const serviceUrl = `http://${ip}:${SERV_REST_PORT}/${req.url.slice(1)}`
        const response = await axios({
            method: req.method,
            url: serviceUrl,
            data: req.body,
            headers: req.headers,
            timeout: SERVER_TIMEOUT_MS,
        });

        res.status(response.status).send(response.data);

    } catch (error) {
        if (error.code === 'ECONNABORTED') {
            await circuitBreak(ip, 'review');
            res.status(504).json({ detail: "Request timed out." });
        } else if (error.message === `TASK LIMITER LIMITED THE TASKS`) {
            res.status(503).json({detail: error.message})
        }
        
        else {
            // Extract details from the error response if it exists
            const errorResponse = error.response?.data || { detail: error.message };

            // Forward the status code and error details from the service
            res.status(error.response?.status || 500).json(errorResponse);
        }
    } finally{
        if (ip){
            await redisClient.decr(CONCURRENT_REQUESTS_KEY+ip);
        }
    }
});

app.listen(PORT, () => {
    console.log(`API Gateway listening at http://127.0.0.1:${PORT}`);
});