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
// const SERVER_TIMEOUT_MS = process.env.SERV_TIMEOUT_MS;
const SERVER_TIMEOUT_MS = 9000;
const MAX_CONCURRENT_REQUESTS = process.env.MAX_CONCURRENT_REQUESTS;
const USER_SERVICE_URL = process.env.USER_SERVICE_URL;
const REVIEW_SERVICE_URL = process.env.REVIEW_SERVICE_URL;
const SERVICE_METADATA_URL = process.env.SERVICE_METADATA_URL; // Redis URL storing metadata
const ROUND_ROBIN = true;

// const FAIL_COUNT_KEY = "fail_count:"; // circuit breaker
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
    console.log(`CONCURRENT: ${concurrent} MAX: ${MAX_CONCURRENT_REQUESTS}`);

    if (concurrent >= MAX_CONCURRENT_REQUESTS){
        throw new Error(`TASK LIMITER LIMITED THE TASKS`);
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
    if (concurrent >= 60){
        console.log(`ALERT!!! ${ip} HAS TOO MANY TASKS PER MINUTE IM SCARED`);
    }
}

//circuit breaker
async function circuitBreak(requestData, ip, serviceType){
   let tries = 1;

   while (tries < 3){
    try{
        console.log(`circuit breaker tries ${tries}`);
        const response = await axios(requestData);
        if (response.code === 500){
            throw new Error("SERVICE ERROR");
        }
        return response;
    } catch(error){
        console.log(error.message);
        tries++;
    }
    
   }

   const redisKey = `service:${serviceType}`;
   await redisClient.lRem(redisKey, 0, ip); 
   return new Error(`CIRCUIT BROKE ON IP ${ip}`);

}

async function shutdown(signal) {
    console.log(`Received ${signal}. Closing Redis and HTTP server...`);
    await redisClient.quit();
    server.close(() => {
        console.log('Express server closed.');
        process.exit(0);
    });
}

async function serviceLoad(ips){
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
    // console.log(minIp);
    return minIp;
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
    let requestData;
    try {
       const ips = await getServiceIps('user');
        console.log(ips);
        if (ips.length === 0){
            return res.status(503).json({detail: "No available services ^^"});
        }
        if (ROUND_ROBIN){
             // round robin
            usersIndex = (usersIndex + 1) % ips.length;
        } else {
            // service load
            usersIndex = await serviceLoad(ips);
            // console.log(`MIN IP ${minIp}`)
            // end service load
        }
       
        ip = ips[usersIndex];

        await limitTasks(ip);
        await writeCurrentLoad(ip);
        
        const serviceUrl = `http://${ip}:${SERV_REST_PORT}/${req.url.slice(1)}`;
        requestData = {
            method: req.method,
            url: serviceUrl,
            data: req.body,
            headers: req.headers,
            timeout: SERVER_TIMEOUT_MS,
        }
        const response = await axios(requestData);

        res.status(response.status).send(response.data);

    }  catch (error) {
        if (error.message === `TASK LIMITER LIMITED THE TASKS`){
            res.status(503).json({detail: error.message})
        } else{
            response = await circuitBreak(requestData, ip, 'user');
            if (response instanceof Error){
                res.status(503).json({detail: response.message})
            } else {
                res.status(response.status).send(response.data)
            }
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
    let requestData;
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
            reviewsIndex = serviceLoad(ips);
            // console.log(`MIN IP ${minIp}`)
            // end service load
        }

        ip = ips[reviewsIndex];

        await limitTasks(ip);
        await writeCurrentLoad(ip)
        
        const serviceUrl = `http://${ip}:${SERV_REST_PORT}/${req.url.slice(1)}`;
        requestData = {
            method: req.method,
            url: serviceUrl,
            data: req.body,
            headers: req.headers,
            timeout: SERVER_TIMEOUT_MS,
        }
        const response = await axios();

        res.status(response.status).send(response.data);

    } catch (error) {
        if (error.message === `TASK LIMITER LIMITED THE TASKS`){
            res.status(503).json({detail: error.message})
        } else{
            response = await circuitBreak(requestData, ip, 'review');
            if (response instanceof Error){
                res.status(503).json({detail: error.message})
            } else {
                res.status(response.status).send(response.data)
            }
                
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