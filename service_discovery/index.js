const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const redis = require('redis');

// Load environment variables
require('dotenv').config();

const PORT = process.env.PORT;
const SERVICE_METADATA_URL = process.env.SERVICE_METADATA_URL;

// Connect to Redis
const redisClient = redis.createClient({ url: SERVICE_METADATA_URL });
redisClient.connect();

// Load protobuf
const PROTO_PATH_DISCOVERY = './service_discovery.proto';
const PROTO_PATH_STATUS = './status.proto';
const packageDefinitionDiscovery = protoLoader.loadSync(PROTO_PATH_DISCOVERY, {});
const packageDefinitionStatus = protoLoader.loadSync(PROTO_PATH_STATUS, {});
const discoveryProto = grpc.loadPackageDefinition(packageDefinitionDiscovery).discovery;
const statusProto = grpc.loadPackageDefinition(packageDefinitionStatus).status;

// gRPC Server for service discovery
function registerService(call, callback) {
    console.log(call.request);
    const { serviceName, ipAddress} = call.request;
    const redisKey = `service:${serviceName}`;
    
    redisClient.lPush(redisKey, ipAddress)
        .then(() => {
            console.log(`Registered ${redisKey} at IP - ${ipAddress}`);
            callback(null, { success: true, detail: `Service ${serviceName} registered successfully.` });
        })
        .catch(err => {
            console.error('Redis error:', err);
            callback(null, { success: false, detail: 'Failed to register service.' });
        });
}

// gRPC status
function status(call, callback) {
    callback(null, {message: `Service Discovery running at http://0.0.0.0:${PORT} is alive!`})
}

// Create gRPC server
function startGrpcServer() {
    const server = new grpc.Server();
    
    server.addService(statusProto.Status.service, { Status: status });
    server.addService(discoveryProto.ServiceDiscovery.service, { RegisterService: registerService });
    
    server.bindAsync(`0.0.0.0:${PORT}`, grpc.ServerCredentials.createInsecure(), () => {
        console.log(`gRPC service discovery running at http://0.0.0.0:${PORT}`);
        server.start();
    });

    // Graceful Shutdown
    async function shutdown(signal) {
        console.log(`Received ${signal}. Shutting down gracefully...`);
        
        // Stop accepting new gRPC requests
        server.tryShutdown(async (err) => {
            if (err) {
                console.error('Error shutting down gRPC server:', err);
            } else {
                console.log('gRPC server stopped accepting new requests.');
            }
            
            // Close Redis connection
            try {
                await redisClient.quit();
                console.log('Redis client disconnected.');
            } catch (redisErr) {
                console.error('Error disconnecting Redis client:', redisErr);
            }

            // Exit process after graceful shutdown
            process.exit(0);
        });
    }

    // Listen for shutdown signals (e.g., SIGINT for Ctrl+C, SIGTERM for Docker stop)
    ['SIGINT', 'SIGTERM'].forEach(signal => process.on(signal, () => shutdown(signal)));
}

startGrpcServer();