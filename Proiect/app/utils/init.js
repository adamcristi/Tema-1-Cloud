module.exports = function() {

    global.LOG = function (string) {
        console.log(string);
    };

    global.DEBUG = function (string) {
        console.log(string);
    };

    process.on('SIGTERM', () => {
        LOG("\nClosing server...");
        process.exit(0);
    });

    process.on('SIGINT', () => {
        LOG("\nClosing server...");
        process.exit(0);
    });

};