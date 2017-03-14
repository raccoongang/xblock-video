/** Run a callback when DOM is fully loaded */
function domReady(callback) {
    if (document.readyState === 'interactive' || document.readyState === 'complete') {
        callback();
    } else {
        document.addEventListener('DOMContentLoaded', callback);
    }
}

export { domReady as default };
